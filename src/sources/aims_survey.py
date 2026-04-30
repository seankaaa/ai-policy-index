"""AIMS Survey (Sentience Institute / OSF) source.

OSF project: https://osf.io/  — search 'AIMS survey Sentience Institute'
Feeds `public_opinion` table.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

from src.common.countries import to_iso3, country_name_for_iso3
from src.common.http import fetch_bytes, make_client

logger = logging.getLogger(__name__)

SOURCE_NAME = "aims_survey"
METHODOLOGY_URL = "https://osf.io/preprints/osf/cxu8r"
SOURCE_URL = "https://osf.io/cxu8r"

# OSF direct download URLs for AIMS replication data
# OSF file IDs can be found via the OSF API: https://api.osf.io/v2/nodes/<project>/files/
OSF_DATA_URLS = [
    "https://osf.io/download/cxu8r/",
    "https://osf.io/cxu8r/download",
]


def fetch(refresh: bool = False) -> Path:
    raw_dir = Path("data/raw") / SOURCE_NAME
    raw_dir.mkdir(parents=True, exist_ok=True)
    client = make_client()

    fetched = False
    for url in OSF_DATA_URLS:
        try:
            fetch_bytes(url, SOURCE_NAME, client=client, refresh=refresh)
            fetched = True
            logger.info("AIMS: fetched from %s", url)
            break
        except Exception as e:
            logger.debug("AIMS fetch failed for %s: %s", url, e)

    if not fetched:
        # Try OSF API to discover file download links
        try:
            import json
            api_url = "https://api.osf.io/v2/nodes/?filter[tags]=AIMS&filter[tags]=AI"
            text = fetch_bytes(api_url, SOURCE_NAME, client=client, refresh=refresh)
            data = json.loads(text)
            logger.info("OSF API returned %d nodes", len(data.get("data", [])))
        except Exception as e:
            logger.warning("AIMS OSF API failed: %s", e)
        (raw_dir / "ACCESS_NOTE.txt").write_text(
            "AIMS Survey data is on OSF. Search https://osf.io for 'AIMS survey Sentience Institute'.\n"
            "Download the CSV replication file and place it in this directory.\n"
            f"Methodology: {METHODOLOGY_URL}\n"
        )
    return raw_dir


def normalize(raw_dir: Path) -> dict[str, pl.DataFrame]:
    retrieved_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []

    for fpath in list(raw_dir.glob("*.csv")) + list(raw_dir.glob("*.xlsx")):
        try:
            df = pl.read_csv(fpath) if fpath.suffix == ".csv" else pl.read_excel(fpath)
        except Exception as e:
            logger.warning("AIMS: failed to parse %s: %s", fpath, e)
            continue

        country_col = next((c for c in df.columns if "country" in c.lower()), None)
        if not country_col:
            continue

        question_cols = [c for c in df.columns if c != country_col]
        year_col = next((c for c in df.columns if "year" in c.lower()), None)

        for raw_row in df.to_dicts():
            iso3 = to_iso3(str(raw_row.get(country_col) or ""))
            if not iso3:
                continue
            year = int(raw_row.get(year_col, 2023)) if year_col else 2023
            for q_col in question_cols:
                if q_col == year_col:
                    continue
                try:
                    value = float(raw_row[q_col])
                except (TypeError, ValueError):
                    continue
                rows.append({
                    "country_iso3": iso3,
                    "year": year,
                    "survey": "aims_survey",
                    "question_id": f"aims.{q_col.lower().replace(' ','_')[:50]}",
                    "question_text": q_col,
                    "response_category": "",
                    "value": value,
                    "n": None,
                    "weighted": False,
                    "source_url": SOURCE_URL,
                    "retrieved_at": retrieved_at,
                })

    if not rows:
        logger.warning("AIMS: no data — place CSV in %s", raw_dir)
        return {"public_opinion": pl.DataFrame()}
    return {"public_opinion": pl.DataFrame(rows)}


def validate(tables: dict[str, pl.DataFrame]) -> list[str]:
    df = tables.get("public_opinion")
    if df is None or df.is_empty():
        return ["public_opinion empty — AIMS data needs manual download from OSF"]
    return []
