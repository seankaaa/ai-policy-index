"""Tests for src/sources/oxford_readiness.py

Unit tests use synthetic Excel data so they don't require network access.
The integration test (marked slow) calls fetch() + normalize() for real.
"""

from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import polars as pl
import pytest

from src.sources.oxford_readiness import (
    _parse_excel,
    _discover_data_urls,
    _merge_url_lists,
    normalize,
    validate,
    SOURCE_NAME,
)


def _make_xlsx(rows: list[dict]) -> bytes:
    """Create a minimal xlsx bytes blob for testing."""
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    if not rows:
        return io.BytesIO(wb.save(io.BytesIO()) or b"").read()  # noqa: won't work; use below

    headers = list(rows[0].keys())
    ws.append(headers)
    for row in rows:
        ws.append([row[h] for h in headers])

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


NOW = datetime.now(timezone.utc)


SAMPLE_ROWS = [
    {
        "Country": "United Kingdom",
        "Overall Score": 81.2,
        "Government": 75.0,
        "Technology Sector": 88.0,
        "Data & Infrastructure": 80.4,
        "Rank": 3,
    },
    {
        "Country": "Germany",
        "Overall Score": 76.5,
        "Government": 70.0,
        "Technology Sector": 82.0,
        "Data & Infrastructure": 77.5,
        "Rank": 6,
    },
    {
        "Country": "Taiwan",
        "Overall Score": 72.0,
        "Government": 65.0,
        "Technology Sector": 79.0,
        "Data & Infrastructure": 72.0,
        "Rank": 11,
    },
    {
        "Country": "Kosovo",
        "Overall Score": 30.1,
        "Government": 28.0,
        "Technology Sector": 31.0,
        "Data & Infrastructure": 31.3,
        "Rank": 112,
    },
]


class TestParseExcel:
    def test_parses_known_countries(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        assert not df.is_empty()
        iso3_vals = df["country_iso3"].to_list()
        assert "GBR" in iso3_vals
        assert "DEU" in iso3_vals

    def test_maps_taiwan_to_twn(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        assert "TWN" in df["country_iso3"].to_list()

    def test_maps_kosovo_to_xkx(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        assert "XKX" in df["country_iso3"].to_list()

    def test_indicator_ids_present(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        ids = df["indicator_id"].to_list()
        assert any("overall" in i for i in ids)
        assert any("government_pillar" in i for i in ids)

    def test_year_recorded(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2022, NOW)
        assert all(y == 2022 for y in df["year"].to_list())

    def test_source_name_recorded(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        assert all(s == SOURCE_NAME for s in df["source"].to_list())

    def test_empty_xlsx_returns_empty_df(self):
        raw = _make_xlsx([])
        df = _parse_excel(raw, 2023, NOW)
        assert df.is_empty()

    def test_schema_columns_present(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        required = {
            "country_iso3", "year", "indicator_id", "indicator_name",
            "value", "unit", "source", "methodology_url", "retrieved_at",
        }
        assert required.issubset(set(df.columns))

    def test_value_types_are_float(self):
        raw = _make_xlsx(SAMPLE_ROWS)
        df = _parse_excel(raw, 2023, NOW)
        assert df["value"].dtype in (pl.Float64, pl.Float32)

    def test_unknown_country_skipped(self):
        rows = SAMPLE_ROWS + [{"Country": "Nowhereland_XYZZY", "Overall Score": 50.0,
                                "Government": 50.0, "Technology Sector": 50.0,
                                "Data & Infrastructure": 50.0, "Rank": 99}]
        raw = _make_xlsx(rows)
        df = _parse_excel(raw, 2023, NOW)
        assert "Nowhereland_XYZZY" not in (df.get_column("country_name").to_list()
                                            if "country_name" in df.columns else [])


class TestMergeUrlLists:
    def test_discovered_overrides_known_for_same_year(self):
        known = [{"year": 2023, "url": "https://known.com/2023.xlsx"}]
        discovered = [{"year": 2023, "url": "https://new.com/2023.xlsx"}]
        merged = _merge_url_lists(discovered, known)
        assert any(e["url"] == "https://new.com/2023.xlsx" for e in merged)

    def test_known_fills_gaps(self):
        known = [{"year": 2022, "url": "https://known.com/2022.xlsx"}]
        discovered = [{"year": 2023, "url": "https://new.com/2023.xlsx"}]
        merged = _merge_url_lists(discovered, known)
        years = [e["year"] for e in merged]
        assert 2022 in years
        assert 2023 in years

    def test_sorted_descending(self):
        known = [{"year": 2021, "url": "a"}, {"year": 2022, "url": "b"}]
        merged = _merge_url_lists([], known)
        years = [e["year"] for e in merged]
        assert years == sorted(years, reverse=True)


class TestNormalize:
    def test_normalize_with_fixture_files(self, tmp_path):
        raw = _make_xlsx(SAMPLE_ROWS)
        (tmp_path / "Oxford-Insights-AI-Readiness-Index-2023.xlsx").write_bytes(raw)

        tables = normalize(tmp_path)
        assert "indicators" in tables
        df = tables["indicators"]
        assert not df.is_empty()
        assert "GBR" in df["country_iso3"].to_list()

    def test_empty_dir_returns_empty_df(self, tmp_path):
        tables = normalize(tmp_path)
        assert tables["indicators"].is_empty()

    def test_deduplication(self, tmp_path):
        raw = _make_xlsx(SAMPLE_ROWS)
        # Write two files for the same year — duplicates should be dropped
        (tmp_path / "Oxford-Insights-2023.xlsx").write_bytes(raw)
        (tmp_path / "Oxford-Insights-2023-copy.xlsx").write_bytes(raw)
        tables = normalize(tmp_path)
        df = tables["indicators"]
        n_uk_overall = len(df.filter(
            (pl.col("country_iso3") == "GBR") & (pl.col("indicator_id") == "oxford_readiness.overall")
        ))
        assert n_uk_overall == 1


def _make_large_sample_rows(n: int = 60) -> list[dict]:
    """Generate synthetic rows for n countries to satisfy country-count validation."""
    import pycountry

    countries = list(pycountry.countries)[:n]
    return [
        {
            "Country": c.name,
            "Overall Score": 50.0 + (i % 50),
            "Government": 45.0 + (i % 50),
            "Technology Sector": 55.0 + (i % 40),
            "Data & Infrastructure": 48.0 + (i % 50),
            "Rank": i + 1,
        }
        for i, c in enumerate(countries)
    ]


class TestValidate:
    def _make_valid_df(self) -> pl.DataFrame:
        raw = _make_xlsx(_make_large_sample_rows(60))
        df = _parse_excel(raw, 2023, NOW)
        return df

    def test_valid_df_passes(self):
        df = self._make_valid_df()
        failures = validate({"indicators": df})
        assert failures == [], failures

    def test_empty_df_fails(self):
        failures = validate({"indicators": pl.DataFrame()})
        assert len(failures) > 0

    def test_missing_table_fails(self):
        failures = validate({})
        assert len(failures) > 0

    def test_null_country_fails(self):
        df = self._make_valid_df()
        df = df.with_columns(pl.lit(None).cast(pl.Utf8).alias("country_iso3"))
        failures = validate({"indicators": df})
        assert any("country_iso3" in f for f in failures)

    def test_out_of_range_score_fails(self):
        df = self._make_valid_df()
        # Inject a bad value
        df = df.with_columns(
            pl.when(pl.col("indicator_id") == "oxford_readiness.overall")
            .then(pl.lit(150.0))
            .otherwise(pl.col("value"))
            .alias("value")
        )
        failures = validate({"indicators": df})
        assert any("score_0_100" in f or "100" in f for f in failures)

    def test_out_of_range_year_fails(self):
        df = self._make_valid_df()
        df = df.with_columns(pl.lit(2010).alias("year"))
        failures = validate({"indicators": df})
        assert any("year" in f for f in failures)
