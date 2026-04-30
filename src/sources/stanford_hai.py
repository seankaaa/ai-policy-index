"""Stanford HAI AI Index source.

Downloads the annual AI Index data files (xlsx/csv) from the Stanford HAI
public data repository. Feeds `indicators` and `public_opinion` tables.

Data: https://hai.stanford.edu/ai-index/
GitHub data repo: https://github.com/stanford-crfm/AIIndexReport (checked annually)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "stanford_hai"
METHODOLOGY_URL = "https://hai.stanford.edu/ai-index/"

# Known direct download URLs for Stanford HAI data annexes
# The AI Index publishes supplemental data CSVs on GitHub
GITHUB_DATA_BASE = "https://raw.githubusercontent.com/stanford-crfm/AIIndexReport/main"
KNOWN_DATA_URLS: list[dict[str, Any]] = [
    # 2024 report data (Chapter 9: Public Opinion)
    {
        "year": 2024,
        "table": "public_opinion",
        "url": f"{GITHUB_DATA_BASE}/2024/src/Chapter_9/",
    },
    {
        "year": 2023,
        "table": "public_opinion",
        "url": f"{GITHUB_DATA_BASE}/2023/src/Chapter_9/",
    },
]

# Ipsos topline questions tracked in the AI Index (public opinion)
IPSOS_QUESTIONS = {
    "q_beneficial": "AI products and services have more benefits than drawbacks",
    "q_nervous": "I am nervous about products and services that use AI",
    "q_regulations": "Companies developing AI products and services should be regulated",
    "q_excited": "AI products and services make me excited about the future",
}


def fetch(refresh: bool = False) -> Path:
    """Download raw Stanford HAI data files. Returns dir path."""
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    # Try GitHub data repo index
    github_urls = [
        "https://raw.githubusercontent.com/stanford-crfm/AIIndexReport/main/2024/src/Chapter_9/fig_9_1_13.csv",
        "https://raw.githubusercontent.com/stanford-crfm/AIIndexReport/main/2024/src/Chapter_9/fig_9_1_1.csv",
        "https://raw.githubusercontent.com/stanford-crfm/AIIndexReport/main/2023/src/Chapter_9/fig_9_1_1.csv",
    ]
    fetched = 0
    for url in github_urls:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched += 1
            logger.info("Stanford HAI: fetched %s", url.split("/")[-1])
        except Exception as e:
            logger.debug("Stanford HAI fetch failed for %s: %s", url, e)

    # Try the HAI website data page
    if fetched == 0:
        try:
            html = fetch_text("https://hai.stanford.edu/ai-index/", SOURCE_NAME, client=client, refresh=refresh)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            data_links = [
                a["href"] for a in soup.find_all("a", href=True)
                if any(ext in a["href"].lower() for ext in (".csv", ".xlsx", ".xls"))
            ]
            for link in data_links[:5]:
                url = link if link.startswith("http") else f"https://hai.stanford.edu{link}"
                try:
                    fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
                    fetched += 1
                except Exception as e:
                    logger.debug("Stanford HAI: failed %s: %s", url, e)
        except Exception as e:
            logger.warning("Stanford HAI website scrape failed: %s", e)

    if fetched == 0:
        logger.warning("Stanford HAI: no files fetched — data may have moved; check %s", METHODOLOGY_URL)
        (raw_dir / "FETCH_FAILED.txt").write_text(
            f"Failed at {datetime.now(timezone.utc).isoformat()}\n"
            "Download data manually from https://hai.stanford.edu/ai-index/\n"
            "or https://github.com/stanford-crfm/AIIndexReport\n"
        )
    return raw_dir


def _parse_ipsos_csv(fpath: Path, year: int, retrieved_at: str) -> list[dict]:
    """Parse a Stanford HAI Ipsos topline CSV into public_opinion rows."""
    rows: list[dict] = []
    try:
        df = pl.read_csv(fpath)
    except Exception as e:
        logger.warning("Failed to read %s: %s", fpath, e)
        return rows

    # Expect columns like: Country, Question, Response, Percentage, N, Year
    country_col = next((c for c in df.columns if "country" in c.lower()), None)
    question_col = next((c for c in df.columns if "question" in c.lower()), None)
    value_col = next((c for c in df.columns if any(x in c.lower() for x in ("pct", "percent", "value", "share"))), None)

    if not country_col or not value_col:
        logger.debug("Stanford HAI: unrecognized CSV format in %s: %s", fpath.name, df.columns)
        return rows

    for raw_row in df.to_dicts():
        country_raw = str(raw_row.get(country_col) or "").strip()
        iso3 = to_iso3(country_raw)
        if not iso3:
            continue
        try:
            value = float(raw_row[value_col])
        except (TypeError, ValueError):
            continue

        question_text = str(raw_row.get(question_col) or fpath.stem)
        question_id = re.sub(r"[^a-z0-9_]", "_", question_text.lower())[:50]

        rows.append({
            "country_iso3": iso3,
            "year": year,
            "survey": "ipsos_ai_monitor",
            "question_id": f"stanford_hai.{fpath.stem}.{question_id}",
            "question_text": question_text,
            "response_category": str(raw_row.get("response") or raw_row.get("category") or ""),
            "value": value,
            "n": raw_row.get("n") or raw_row.get("N"),
            "weighted": True,
            "source_url": METHODOLOGY_URL,
            "retrieved_at": retrieved_at,
        })
    return rows


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Parse Stanford HAI raw files -> {'indicators': df, 'public_opinion': df}."""
    retrieved_at = datetime.now(timezone.utc).isoformat()
    opinion_rows: list[dict] = []
    indicator_rows: list[dict] = []

    for fpath in sorted(raw_dir.glob("*.csv")):
        year_m = re.search(r"20(\d{2})", fpath.name)
        year = int("20" + year_m.group(1)) if year_m else 2024

        # Classify by filename
        fname_lower = fpath.name.lower()
        if any(x in fname_lower for x in ("opinion", "ipsos", "survey", "fig_9")):
            opinion_rows.extend(_parse_ipsos_csv(fpath, year, retrieved_at))
        else:
            # Try to parse as indicator data
            try:
                df = pl.read_csv(fpath)
                country_col = next((c for c in df.columns if "country" in c.lower()), None)
                if not country_col:
                    continue
                for raw_row in df.to_dicts():
                    iso3 = to_iso3(str(raw_row.get(country_col) or ""))
                    if not iso3:
                        continue
                    for col in df.columns:
                        if col == country_col:
                            continue
                        try:
                            value = float(raw_row[col])
                        except (TypeError, ValueError):
                            continue
                        indicator_rows.append({
                            "country_iso3": iso3,
                            "country_name": country_name_for_iso3(iso3) or str(raw_row[country_col]),
                            "year": year,
                            "indicator_id": f"stanford_hai.{col.lower().replace(' ','_')}",
                            "indicator_name": col,
                            "value": value,
                            "unit": "score_0_100",
                            "source": SOURCE_NAME,
                            "methodology_url": METHODOLOGY_URL,
                            "retrieved_at": retrieved_at,
                        })
            except Exception as e:
                logger.debug("Stanford HAI: failed to parse %s: %s", fpath, e)

    indicators_df = pl.DataFrame(indicator_rows) if indicator_rows else pl.DataFrame()
    opinion_df = pl.DataFrame(opinion_rows) if opinion_rows else pl.DataFrame()

    if indicators_df.is_empty() and opinion_df.is_empty():
        logger.warning("Stanford HAI: no data parsed — fetch may have failed")

    return {"indicators": indicators_df, "public_opinion": opinion_df}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    failures: list[str] = []
    for key in ("indicators", "public_opinion"):
        df = tables.get(key)
        if df is None or df.is_empty():
            failures.append(f"{key} table is empty (Stanford HAI fetch may have failed)")
    return failures
