"""Ipsos AI Monitor source (Tier 3 — public topline PDF extraction).

Free topline PDFs: https://www.ipsos.com/en/ai-monitor
Microdata requires commercial license (Tier 4 — not fetched here).
Feeds `public_opinion` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3
from src.common.http import fetch_bytes, fetch_text, make_client
from src.common.pdf import extract_text

logger = logging.getLogger(__name__)

SOURCE_NAME = "ipsos_ai_monitor"
SOURCE_URL = "https://www.ipsos.com/en/ai-monitor"
METHODOLOGY_URL = "https://www.ipsos.com/en/ai-monitor"

KNOWN_TOPLINE_URLS = [
    "https://www.ipsos.com/sites/default/files/ct/news/documents/2024-01/Ipsos-AI-Monitor-2024-Report.pdf",
    "https://www.ipsos.com/sites/default/files/ct/news/documents/2023-07/Ipsos-AI-Monitor-2023.pdf",
]

# Countries included in Ipsos AI Monitor (typically 28 countries)
IPSOS_COUNTRIES = [
    "Argentina", "Australia", "Belgium", "Brazil", "Canada", "Chile",
    "China", "Colombia", "France", "Germany", "Hungary", "India",
    "Indonesia", "Italy", "Japan", "Malaysia", "Mexico", "Netherlands",
    "Peru", "Poland", "Saudi Arabia", "South Africa", "South Korea",
    "Spain", "Sweden", "Turkey", "United Kingdom", "United States",
]


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    fetched = 0
    # Try to find topline PDF links from the Ipsos page
    try:
        html = fetch_text(SOURCE_URL, SOURCE_NAME, client=client, refresh=refresh)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        pdf_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if "ai" in a["href"].lower() and a["href"].endswith(".pdf")
        ]
        for link in pdf_links[:3]:
            try:
                fetch_bytes(link, SOURCE_NAME, client=client, refresh=refresh)
                fetched += 1
            except Exception as e:
                logger.debug("Ipsos: PDF fetch failed %s: %s", link, e)
    except Exception as e:
        logger.debug("Ipsos: page scrape failed: %s", e)

    for url in KNOWN_TOPLINE_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched += 1
        except Exception as e:
            logger.debug("Ipsos: known URL failed %s: %s", url, e)

    if fetched == 0:
        logger.warning("Ipsos AI Monitor: no topline PDFs fetched")
    return raw_dir


def _parse_topline_pdf(pdf_path: Path, retrieved_at: str) -> list[dict]:
    """Extract country-level percentages from an Ipsos topline PDF."""
    rows: list[dict] = []
    try:
        text = extract_text(pdf_path)
    except Exception as e:
        logger.warning("Ipsos: PDF extraction failed %s: %s", pdf_path.name, e)
        return rows

    year_m = re.search(r"20(\d{2})", pdf_path.name)
    year = int("20" + year_m.group(1)) if year_m else 2024

    # Look for patterns like "Country  XX%" near question blocks
    pct_pattern = re.compile(
        r"([A-Z][A-Za-z ]+?)\s{2,}(\d{1,3})%",
        re.MULTILINE,
    )
    question_blocks = re.split(r"Q\d+[.:]|Question \d+", text)

    for qi, block in enumerate(question_blocks[1:], 1):
        question_text = block[:200].strip().replace("\n", " ")
        question_id = f"ipsos_q{qi}"
        for m in pct_pattern.finditer(block[:2000]):
            country_raw = m.group(1).strip()
            iso3 = to_iso3(country_raw)
            if not iso3:
                continue
            rows.append({
                "country_iso3": iso3,
                "year": year,
                "survey": "ipsos_ai_monitor",
                "question_id": f"ipsos.{pdf_path.stem}.{question_id}",
                "question_text": question_text,
                "response_category": "agree/positive",
                "value": float(m.group(2)),
                "n": None,
                "weighted": True,
                "source_url": SOURCE_URL,
                "retrieved_at": retrieved_at,
            })
    return rows


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for pdf_path in raw_dir.glob("*.pdf"):
        rows.extend(_parse_topline_pdf(pdf_path, retrieved_at))

    if not rows:
        logger.warning("Ipsos AI Monitor: no data parsed — topline PDFs may not be cached")
        return {"public_opinion": pl.DataFrame()}

    return {"public_opinion": pl.DataFrame(rows).unique(
        subset=["country_iso3", "year", "question_id", "response_category"]
    )}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty — Ipsos topline PDFs needed"]
    return []
