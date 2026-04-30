"""Tests for src/common/countries.py"""

import pytest
from src.common.countries import to_iso3, is_valid_iso3, country_name_for_iso3


class TestToIso3:
    def test_standard_names(self):
        assert to_iso3("Germany") == "DEU"
        assert to_iso3("France") == "FRA"
        assert to_iso3("Japan") == "JPN"
        assert to_iso3("Brazil") == "BRA"
        assert to_iso3("India") == "IND"

    def test_override_map(self):
        assert to_iso3("Kosovo") == "XKX"
        assert to_iso3("Taiwan") == "TWN"
        assert to_iso3("Palestine") == "PSE"
        assert to_iso3("South Korea") == "KOR"
        assert to_iso3("UK") == "GBR"
        assert to_iso3("USA") == "USA"
        assert to_iso3("Czech Republic") == "CZE"
        assert to_iso3("Türkiye") == "TUR"
        assert to_iso3("Russia") == "RUS"
        assert to_iso3("Belarus") == "BLR"

    def test_alternate_names(self):
        assert to_iso3("United States") == "USA"
        assert to_iso3("United Kingdom") == "GBR"
        assert to_iso3("South Korea") == "KOR"
        assert to_iso3("Iran") == "IRN"
        assert to_iso3("Vietnam") == "VNM"

    def test_empty_returns_none(self):
        assert to_iso3("") is None
        assert to_iso3("  ") is None

    def test_unknown_returns_none_and_logs(self, tmp_path, monkeypatch):
        import src.common.countries as m
        monkeypatch.setattr(m, "_UNMAPPED_LOG", tmp_path / "unmapped.csv")
        monkeypatch.setattr(m, "_logged_unmapped", set())
        result = to_iso3("Nowhereland_XYZZY_99")
        assert result is None
        assert (tmp_path / "unmapped.csv").exists()

    def test_strips_whitespace(self):
        assert to_iso3("  Germany  ") == "DEU"


class TestIsValidIso3:
    def test_valid_codes(self):
        assert is_valid_iso3("DEU") is True
        assert is_valid_iso3("USA") is True
        assert is_valid_iso3("XKX") is True  # Kosovo custom

    def test_invalid_codes(self):
        assert is_valid_iso3("ZZZ") is False
        assert is_valid_iso3("") is False
        assert is_valid_iso3("US") is False


class TestCountryNameForIso3:
    def test_known_codes(self):
        name = country_name_for_iso3("DEU")
        assert name is not None
        assert "Germany" in name or name == "Germany"

    def test_kosovo_custom(self):
        assert country_name_for_iso3("XKX") == "Kosovo"

    def test_unknown_returns_none(self):
        assert country_name_for_iso3("ZZZ") is None
