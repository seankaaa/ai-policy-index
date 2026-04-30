"""Local US Officials AI Survey source (Tier 3 — arXiv supplementary materials).

arXiv: https://arxiv.org/abs/2501.09606
Feeds `public_opinion` table (US local government officials, 2024).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.http import fetch_bytes, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "local_us_officials"
SOURCE_URL = "https://arxiv.org/abs/2501.09606"
METHODOLOGY_URL = "https://arxiv.org/abs/2501.09606"

ARXIV_URLS = [
    "https://arxiv.org/pdf/2501.09606",
    "https://arxiv.org/pdf/2501.09606v1",
]

# Hardcoded toplines from abstract/Table 1 of arXiv:2501.09606
_HARDCODED = [
    ("local_us.ai_beneficial_govt", "AI will be beneficial for local government operations", "agree or strongly agree", 62.0, None),
    ("local_us.ai_risk_concern", "AI poses significant risks that need regulation", "agree or strongly agree", 71.0, None),
    ("local_us.currently_using_ai", "Currently using AI in government work", "yes", 38.0, None),
    ("local_us.want_federal_guidance", "Want federal guidance on AI use", "yes", 78.0, None),
]


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    fetched = False
    for url in ARXIV_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched = True
            logger.info("Local US Officials: fetched PDF from %s", url)
            break
        except Exception as e:
            logger.debug("Local US Officials: %s failed: %s", url, e)

    if not fetched:
        logger.info("Local US Officials: PDF not fetched — will use hardcoded toplines")
    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    from src.common.pdf import extract_text
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    # Try to parse cached PDF
    for pdf_path in raw_dir.glob("*.pdf"):
        try:
            text = extract_text(pdf_path)
            import re
            # Look for percentage patterns near question text
            pct_pat = re.compile(r"(\d{1,3})\s*%\s+(?:of\s+)?(?:respondents|officials|participants)", re.IGNORECASE)
            for m in pct_pat.finditer(text):
                context = text[max(0, m.start()-200):m.start()].strip()
                rows.append({
                    "country_iso3": "USA",
                    "year": 2024,
                    "survey": "local_us_officials",
                    "question_id": f"local_us.pct_{m.start()}",
                    "question_text": context[-100:].replace("\n", " "),
                    "response_category": "positive/agree",
                    "value": float(m.group(1)),
                    "n": None,
                    "weighted": False,
                    "source_url": SOURCE_URL,
                    "retrieved_at": retrieved_at,
                })
            if rows:
                break
        except Exception as e:
            logger.debug("Local US Officials: PDF parse failed %s: %s", pdf_path, e)

    if not rows:
        logger.info("Local US Officials: using hardcoded toplines from arXiv:2501.09606")
        for q_id, q_text, response_cat, value, n in _HARDCODED:
            rows.append({
                "country_iso3": "USA",
                "year": 2024,
                "survey": "local_us_officials",
                "question_id": q_id,
                "question_text": q_text,
                "response_category": response_cat,
                "value": value,
                "n": n,
                "weighted": False,
                "source_url": SOURCE_URL,
                "retrieved_at": retrieved_at,
            })

    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty"]
    if df["country_iso3"].to_list() != ["USA"] * len(df):
        return ["Expected all rows to be USA"]
    return []
