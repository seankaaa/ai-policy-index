"""World Risk Poll (Lloyd's Register Foundation) source.

Data: https://wrp.lrfoundation.org.uk/data-resources/
Open microdata download, ~140 countries.
Feeds `public_opinion` table.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, fetch_text, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "world_risk_poll"
SOURCE_URL = "https://wrp.lrfoundation.org.uk/"
METHODOLOGY_URL = "https://wrp.lrfoundation.org.uk/about-the-poll/"

DATA_PAGE_URL = "https://wrp.lrfoundation.org.uk/data-resources/"

# Key AI/tech risk questions in the WRP
WRP_TECH_QUESTIONS = {
    "wrp_tech_worry": "In the past 12 months, have you ever worried about the safety of using modern technology?",
    "wrp_ai_concern": "How concerned are you about the use of AI in decisions that affect you?",
}


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    # Try to discover data download links from the page
    try:
        html = fetch_text(DATA_PAGE_URL, SOURCE_NAME, client=client, refresh=refresh)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, "lxml")
        data_links = [
            a["href"] for a in soup.find_all("a", href=True)
            if any(ext in a["href"].lower() for ext in (".csv", ".xlsx", ".sav", ".dta", ".zip"))
        ]
        fetched = 0
        for link in data_links[:5]:
            url = link if link.startswith("http") else f"https://wrp.lrfoundation.org.uk{link}"
            try:
                fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
                fetched += 1
                logger.info("WRP: fetched %s", url.split("/")[-1])
            except Exception as e:
                logger.debug("WRP: failed %s: %s", url, e)
        if fetched == 0:
            logger.warning("WRP: no data files found — registration may be required")
            (raw_dir / "ACCESS_NOTE.txt").write_text(
                "World Risk Poll data requires registration at https://wrp.lrfoundation.org.uk/data-resources/\n"
                "Download the microdata (CSV/Excel) and place in this directory.\n"
            )
    except Exception as e:
        logger.warning("WRP: data page scrape failed: %s", e)

    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for fpath in list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.xlsx")):
        try:
            df = pl.read_csv(fpath) if fpath.suffix == ".csv" else pl.read_excel(fpath)
        except Exception as e:
            logger.warning("WRP: failed to parse %s: %s", fpath, e)
            continue

        country_col = next((c for c in df.columns if any(x in c.lower() for x in ("country", "nation", "wgt_country"))), None)
        if not country_col:
            continue

        import re
        year_m = re.search(r"20(\d{2})", fpath.name)
        year = int("20" + year_m.group(1)) if year_m else 2021  # WRP 2021 wave

        tech_cols = [c for c in df.columns if any(x in c.lower() for x in ("tech", "ai", "robot", "digital", "worry", "risk"))]

        for raw_row in df.to_dicts():
            iso3 = to_iso3(str(raw_row.get(country_col) or ""))
            if not iso3:
                continue
            for q_col in tech_cols:
                try:
                    value = float(raw_row[q_col])
                except (TypeError, ValueError):
                    continue
                rows.append({
                    "country_iso3": iso3,
                    "year": year,
                    "survey": "world_risk_poll",
                    "question_id": f"wrp.{q_col.lower()[:50]}",
                    "question_text": q_col,
                    "response_category": "",
                    "value": value,
                    "n": None,
                    "weighted": True,
                    "source_url": SOURCE_URL,
                    "retrieved_at": retrieved_at,
                })

    if not rows:
        logger.warning("WRP: no data parsed — place downloaded files in %s", raw_dir)
        return {"public_opinion": pl.DataFrame()}

    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty — WRP data needs download from lrfoundation.org.uk"]
    n_countries = df["country_iso3"].n_unique()
    if n_countries < 50:
        return [f"Only {n_countries} countries — expected 100+ (WRP covers ~140)"]
    return []
