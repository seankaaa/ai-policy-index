"""Command-line interface: python -m src.cli fetch <source> | normalize <source> | validate <source>"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

SOURCES = {
    "oxford_readiness": "src.sources.oxford_readiness",
}


def _load_source(name: str):
    import importlib

    mod_path = SOURCES.get(name)
    if mod_path is None:
        print(f"Unknown source: {name!r}. Known: {list(SOURCES)}", file=sys.stderr)
        sys.exit(1)
    return importlib.import_module(mod_path)


def cmd_fetch(source: str, refresh: bool) -> None:
    mod = _load_source(source)
    raw_dir = mod.fetch(refresh=refresh)
    print(f"Raw data in: {raw_dir}")


def cmd_normalize(source: str) -> dict:
    import polars as pl

    mod = _load_source(source)
    raw_dir = Path("data/raw") / source
    tables = mod.normalize(raw_dir)

    interim_dir = Path("data/interim") / source
    interim_dir.mkdir(parents=True, exist_ok=True)

    for table_name, df in tables.items():
        if df.is_empty():
            print(f"  [WARN] {table_name}: empty")
            continue
        out_path = interim_dir / f"{table_name}.parquet"
        df.write_parquet(out_path)
        print(f"  Wrote {len(df):,} rows -> {out_path}")

    return tables


def cmd_validate(source: str) -> None:
    import polars as pl

    mod = _load_source(source)
    interim_dir = Path("data/interim") / source
    tables: dict[str, pl.DataFrame] = {}
    for parquet_file in interim_dir.glob("*.parquet"):
        key = parquet_file.stem
        tables[key] = pl.read_parquet(parquet_file)

    failures = mod.validate(tables)
    if failures:
        print(f"VALIDATION FAILURES for {source}:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        print(f"Validation OK for {source}")


def main() -> None:
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python -m src.cli <fetch|normalize|validate> <source> [--refresh]")
        sys.exit(1)

    command, source = args[0], args[1]
    refresh = "--refresh" in args

    if command == "fetch":
        cmd_fetch(source, refresh=refresh)
    elif command == "normalize":
        cmd_normalize(source)
    elif command == "validate":
        cmd_validate(source)
    elif command == "run":
        cmd_fetch(source, refresh=refresh)
        cmd_normalize(source)
        cmd_validate(source)
    else:
        print(f"Unknown command: {command!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
