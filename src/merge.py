"""Merge all per-source interim parquets into unified processed tables.

Output:
  data/processed/policies.parquet
  data/processed/indicators.parquet
  data/processed/public_opinion.parquet
  data/processed/country_year_panel.parquet   (wide regression panel)
  data/processed/sources_metadata.csv
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from pathlib import Path

import polars as pl

logger = logging.getLogger(__name__)

INTERIM_DIR = Path("data/interim")
PROCESSED_DIR = Path("data/processed")

# Maps table name -> list of required columns that must exist in every source's output
REQUIRED_COLS: dict[str, list[str]] = {
    "policies": ["country_iso3", "policy_id", "policy_name", "policy_type", "policy_status"],
    "indicators": ["country_iso3", "year", "indicator_id", "value"],
    "public_opinion": ["country_iso3", "year", "survey", "question_id", "value"],
}

# Columns used for deduplication per table
DEDUP_KEYS: dict[str, list[str]] = {
    "policies": ["country_iso3", "policy_id"],
    "indicators": ["country_iso3", "year", "indicator_id"],
    "public_opinion": ["country_iso3", "year", "question_id", "response_category"],
}

# Indicator IDs to pivot into the wide panel (representative cross-source set)
PANEL_INDICATORS = [
    "oxford_readiness.overall",
    "oxford_readiness.government_pillar",
    "oxford_readiness.technology_sector_pillar",
    "oxford_readiness.data_infrastructure_pillar",
    "girai.overall",
    "girai.governance",
    "girai.human_rights",
    "oecd_ai.strategy_count",
    "unesco_ram.readiness",
    "unesco_ram.policy",
]


def _load_table(table_name: str) -> pl.DataFrame:
    """Concatenate all per-source parquets for a given table type."""
    frames: list[pl.DataFrame] = []
    required = REQUIRED_COLS[table_name]

    for source_dir in sorted(INTERIM_DIR.iterdir()):
        if not source_dir.is_dir():
            continue
        parquet_path = source_dir / f"{table_name}.parquet"
        if not parquet_path.exists():
            continue
        try:
            df = pl.read_parquet(parquet_path)
            if df.is_empty():
                logger.debug("merge: %s/%s.parquet is empty — skipping", source_dir.name, table_name)
                continue
            missing = [c for c in required if c not in df.columns]
            if missing:
                logger.warning(
                    "merge: %s/%s.parquet missing columns %s — skipping",
                    source_dir.name, table_name, missing,
                )
                continue
            frames.append(df)
            logger.info("merge: loaded %d rows from %s/%s", len(df), source_dir.name, table_name)
        except Exception as e:
            logger.warning("merge: failed to load %s/%s.parquet: %s", source_dir.name, table_name, e)

    if not frames:
        logger.warning("merge: no data found for table %s", table_name)
        return pl.DataFrame()

    combined = pl.concat(frames, how="diagonal_relaxed")
    dedup_keys = DEDUP_KEYS[table_name]
    before = len(combined)
    combined = combined.unique(subset=dedup_keys, keep="first")
    after = len(combined)
    if before != after:
        logger.info("merge: %s deduped %d -> %d rows", table_name, before, after)
    return combined


def _build_panel(indicators: pl.DataFrame) -> pl.DataFrame:
    """Build a wide-format country×year panel for regression use."""
    if indicators.is_empty():
        return pl.DataFrame()

    panel_df = indicators.filter(pl.col("indicator_id").is_in(PANEL_INDICATORS))
    if panel_df.is_empty():
        logger.warning("merge: no panel indicators found in indicators table")
        return pl.DataFrame()

    wide = panel_df.pivot(
        values="value",
        index=["country_iso3", "year"],
        on="indicator_id",
        aggregate_function="first",
    )
    wide = wide.sort(["country_iso3", "year"])
    return wide


def _sources_metadata() -> pl.DataFrame:
    """Build a summary of what each source contributed."""
    rows: list[dict] = []
    for source_dir in sorted(INTERIM_DIR.iterdir()):
        if not source_dir.is_dir():
            continue
        source_name = source_dir.name
        for parquet_path in sorted(source_dir.glob("*.parquet")):
            table_name = parquet_path.stem
            try:
                df = pl.read_parquet(parquet_path)
                n_rows = len(df)
                n_countries = df["country_iso3"].n_unique() if "country_iso3" in df.columns else None
                year_min = int(df["year"].min()) if "year" in df.columns and n_rows > 0 else None
                year_max = int(df["year"].max()) if "year" in df.columns and n_rows > 0 else None
            except Exception:
                n_rows = 0
                n_countries = None
                year_min = None
                year_max = None
            rows.append({
                "source": source_name,
                "table": table_name,
                "n_rows": n_rows,
                "n_countries": n_countries,
                "year_min": year_min,
                "year_max": year_max,
                "parquet_path": str(parquet_path),
                "merged_at": datetime.now(timezone.utc).isoformat(),
            })
    return pl.DataFrame(rows)


def run() -> dict[str, pl.DataFrame]:
    """Run the full merge pipeline and write all processed outputs."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, pl.DataFrame] = {}

    for table_name in ("policies", "indicators", "public_opinion"):
        logger.info("merge: processing %s ...", table_name)
        df = _load_table(table_name)
        out_path = PROCESSED_DIR / f"{table_name}.parquet"
        df.write_parquet(out_path)
        results[table_name] = df
        logger.info("merge: wrote %d rows to %s", len(df), out_path)

    panel = _build_panel(results.get("indicators", pl.DataFrame()))
    panel_path = PROCESSED_DIR / "country_year_panel.parquet"
    panel.write_parquet(panel_path)
    results["country_year_panel"] = panel
    logger.info("merge: panel written: %d rows, %d columns -> %s", len(panel), len(panel.columns), panel_path)

    meta = _sources_metadata()
    meta_path = PROCESSED_DIR / "sources_metadata.csv"
    meta.write_csv(meta_path)
    logger.info("merge: sources_metadata written -> %s", meta_path)

    return results


def summary(results: dict[str, pl.DataFrame]) -> str:
    lines = ["## Merge summary\n"]
    for name, df in results.items():
        if df.is_empty():
            lines.append(f"- **{name}**: empty")
        else:
            n_countries = df["country_iso3"].n_unique() if "country_iso3" in df.columns else "n/a"
            lines.append(f"- **{name}**: {len(df):,} rows, {n_countries} countries")
    return "\n".join(lines)


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
    results = run()
    print(summary(results))
