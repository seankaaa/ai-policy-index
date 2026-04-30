"""OECD.AI Policy Navigator source.

Fetches AI policy records from the OECD.AI dashboard JSON API.
Endpoint discovered via browser network inspection of https://oecd.ai/en/dashboards

Produces:
  - `policies`   — one row per (country, initiative)
  - `indicators` — OECD country-level AI metrics where available
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import polars as pl

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "oecd_ai"
METHODOLOGY_URL = "https://oecd.ai/en/dashboards"
SOURCE_URL_BASE = "https://oecd.ai/en/policy-areas"

# OECD.AI public JSON endpoints (discovered from network tab of oecd.ai/en/dashboards)
INITIATIVES_API = "https://oecd.ai/api/en/data/initiatives"
COUNTRY_API_TMPL = "https://oecd.ai/api/v2/analytics/country/{iso2}"

POLICY_TYPE_MAP = {
    "National AI strategy": "strategy",
    "AI strategy": "strategy",
    "Legislation": "legislation",
    "Regulation": "regulation",
    "Guideline": "guideline",
    "Principles": "principle",
    "Funding": "funding",
}

STATUS_MAP = {
    "Adopted": "enacted",
    "Enacted": "enacted",
    "Proposed": "proposed",
    "In force": "enforced",
    "Repealed": "superseded",
}


def _map_policy_type(raw: str | None) -> str:
    if not raw:
        return "other"
    for k, v in POLICY_TYPE_MAP.items():
        if k.lower() in (raw or "").lower():
            return v
    return "other"


def _map_status(raw: str | None) -> str:
    if not raw:
        return "enacted"
    for k, v in STATUS_MAP.items():
        if k.lower() in (raw or "").lower():
            return v
    return "enacted"


def fetch(refresh: bool = False) -> Path:
    """Download raw JSON from OECD.AI API. Returns raw dir path."""
    import json

    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)

    client = make_client()

    # Try the initiatives API endpoint
    try:
        text = fetch_text(INITIATIVES_API, SOURCE_NAME, client=client, refresh=refresh)
        data = json.loads(text)
        logger.info("OECD.AI initiatives API returned %d bytes", len(text))
        (raw_dir / "initiatives.json").write_text(text)
    except Exception as e:
        logger.warning("OECD.AI initiatives API failed: %s — trying country page scrape", e)
        _scrape_country_pages(client, raw_dir, refresh)

    return raw_dir


def _scrape_country_pages(client: Any, raw_dir: Path, refresh: bool) -> None:
    """Fallback: scrape individual country dashboard pages."""
    import json
    from bs4 import BeautifulSoup

    # OECD provides a country list page
    countries_url = "https://oecd.ai/en/dashboards"
    try:
        html = fetch_text(countries_url, SOURCE_NAME, client=client, refresh=refresh)
        soup = BeautifulSoup(html, "lxml")
        # Country links typically follow pattern /en/countries/<iso2>
        country_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if "/en/countries/" in a.get("href", "")
        ]
        logger.info("Found %d country links on OECD.AI dashboard", len(country_links))
        for link in country_links[:10]:  # sample first 10 to avoid rate limiting in CI
            try:
                page = fetch_text(f"https://oecd.ai{link}", SOURCE_NAME, client=client, refresh=refresh)
                (raw_dir / f"country_{link.split('/')[-1]}.html").write_text(page)
            except Exception as ex:
                logger.debug("Skipping %s: %s", link, ex)
    except Exception as e:
        logger.warning("OECD.AI dashboard scrape failed: %s", e)
        (raw_dir / "FETCH_FAILED.txt").write_text(f"Failed at {datetime.now(timezone.utc).isoformat()}: {e}\n")


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    """Parse raw OECD.AI data -> {'policies': df, 'indicators': df}."""
    import json

    retrieved_at = datetime.now(timezone.utc).isoformat()
    policy_rows: list[dict] = []

    # Try JSON initiatives file first
    json_file = raw_dir / "initiatives.json"
    if json_file.exists():
        try:
            data = json.loads(json_file.read_text())
            items = data if isinstance(data, list) else data.get("data", data.get("results", []))
            logger.info("OECD.AI JSON: %d items", len(items))
            for item in items:
                country_raw = item.get("country") or item.get("jurisdiction") or item.get("countryName")
                if not country_raw:
                    continue
                iso3 = to_iso3(str(country_raw))
                if not iso3:
                    continue
                policy_rows.append({
                    "country_iso3": iso3,
                    "country_name": country_name_for_iso3(iso3) or str(country_raw),
                    "policy_id": f"oecd:{item.get('id', item.get('slug', 'unknown'))}",
                    "policy_name": str(item.get("name") or item.get("title") or ""),
                    "policy_type": _map_policy_type(item.get("type") or item.get("category")),
                    "policy_status": _map_status(item.get("status")),
                    "target_sector": item.get("sector") or item.get("theme"),
                    "risk_focus": [],
                    "enacted_date": item.get("date") or item.get("adoptionDate"),
                    "source_url": item.get("url") or f"https://oecd.ai/en/initiatives/{item.get('slug','')}",
                    "source": SOURCE_NAME,
                    "raw_text": None,
                    "retrieved_at": retrieved_at,
                })
        except Exception as e:
            logger.error("Failed to parse OECD.AI JSON: %s", e)

    if not policy_rows:
        logger.warning("No OECD.AI policy rows extracted — API may require auth or changed structure")
        logger.warning("See data/raw/oecd_ai/ for raw files and adjust normalize() if needed")
        return {"policies": pl.DataFrame(), "indicators": pl.DataFrame()}

    df = pl.DataFrame(policy_rows)
    return {"policies": df, "indicators": pl.DataFrame()}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    failures: list[str] = []
    df = tables.get("policies")
    if df is None or df.is_empty():
        failures.append("policies table is empty (OECD.AI API may require auth — check raw dir)")
        return failures
    for col in ("country_iso3", "policy_id", "policy_name", "policy_type", "policy_status"):
        if col not in df.columns:
            failures.append(f"Missing column: {col}")
        elif df[col].null_count() > 0:
            failures.append(f"Column '{col}' has {df[col].null_count()} nulls")
    if "country_iso3" in df.columns:
        bad = df.filter(pl.col("country_iso3").str.len_chars() != 3)
        if len(bad):
            failures.append(f"{len(bad)} rows have invalid country_iso3")
    return failures
