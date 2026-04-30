"""Global Index on Responsible AI (GIRAI) source.

Data: https://www.global-index.ai/ — per-country scorecards, 138 countries.
Produces `indicators` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl
from bs4 import BeautifulSoup

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "girai"
BASE_URL = "https://www.global-index.ai"
DATA_URL = "https://www.global-index.ai/data"
METHODOLOGY_URL = "https://www.global-index.ai/methodology"

# GIRAI dimensions as defined in the index
DIMENSIONS = [
    "Governance",
    "Human Rights",
    "Socioeconomic Conditions",
    "Technology Infrastructure",
    "Research and Development",
]


def fetch(refresh: bool = False) -> Path:
    """Download raw GIRAI data to data/raw/girai/. Returns dir path."""
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)

    client = make_client()

    # Try CSV/Excel data download first
    data_attempts = [
        f"{BASE_URL}/data/download",
        f"{BASE_URL}/assets/data/girai-data.csv",
        f"{BASE_URL}/assets/data/girai-scores.xlsx",
        DATA_URL,
    ]
    fetched = False
    for url in data_attempts:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched = True
            logger.info("GIRAI data fetched from %s", url)
            break
        except Exception as e:
            logger.debug("GIRAI data attempt failed for %s: %s", url, e)

    if not fetched:
        # Fall back to scraping the main page + individual country pages
        try:
            html = fetch_text(BASE_URL, SOURCE_NAME, client=client, refresh=refresh)
            (raw_dir / "index.html").write_text(html)
            logger.info("GIRAI index page scraped")
        except Exception as e:
            logger.warning("GIRAI scrape failed: %s", e)
            (raw_dir / "FETCH_FAILED.txt").write_text(
                f"Failed at {datetime.now(timezone.utc).isoformat()}: {e}\n"
                "Visit https://www.global-index.ai to download data manually.\n"
            )

    return raw_dir


def _parse_html_table(html: str, retrieved_at: str) -> list[dict]:
    """Extract country scores from HTML table on GIRAI pages."""
    soup = BeautifulSoup(html, "lxml")
    rows = []

    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True) for th in table.find_all("th")]
        if not any("country" in h.lower() or "score" in h.lower() for h in headers):
            continue
        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) < 2:
                continue
            country_raw = cells[0]
            iso3 = to_iso3(country_raw)
            if not iso3:
                continue
            country_name = country_name_for_iso3(iso3) or country_raw
            for i, header in enumerate(headers[1:], 1):
                if i >= len(cells):
                    break
                try:
                    value = float(cells[i].replace(",", "."))
                except ValueError:
                    continue
                rows.append({
                    "country_iso3": iso3,
                    "country_name": country_name,
                    "year": 2024,
                    "indicator_id": f"girai.{header.lower().replace(' ', '_')}",
                    "indicator_name": header,
                    "value": value,
                    "unit": "score_0_100",
                    "source": SOURCE_NAME,
                    "methodology_url": METHODOLOGY_URL,
                    "retrieved_at": retrieved_at,
                })
    return rows


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Parse raw GIRAI files -> {'indicators': df}."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    # Try CSV/Excel
    for fpath in list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.xlsx")):
        try:
            if fpath.suffix == ".csv":
                df_raw = pl.read_csv(fpath)
            else:
                df_raw = pl.read_excel(fpath)

            country_col = next(
                (c for c in df_raw.columns if "country" in c.lower()), df_raw.columns[0]
            )
            for raw_row in df_raw.to_dicts():
                country_raw = str(raw_row.get(country_col) or "").strip()
                iso3 = to_iso3(country_raw)
                if not iso3:
                    continue
                country_name = country_name_for_iso3(iso3) or country_raw
                for col in df_raw.columns:
                    if col == country_col:
                        continue
                    try:
                        value = float(raw_row[col])
                    except (TypeError, ValueError):
                        continue
                    rows.append({
                        "country_iso3": iso3,
                        "country_name": country_name,
                        "year": 2024,
                        "indicator_id": f"girai.{col.lower().replace(' ', '_')}",
                        "indicator_name": col,
                        "value": value,
                        "unit": "score_0_100",
                        "source": SOURCE_NAME,
                        "methodology_url": METHODOLOGY_URL,
                        "retrieved_at": retrieved_at,
                    })
        except Exception as e:
            logger.warning("Failed to parse %s: %s", fpath, e)

    # Try HTML index page
    if not rows:
        index_html = raw_dir / "index.html"
        if index_html.exists():
            rows = _parse_html_table(index_html.read_text(), retrieved_at)

    if not rows:
        logger.warning("No GIRAI rows extracted — download data manually from %s", BASE_URL)
        return {"indicators": pl.DataFrame()}

    return {"indicators": pl.DataFrame(rows).unique(subset=["country_iso3", "year", "indicator_id"])}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    failures: list[str] = []
    df = tables.get("indicators")
    if df is None or df.is_empty():
        failures.append("indicators table is empty — GIRAI data may need manual download")
        return failures
    for col in ("country_iso3", "year", "value", "indicator_id"):
        if col not in df.columns:
            failures.append(f"Missing column: {col}")
        elif df[col].null_count() > 0:
            failures.append(f"'{col}' has {df[col].null_count()} nulls")
    if "country_iso3" in df.columns:
        n = df["country_iso3"].n_unique()
        if n < 50:
            failures.append(f"Only {n} countries — expected 100+ (GIRAI covers 138)")
    return failures
