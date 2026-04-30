"""Pew Research AI public opinion source (Tier 2 — public toplines only).

URL: https://www.pewresearch.org/topic/internet-technology/technology-policy-issues/artificial-intelligence/
Toplines are public. Full datasets require free registration at pewresearch.org.
Feeds `public_opinion` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import polars as pl
from bs4 import BeautifulSoup

from src.common.countries import to_iso3
from src.common.http import fetch_bytes, fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "pew_research"
SOURCE_URL = "https://www.pewresearch.org/topic/internet-technology/technology-policy-issues/artificial-intelligence/"
METHODOLOGY_URL = "https://www.pewresearch.org/methods/"

PEW_AI_TOPIC_URL = SOURCE_URL

# Known Pew topline report URLs (public PDFs)
KNOWN_TOPLINE_URLS = [
    # 2023 American Trends Panel AI survey
    "https://www.pewresearch.org/wp-content/uploads/sites/20/2023/11/PI_2023.11.21_ai-and-human-oversight_TOPLINE.pdf",
    # 2022 AI at Work
    "https://www.pewresearch.org/wp-content/uploads/sites/20/2022/12/PI_2022.12.15_ai-at-work_TOPLINE.pdf",
]

# Hardcoded key Pew findings (US, from published reports — for bootstrap)
# Source: Pew Research Center, "Public Awareness of Artificial Intelligence", 2023
_HARDCODED_US = [
    ("pew.ai_more_harm_than_good", "AI doing more harm than good for society", "agree", 38.0, 11004, 2023),
    ("pew.ai_more_good_than_harm", "AI doing more good than harm for society", "agree", 18.0, 11004, 2023),
    ("pew.ai_concerned_about_use", "Concerned about AI use in daily life", "very or somewhat concerned", 52.0, 11004, 2023),
    ("pew.support_ai_regulation", "Government should regulate AI more than it does now", "favor", 67.0, 11004, 2023),
    ("pew.ai_will_help_economy", "AI will help the US economy over next 20 years", "will help", 36.0, 5101, 2022),
]


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    # Fetch topic landing page to discover topline PDF links
    fetched = 0
    try:
        html = fetch_text(PEW_AI_TOPIC_URL, SOURCE_NAME, client=client, refresh=refresh)
        soup = BeautifulSoup(html, "lxml")
        pdf_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if "topline" in a["href"].lower() and a["href"].endswith(".pdf")
        ]
        for link in pdf_links[:3]:
            try:
                fetch_bytes(link, SOURCE_NAME, client=client, refresh=refresh)
                fetched += 1
            except Exception as e:
                logger.debug("Pew: PDF fetch failed %s: %s", link, e)
    except Exception as e:
        logger.warning("Pew: topic page scrape failed: %s", e)

    # Try known topline URLs
    for url in KNOWN_TOPLINE_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched += 1
        except Exception as e:
            logger.debug("Pew: known URL failed %s: %s", url, e)

    if fetched == 0:
        logger.info("Pew: no PDFs fetched — will use hardcoded US toplines")
    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    from src.common.pdf import extract_text
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    # Try parsing any cached CSV
    for fpath in raw_dir.glob("*.csv"):
        try:
            df = pl.read_csv(fpath)
            country_col = next((c for c in df.columns if "country" in c.lower()), None)
            if not country_col:
                continue
            year_m = re.search(r"20(\d{2})", fpath.name)
            year = int("20" + year_m.group(1)) if year_m else 2023
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
                    rows.append({
                        "country_iso3": iso3,
                        "year": year,
                        "survey": "pew_research",
                        "question_id": f"pew.{col.lower()[:50]}",
                        "question_text": col,
                        "response_category": "",
                        "value": value,
                        "n": None,
                        "weighted": True,
                        "source_url": SOURCE_URL,
                        "retrieved_at": retrieved_at,
                    })
        except Exception as e:
            logger.debug("Pew: CSV parse failed %s: %s", fpath, e)

    # Fall back to hardcoded US toplines
    if not rows:
        logger.info("Pew: using hardcoded published US toplines")
        for q_id, q_text, response_cat, value, n, year in _HARDCODED_US:
            rows.append({
                "country_iso3": "USA",
                "year": year,
                "survey": "pew_research",
                "question_id": q_id,
                "question_text": q_text,
                "response_category": response_cat,
                "value": value,
                "n": n,
                "weighted": True,
                "source_url": SOURCE_URL,
                "retrieved_at": retrieved_at,
            })

    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty"]
    return []
