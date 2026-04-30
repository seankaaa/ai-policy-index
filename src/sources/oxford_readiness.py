"""Oxford Insights Government AI Readiness Index source.

Fetches the annual Excel/CSV data files from Oxford Insights' public downloads.
Produces an `indicators` table with one row per (country, year, indicator).

Oxford Insights publishes annual reports. Each edition covers ~193 countries
across three pillars: Government, Technology Sector, Data & Infrastructure.

Data download page: https://oxfordinsights.com/ai-readiness/ai-readiness-index/
"""

from __future__ import annotations

import io
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
import polars as pl
from bs4 import BeautifulSoup

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "oxford_readiness"
METHODOLOGY_URL = "https://oxfordinsights.com/ai-readiness/ai-readiness-index/"

# Oxford Insights data download page URL
DATA_PAGE_URL = "https://oxfordinsights.com/ai-readiness/ai-readiness-index/"

# Known direct download URLs for recent editions (updated as new editions are published).
# The scraper tries to discover newer URLs from the page, falling back to these.
KNOWN_DATA_URLS: list[dict[str, Any]] = [
    {
        "year": 2023,
        "url": "https://oxfordinsights.com/wp-content/uploads/2023/10/Oxford-Insights-AI-Readiness-Index-2023.xlsx",
    },
    {
        "year": 2022,
        "url": "https://oxfordinsights.com/wp-content/uploads/2022/09/Oxford-Insights-Government-AI-Readiness-Index-2022.xlsx",
    },
    {
        "year": 2021,
        "url": "https://oxfordinsights.com/wp-content/uploads/2021/09/2021-GARI-Data.xlsx",
    },
    {
        "year": 2020,
        "url": "https://oxfordinsights.com/wp-content/uploads/2020/11/GARI_2020_Data.xlsx",
    },
    {
        "year": 2019,
        "url": "https://oxfordinsights.com/wp-content/uploads/2019/09/GARI_2019_DATA.xlsx",
    },
]

# Indicator definitions: (column_fragment, indicator_id_suffix, human_name, unit)
# These are matched against actual column names using substring search (case-insensitive).
INDICATOR_DEFS: list[tuple[str, str, str, str]] = [
    ("overall", "overall", "Overall Score", "score_0_100"),
    ("government", "government_pillar", "Government Pillar Score", "score_0_100"),
    ("technology sector", "technology_sector_pillar", "Technology Sector Pillar Score", "score_0_100"),
    ("data & infrastructure", "data_infrastructure_pillar", "Data & Infrastructure Pillar Score", "score_0_100"),
    ("data and infrastructure", "data_infrastructure_pillar", "Data & Infrastructure Pillar Score", "score_0_100"),
    ("rank", "rank", "Overall Rank", "rank"),
]


def _discover_data_urls(client: httpx.Client, refresh: bool) -> list[dict[str, Any]]:
    """Scrape the Oxford Insights page to discover xlsx download links."""
    try:
        html = fetch_text(DATA_PAGE_URL, SOURCE_NAME, client=client, refresh=refresh)
    except Exception as e:
        logger.warning("Could not fetch Oxford Insights page: %s — using known URLs", e)
        return []

    soup = BeautifulSoup(html, "lxml")
    discovered = []
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if not href.lower().endswith((".xlsx", ".xls", ".csv")):
            continue
        if "readiness" not in href.lower() and "gari" not in href.lower():
            continue

        year_match = re.search(r"20(\d{2})", href)
        year = int("20" + year_match.group(1)) if year_match else None
        if year and 2015 <= year <= 2030:
            discovered.append({"year": year, "url": href})
            logger.info("Discovered Oxford data URL: %s (year=%s)", href, year)

    return discovered


def _merge_url_lists(discovered: list[dict], known: list[dict]) -> list[dict]:
    """Merge discovered URLs with known fallbacks, deduplicating by year (prefer discovered)."""
    by_year: dict[int, dict] = {}
    for entry in known:
        by_year[entry["year"]] = entry
    for entry in discovered:
        if entry["year"]:
            by_year[entry["year"]] = entry
    return sorted(by_year.values(), key=lambda x: x["year"], reverse=True)


def _col_match(col: str, fragment: str) -> bool:
    return fragment.lower() in col.lower()


# CSV column name -> (indicator_id_suffix, human_name, unit)
# These are the exact column names produced by our PDF extraction script.
_CSV_COL_MAP: dict[str, tuple[str, str, str]] = {
    "overall": ("overall", "Overall Score", "score_0_100"),
    "government_pillar": ("government_pillar", "Government Pillar Score", "score_0_100"),
    "technology_sector_pillar": ("technology_sector_pillar", "Technology Sector Pillar Score", "score_0_100"),
    "data_infrastructure_pillar": ("data_infrastructure_pillar", "Data & Infrastructure Pillar Score", "score_0_100"),
    "rank": ("rank", "Overall Rank", "rank"),
}


def _parse_csv(csv_bytes: bytes, year: int, retrieved_at: datetime) -> pl.DataFrame:
    """Parse a pre-extracted CSV (from PDF text) into a normalized indicators DataFrame."""
    try:
        df_raw = pl.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        logger.error("Failed to parse CSV for year %d: %s", year, e)
        return pl.DataFrame()

    if df_raw.is_empty():
        return pl.DataFrame()

    logger.debug("CSV columns for year %d: %s", year, df_raw.columns)

    # Determine country column
    country_col = None
    for col in df_raw.columns:
        if any(x in col.lower() for x in ("country", "nation", "economy")):
            country_col = col
            break
    if country_col is None:
        country_col = df_raw.columns[0]

    rows: list[dict[str, Any]] = []
    retrieved_str = retrieved_at.isoformat()

    for raw_row in df_raw.to_dicts():
        raw_country = str(raw_row.get(country_col) or "").strip()
        if not raw_country or raw_country.lower() in ("country", "nan", "none", ""):
            continue

        iso3 = to_iso3(raw_country)
        if iso3 is None:
            continue

        country_name = country_name_for_iso3(iso3) or raw_country

        for col, (ind_id, ind_name, unit) in _CSV_COL_MAP.items():
            if col not in df_raw.columns:
                continue
            raw_val = raw_row.get(col)
            if raw_val is None or str(raw_val).strip() in ("", "nan", "None", "-", "N/A"):
                continue
            try:
                value = float(raw_val)
            except (TypeError, ValueError):
                continue

            rows.append({
                "country_iso3": iso3,
                "country_name": country_name,
                "year": year,
                "indicator_id": f"oxford_readiness.{ind_id}",
                "indicator_name": ind_name,
                "value": value,
                "unit": unit,
                "source": SOURCE_NAME,
                "methodology_url": METHODOLOGY_URL,
                "retrieved_at": retrieved_str,
            })

    if not rows:
        logger.warning("No rows parsed from CSV for year %d", year)
        return pl.DataFrame()

    return pl.DataFrame(rows)


def _parse_excel(raw_bytes: bytes, year: int, retrieved_at: datetime) -> pl.DataFrame:
    """Parse an Oxford Insights xlsx file into a normalized indicators DataFrame."""
    try:
        import openpyxl  # noqa: F401
    except ImportError as e:
        raise RuntimeError("openpyxl is required to read xlsx files") from e

    # Try reading with polars directly (uses xlsx2csv under the hood in some versions)
    # Fall back to pandas-style openpyxl if needed.
    try:
        df_raw = pl.read_excel(io.BytesIO(raw_bytes))
    except Exception:
        try:
            import openpyxl
            wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), data_only=True)
            ws = wb.active
            data = list(ws.values)
            if not data:
                return pl.DataFrame()
            headers = [str(h or "").strip() for h in data[0]]
            rows = [
                {headers[i]: cell for i, cell in enumerate(row) if i < len(headers)}
                for row in data[1:]
            ]
            df_raw = pl.DataFrame(rows)
        except Exception as e:
            logger.error("Failed to parse Excel for year %d: %s", year, e)
            return pl.DataFrame()

    if df_raw.is_empty():
        return pl.DataFrame()

    logger.debug("Raw columns for year %d: %s", year, df_raw.columns)

    # Find country column
    country_col = None
    for col in df_raw.columns:
        if any(x in col.lower() for x in ("country", "nation", "economy")):
            country_col = col
            break
    if country_col is None:
        # Assume first column is country
        country_col = df_raw.columns[0]
    logger.debug("Country column: %r", country_col)

    rows: list[dict[str, Any]] = []
    retrieved_str = retrieved_at.isoformat()

    for raw_row in df_raw.to_dicts():
        raw_country = str(raw_row.get(country_col) or "").strip()
        if not raw_country or raw_country.lower() in ("country", "nation", "nan", "none", ""):
            continue

        iso3 = to_iso3(raw_country)
        if iso3 is None:
            continue  # already logged by to_iso3

        country_name = country_name_for_iso3(iso3) or raw_country

        # Map each recognized column to an indicator row
        seen_indicator_ids: set[str] = set()
        for col in df_raw.columns:
            matched_def = None
            for fragment, ind_id, ind_name, unit in INDICATOR_DEFS:
                if _col_match(col, fragment) and ind_id not in seen_indicator_ids:
                    matched_def = (ind_id, ind_name, unit)
                    break
            if matched_def is None:
                continue

            ind_id, ind_name, unit = matched_def
            raw_val = raw_row.get(col)
            if raw_val is None or str(raw_val).strip() in ("", "nan", "None", "-", "N/A"):
                continue
            try:
                value = float(raw_val)
            except (TypeError, ValueError):
                logger.debug("Non-numeric value for %s/%s: %r", iso3, col, raw_val)
                continue

            seen_indicator_ids.add(ind_id)
            rows.append(
                {
                    "country_iso3": iso3,
                    "country_name": country_name,
                    "year": year,
                    "indicator_id": f"oxford_readiness.{ind_id}",
                    "indicator_name": ind_name,
                    "value": value,
                    "unit": unit,
                    "source": SOURCE_NAME,
                    "methodology_url": METHODOLOGY_URL,
                    "retrieved_at": retrieved_str,
                }
            )

    if not rows:
        logger.warning("No rows parsed for year %d", year)
        return pl.DataFrame()

    return pl.DataFrame(rows)


# --------------------------------------------------------------------------- #
# Public module contract                                                        #
# --------------------------------------------------------------------------- #


def fetch(refresh: bool = False) -> Path:
    """Download raw xlsx files to data/raw/oxford_readiness/. Returns dir path."""
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)

    client = make_client()
    discovered = _discover_data_urls(client, refresh=refresh)
    all_urls = _merge_url_lists(discovered, KNOWN_DATA_URLS)

    if not all_urls:
        logger.error("No Oxford Readiness data URLs found")
        return raw_dir

    fetched_count = 0
    for entry in all_urls:
        url = entry["url"]
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched_count += 1
        except PermissionError as e:
            logger.warning("robots.txt blocked %s: %s", url, e)
        except Exception as e:
            logger.warning("Failed to fetch %s: %s", url, e)

    logger.info("Oxford Readiness: fetched %d/%d files", fetched_count, len(all_urls))
    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Parse raw xlsx files -> {'indicators': pl.DataFrame}."""
    retrieved_at = datetime.now(timezone.utc)
    all_frames: list[pl.DataFrame] = []

    # Find all xlsx/csv files in raw_dir
    excel_files = sorted(raw_dir.glob("*.xlsx")) + sorted(raw_dir.glob("*.xls")) + sorted(raw_dir.glob("*.csv"))

    if not excel_files:
        logger.warning("No data files found in %s", raw_dir)
        return {"indicators": pl.DataFrame()}

    # Map files to years via filename patterns
    for fpath in excel_files:
        year_match = re.search(r"20(\d{2})", fpath.name)
        if year_match:
            year = int("20" + year_match.group(1))
        else:
            # Try to match via known URL list
            fname_hash = fpath.stem[:8]
            matched_year = None
            for entry in KNOWN_DATA_URLS:
                url_hash = entry["url"].split("/")[-1][:8]
                if fname_hash == url_hash:
                    matched_year = entry["year"]
                    break
            year = matched_year or 2023  # fallback

        if not (2015 <= year <= 2030):
            logger.warning("Skipping file with implausible year %d: %s", year, fpath)
            continue

        logger.info("Parsing %s (year=%d)", fpath.name, year)
        raw_bytes = fpath.read_bytes()
        if fpath.suffix.lower() == ".csv":
            df = _parse_csv(raw_bytes, year, retrieved_at)
        else:
            df = _parse_excel(raw_bytes, year, retrieved_at)
        if not df.is_empty():
            all_frames.append(df)

    if not all_frames:
        return {"indicators": pl.DataFrame()}

    combined = pl.concat(all_frames, how="diagonal")
    # Drop duplicates: same country/year/indicator from multiple files
    combined = combined.unique(subset=["country_iso3", "year", "indicator_id"])
    logger.info("Oxford Readiness: %d indicator rows across %d editions", len(combined), len(all_frames))
    return {"indicators": combined}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    """Sanity checks on normalized tables. Returns list of failure messages."""
    failures: list[str] = []
    df = tables.get("indicators")

    if df is None or df.is_empty():
        failures.append("indicators table is empty or missing")
        return failures

    # No nulls in required columns
    for col in ("country_iso3", "year", "value", "indicator_id"):
        if col not in df.columns:
            failures.append(f"Missing required column: {col}")
            continue
        null_count = df[col].null_count()
        if null_count > 0:
            failures.append(f"Column '{col}' has {null_count} null values")

    # All country_iso3 values are valid 3-letter codes
    if "country_iso3" in df.columns:
        bad_iso = df.filter(pl.col("country_iso3").str.len_chars() != 3)
        if len(bad_iso) > 0:
            failures.append(f"{len(bad_iso)} rows have country_iso3 != 3 chars")

    # year in plausible range
    if "year" in df.columns:
        out_of_range = df.filter((pl.col("year") < 2015) | (pl.col("year") > 2026))
        if len(out_of_range) > 0:
            failures.append(f"{len(out_of_range)} rows have year outside 2015–2026")

    # value in 0–100 for score indicators; rank indicators can exceed 100
    if "value" in df.columns and "unit" in df.columns:
        score_rows = df.filter(pl.col("unit") == "score_0_100")
        if not score_rows.is_empty():
            out_of_range = score_rows.filter((pl.col("value") < 0) | (pl.col("value") > 100))
            if len(out_of_range) > 0:
                failures.append(
                    f"{len(out_of_range)} score_0_100 rows have value outside [0, 100]"
                )

    # Expect at least 100 countries (Oxford covers ~195)
    if "country_iso3" in df.columns:
        n_countries = df["country_iso3"].n_unique()
        if n_countries < 50:
            failures.append(f"Only {n_countries} unique countries — expected 100+")

    # At least one year of data
    if "year" in df.columns:
        n_years = df["year"].n_unique()
        if n_years < 1:
            failures.append("No years in data")

    return failures
