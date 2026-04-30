"""UNESCO Readiness Assessment Methodology (RAM) source (Tier 3 — PDF extraction).

Data: https://www.unesco.org/ethics-ai/en/ram
Country reports published as PDFs. Uses pdfplumber for extraction.
Start with: Philippines, Chile, Senegal, Morocco, Brazil (best-formatted reports).
Feeds `indicators` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, fetch_text, make_client
from src.common.pdf import extract_text, extract_score_pattern

logger = logging.getLogger(__name__)

SOURCE_NAME = "unesco_ram"
BASE_URL = "https://www.unesco.org/ethics-ai/en/ram"
METHODOLOGY_URL = "https://www.unesco.org/ethics-ai/en/ram"

# Priority countries for initial parser development
PRIORITY_COUNTRIES = ["Philippines", "Chile", "Senegal", "Morocco", "Brazil"]

# UNESCO RAM 5 dimensions
DIMENSIONS = [
    ("readiness", "Readiness"),
    ("implementation", "Responsible AI Implementation"),
    ("monitoring", "Monitoring and Evaluation"),
    ("policy", "Legal and Policy Frameworks"),
    ("international", "International Cooperation"),
]

# Known country page URL pattern
COUNTRY_PAGE_TMPL = "https://www.unesco.org/ethics-ai/en/ram/{country_slug}"


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    # Fetch the main RAM page to discover country report links
    try:
        html = fetch_text(BASE_URL, SOURCE_NAME, client=client, refresh=refresh)
        (raw_dir / "ram_index.html").write_text(html)

        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        pdf_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if a["href"].endswith(".pdf") and "ram" in a["href"].lower()
        ]
        fetched = 0
        for link in pdf_links[:20]:  # Cap at 20 to avoid overwhelming
            url = link if link.startswith("http") else f"https://www.unesco.org{link}"
            try:
                fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
                fetched += 1
            except Exception as e:
                logger.debug("UNESCO RAM: PDF fetch failed %s: %s", url, e)
        logger.info("UNESCO RAM: fetched %d PDF reports", fetched)
    except Exception as e:
        logger.warning("UNESCO RAM: main page fetch failed: %s", e)

    return raw_dir


def _extract_scores_from_pdf(pdf_path: Path) -> dict[str, float]:
    """Extract the 5-dimension scores from a UNESCO RAM country report PDF."""
    scores: dict[str, float] = {}
    try:
        text = extract_text(pdf_path)
        for dim_id, dim_name in DIMENSIONS:
            score = extract_score_pattern(text, dim_name)
            if score is None:
                # Try abbreviated patterns
                score = extract_score_pattern(text, dim_id.capitalize())
            if score is not None:
                scores[dim_id] = score
    except Exception as e:
        logger.warning("UNESCO RAM: PDF extraction failed for %s: %s", pdf_path, e)
    return scores


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for pdf_path in raw_dir.glob("*.pdf"):
        # Infer country from filename
        country_raw = pdf_path.stem.replace("-", " ").replace("_", " ").title()
        # Strip common suffixes
        country_raw = re.sub(r"\s*(ram|report|assessment|readiness)\s*", " ", country_raw, flags=re.IGNORECASE).strip()
        iso3 = to_iso3(country_raw)
        if not iso3:
            logger.warning("UNESCO RAM: cannot map %r to iso3", country_raw)
            continue

        country_name = country_name_for_iso3(iso3) or country_raw
        year_m = re.search(r"20(\d{2})", pdf_path.name)
        year = int("20" + year_m.group(1)) if year_m else 2023

        scores = _extract_scores_from_pdf(pdf_path)
        if not scores:
            logger.debug("UNESCO RAM: no scores extracted from %s", pdf_path.name)
            continue

        for dim_id, score in scores.items():
            dim_name = next((n for d, n in DIMENSIONS if d == dim_id), dim_id)
            rows.append({
                "country_iso3": iso3,
                "country_name": country_name,
                "year": year,
                "indicator_id": f"unesco_ram.{dim_id}",
                "indicator_name": f"UNESCO RAM — {dim_name}",
                "value": score,
                "unit": "score_0_100",
                "source": SOURCE_NAME,
                "methodology_url": METHODOLOGY_URL,
                "retrieved_at": retrieved_at,
            })

    if not rows:
        logger.warning("UNESCO RAM: no data extracted — place country PDFs in %s", raw_dir)
        return {"indicators": pl.DataFrame()}

    return {"indicators": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("indicators")
    if df is None or df.is_empty():
        return ["indicators empty — UNESCO RAM PDFs may not be downloaded yet"]
    return []
