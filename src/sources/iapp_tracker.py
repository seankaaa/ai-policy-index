"""IAPP Global AI Law and Policy Tracker source (Tier 2 — public table only).

URL: https://iapp.org/resources/article/global-ai-legislation-tracker/
Scrapes the public summary table only. Respects robots.txt.
Feeds `policies` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import polars as pl
from bs4 import BeautifulSoup

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "iapp_tracker"
SOURCE_URL = "https://iapp.org/resources/article/global-ai-legislation-tracker/"
METHODOLOGY_URL = "https://iapp.org/resources/article/global-ai-legislation-tracker/"

STATUS_MAP = {
    "enacted": "enacted",
    "passed": "enacted",
    "in force": "enforced",
    "effective": "enforced",
    "proposed": "proposed",
    "draft": "proposed",
    "under consideration": "proposed",
    "repealed": "superseded",
    "withdrawn": "superseded",
}

TYPE_MAP = {
    "comprehensive": "legislation",
    "law": "legislation",
    "act": "legislation",
    "regulation": "regulation",
    "strategy": "strategy",
    "guideline": "guideline",
    "principle": "principle",
    "framework": "guideline",
}


def _infer_type(text: str) -> str:
    lower = text.lower()
    for kw, val in TYPE_MAP.items():
        if kw in lower:
            return val
    return "other"


def _infer_status(text: str) -> str:
    lower = text.lower()
    for kw, val in STATUS_MAP.items():
        if kw in lower:
            return val
    return "enacted"


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    try:
        html = fetch_text(SOURCE_URL, SOURCE_NAME, client=client, refresh=refresh)
        (raw_dir / "tracker.html").write_text(html, encoding="utf-8")
        logger.info("IAPP tracker: page fetched (%d bytes)", len(html))
    except Exception as e:
        logger.warning("IAPP tracker: fetch failed: %s", e)
        (raw_dir / "FETCH_FAILED.txt").write_text(
            f"Failed at {datetime.now(timezone.utc).isoformat()}: {e}\n"
            "Public table may require JavaScript rendering.\n"
            f"Visit {SOURCE_URL} and save the page HTML manually.\n"
        )
    return raw_dir


def _parse_table(soup: BeautifulSoup, retrieved_at: str) -> list[dict]:
    rows: list[dict] = []
    for table in soup.find_all("table"):
        headers = [th.get_text(strip=True).lower() for th in table.find_all("th")]
        if not any("country" in h or "jurisdiction" in h for h in headers):
            continue
        country_idx = next((i for i, h in enumerate(headers) if "country" in h or "jurisdiction" in h), 0)
        name_idx = next((i for i, h in enumerate(headers) if "name" in h or "title" in h or "initiative" in h), 1)

        for tr in table.find_all("tr")[1:]:
            cells = [td.get_text(strip=True) for td in tr.find_all("td")]
            if len(cells) < 2:
                continue
            country_raw = cells[country_idx] if country_idx < len(cells) else ""
            iso3 = to_iso3(country_raw)
            if not iso3:
                continue
            policy_name = cells[name_idx] if name_idx < len(cells) else ""
            all_text = " ".join(cells)
            rows.append({
                "country_iso3": iso3,
                "country_name": country_name_for_iso3(iso3) or country_raw,
                "policy_id": f"iapp:{re.sub(r'[^a-z0-9]', '_', policy_name.lower())[:40]}",
                "policy_name": policy_name,
                "policy_type": _infer_type(all_text),
                "policy_status": _infer_status(all_text),
                "target_sector": None,
                "risk_focus": [],
                "enacted_date": None,
                "source_url": SOURCE_URL,
                "source": SOURCE_NAME,
                "raw_text": None,
                "retrieved_at": retrieved_at,
            })
    return rows


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    html_file = raw_dir / "tracker.html"
    if html_file.exists():
        soup = BeautifulSoup(html_file.read_text(encoding="utf-8"), "lxml")
        rows = _parse_table(soup, retrieved_at)
        logger.info("IAPP tracker: parsed %d rows from HTML", len(rows))

    if not rows:
        logger.warning("IAPP tracker: no rows parsed — page may use JavaScript rendering")
        return {"policies": pl.DataFrame()}

    return {"policies": pl.DataFrame(rows).unique(subset=["country_iso3", "policy_id"])}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("policies")
    if df is None or df.is_empty():
        return ["policies empty — IAPP tracker scrape may have failed (JS-rendered page)"]
    for col in ("country_iso3", "policy_name", "policy_type", "policy_status"):
        if col not in df.columns:
            return [f"Missing column: {col}"]
    return []
