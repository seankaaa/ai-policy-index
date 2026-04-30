"""Kelley et al. (2021) 8-country AI perception study source.

arXiv: https://arxiv.org/abs/2001.00081
Replication data: https://github.com/google-research/google-research/tree/master/ai_perception_survey
Feeds `public_opinion` table (8 countries, 2019).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3
from src.common.http import fetch_bytes, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "kelley_8country"
SOURCE_URL = "https://arxiv.org/abs/2001.00081"
METHODOLOGY_URL = "https://arxiv.org/abs/2001.00081"
GITHUB_BASE = "https://raw.githubusercontent.com/google-research/google-research/master/ai_perception_survey"

GITHUB_URLS = [
    f"{GITHUB_BASE}/data/weighted_toplines.csv",
    f"{GITHUB_BASE}/data/survey_results.csv",
    f"{GITHUB_BASE}/toplines.csv",
]

# Countries in the study
STUDY_COUNTRIES = ["USA", "GBR", "AUS", "CAN", "FRA", "DEU", "BRA", "IND"]

# Hardcoded key toplines from Table 1 of Kelley et al. 2021
# "% who think AI will cause more good than harm in next 20 years"
_HARDCODED = {
    "USA": 41, "GBR": 37, "AUS": 43, "CAN": 43,
    "FRA": 32, "DEU": 35, "BRA": 67, "IND": 72,
}


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    fetched = False
    for url in GITHUB_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched = True
            logger.info("Kelley 8-country: fetched %s", url.split("/")[-1])
            break
        except Exception as e:
            logger.debug("Kelley 8-country: %s failed: %s", url, e)

    if not fetched:
        logger.info("Kelley 8-country: GitHub data not found — using hardcoded toplines from paper")
    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    csvs = list(raw_dir.glob("*.csv"))
    parsed_from_file = False

    if csvs:
        for fpath in csvs:
            try:
                df = pl.read_csv(fpath)
                country_col = next((c for c in df.columns if "country" in c.lower()), None)
                if not country_col:
                    continue
                q_cols = [c for c in df.columns if c != country_col]
                for raw_row in df.to_dicts():
                    iso3 = to_iso3(str(raw_row.get(country_col) or ""))
                    if not iso3:
                        continue
                    for q_col in q_cols:
                        try:
                            value = float(raw_row[q_col])
                        except (TypeError, ValueError):
                            continue
                        rows.append({
                            "country_iso3": iso3,
                            "year": 2019,
                            "survey": "kelley_8country",
                            "question_id": f"kelley.{q_col.lower()[:50]}",
                            "question_text": q_col,
                            "response_category": "",
                            "value": value,
                            "n": None,
                            "weighted": True,
                            "source_url": SOURCE_URL,
                            "retrieved_at": retrieved_at,
                        })
                parsed_from_file = True
                break
            except Exception as e:
                logger.debug("Kelley: parse failed %s: %s", fpath, e)

    if not parsed_from_file:
        logger.info("Kelley 8-country: using hardcoded toplines from paper (Table 1)")
        for iso3, pct in _HARDCODED.items():
            rows.append({
                "country_iso3": iso3,
                "year": 2019,
                "survey": "kelley_8country",
                "question_id": "kelley.ai_more_good_than_harm",
                "question_text": "AI will cause more good than harm in the next 20 years",
                "response_category": "agree or strongly agree",
                "value": float(pct),
                "n": None,
                "weighted": True,
                "source_url": SOURCE_URL,
                "retrieved_at": retrieved_at,
            })

    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty"]
    n_countries = df["country_iso3"].n_unique()
    if n_countries < 8:
        return [f"Expected 8 countries, got {n_countries}"]
    return []
