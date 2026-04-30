"""Tests for src/common/schema.py"""

from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from src.common.schema import (
    PolicyRow,
    PolicyType,
    PolicyStatus,
    IndicatorRow,
    PublicOpinionRow,
    VALID_TABLE_KEYS,
)

NOW = datetime.now(timezone.utc)


class TestPolicyRow:
    def _valid(self, **overrides):
        base = dict(
            country_iso3="DEU",
            country_name="Germany",
            policy_id="test:001",
            policy_name="AI Act",
            policy_type=PolicyType.legislation,
            policy_status=PolicyStatus.enacted,
            source_url="https://example.com",
            source="TEST",
            retrieved_at=NOW,
        )
        base.update(overrides)
        return PolicyRow(**base)

    def test_valid_row(self):
        row = self._valid()
        assert row.country_iso3 == "DEU"
        assert row.policy_type == PolicyType.legislation

    def test_iso3_uppercased(self):
        row = self._valid(country_iso3="deu")
        assert row.country_iso3 == "DEU"

    def test_optional_fields_default_none(self):
        row = self._valid()
        assert row.target_sector is None
        assert row.enacted_date is None
        assert row.raw_text is None
        assert row.risk_focus == []

    def test_invalid_policy_type(self):
        with pytest.raises(ValidationError):
            self._valid(policy_type="unknown_type")

    def test_invalid_iso3_too_short(self):
        with pytest.raises(ValidationError):
            self._valid(country_iso3="DE")


class TestIndicatorRow:
    def _valid(self, **overrides):
        base = dict(
            country_iso3="GBR",
            year=2023,
            indicator_id="oxford_readiness.overall",
            indicator_name="Overall Score",
            value=72.5,
            unit="score_0_100",
            source="oxford_readiness",
            methodology_url="https://oxfordinsights.com/methodology",
            retrieved_at=NOW,
        )
        base.update(overrides)
        return IndicatorRow(**base)

    def test_valid_row(self):
        row = self._valid()
        assert row.value == 72.5
        assert row.year == 2023

    def test_year_out_of_range(self):
        with pytest.raises(ValidationError):
            self._valid(year=2010)
        with pytest.raises(ValidationError):
            self._valid(year=2031)

    def test_iso3_uppercased(self):
        row = self._valid(country_iso3="gbr")
        assert row.country_iso3 == "GBR"


class TestPublicOpinionRow:
    def _valid(self, **overrides):
        base = dict(
            country_iso3="FRA",
            year=2022,
            survey="ipsos_ai_monitor",
            question_id="q1",
            question_text="Do you support AI regulation?",
            response_category="strongly support",
            value=45.2,
            weighted=True,
            source_url="https://example.com/survey",
            retrieved_at=NOW,
        )
        base.update(overrides)
        return PublicOpinionRow(**base)

    def test_valid_row(self):
        row = self._valid()
        assert row.value == 45.2
        assert row.weighted is True

    def test_optional_n(self):
        row = self._valid()
        assert row.n is None
        row2 = self._valid(n=1000)
        assert row2.n == 1000


class TestValidTableKeys:
    def test_contains_expected_keys(self):
        assert "policies" in VALID_TABLE_KEYS
        assert "indicators" in VALID_TABLE_KEYS
        assert "public_opinion" in VALID_TABLE_KEYS
