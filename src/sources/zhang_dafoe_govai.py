"""Zhang & Dafoe (2019) 'Artificial Intelligence: American Attitudes and Trends' source.

Replication data: https://osf.io/gjxbp/ or Harvard Dataverse
Feeds `public_opinion` table (US-only survey, 2019).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3
from src.common.http import fetch_bytes, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "zhang_dafoe_govai"
SOURCE_URL = "https://osf.io/gjxbp/"
METHODOLOGY_URL = "https://governanceai.github.io/US-Public-Opinion-Report-Jan-2019/"

OSF_DOWNLOAD_URLS = [
    "https://osf.io/download/gjxbp/",
    "https://osf.io/gjxbp/download",
]

# Key topline findings (hard-coded from published report for US, 2019)
# Source: Zhang & Dafoe (2019) Table 1 and Section 3
_HARDCODED_TOPLINES = [
    ("zhang_dafoe.ai_regulated", "AI should be carefully managed by the government", "agree or strongly agree", 82.0),
    ("zhang_dafoe.ai_more_good", "AI will do more good than harm", "agree or somewhat agree", 41.0),
    ("zhang_dafoe.us_lead_ai", "US should ensure US leads world in AI development", "favor", 77.0),
    ("zhang_dafoe.international_cooperation", "Support international AI cooperation", "favor", 75.0),
]


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    fetched = False
    for url in OSF_DOWNLOAD_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched = True
            break
        except Exception as e:
            logger.debug("Zhang & Dafoe: %s failed: %s", url, e)

    if not fetched:
        logger.warning("Zhang & Dafoe: could not fetch replication data — writing hardcoded toplines")

    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    # Try replication CSV if available
    csvs = list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.xlsx"))
    parsed_from_file = False
    if csvs:
        for fpath in csvs:
            try:
                df = pl.read_csv(fpath) if fpath.suffix == ".csv" else pl.read_excel(fpath)
                logger.info("Zhang & Dafoe: parsing %s (%d rows)", fpath.name, len(df))
                # Microdata format: one row per respondent
                # For now emit aggregate means per question
                for col in df.columns:
                    try:
                        mean_val = df[col].cast(pl.Float64, strict=False).drop_nulls().mean()
                        if mean_val is not None:
                            rows.append({
                                "country_iso3": "USA",
                                "year": 2019,
                                "survey": "zhang_dafoe_govai",
                                "question_id": f"zhang_dafoe.{col.lower()[:50]}",
                                "question_text": col,
                                "response_category": "mean",
                                "value": float(mean_val),
                                "n": len(df),
                                "weighted": False,
                                "source_url": SOURCE_URL,
                                "retrieved_at": retrieved_at,
                            })
                    except Exception:
                        continue
                parsed_from_file = True
                break
            except Exception as e:
                logger.debug("Zhang & Dafoe: parse failed %s: %s", fpath, e)

    # Fall back to hardcoded published toplines
    if not parsed_from_file:
        logger.info("Zhang & Dafoe: using hardcoded published toplines (US, 2019)")
        for q_id, q_text, response_cat, value in _HARDCODED_TOPLINES:
            rows.append({
                "country_iso3": "USA",
                "year": 2019,
                "survey": "zhang_dafoe_govai",
                "question_id": q_id,
                "question_text": q_text,
                "response_category": response_cat,
                "value": value,
                "n": 2000,
                "weighted": True,
                "source_url": SOURCE_URL,
                "retrieved_at": retrieved_at,
            })

    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty"]
    if "USA" not in df["country_iso3"].to_list():
        return ["Expected USA in country_iso3"]
    return []
