"""ISO 3166-1 alpha-3 country name normalization.

Unmapped names are logged to data/interim/unmapped_countries.csv.
"""

import csv
import logging
from pathlib import Path

import pycountry

logger = logging.getLogger(__name__)

# Manual overrides for names pycountry misses or handles inconsistently.
_OVERRIDES: dict[str, str] = {
    # Oxford Insights PDF-extracted names
    "Iran (Islamic Republic of)": "IRN",
    "Bolivia (Plurinational State of)": "BOL",
    "Gambia (Republic of The)": "GMB",
    "Gambia": "GMB",
    "Guinea Bissau": "GNB",
    "Guinea-Bissau": "GNB",
    "Democratic Republic of the Congo": "COD",
    "Congo, Dem. Rep.": "COD",
    "Venezuela (Bolivarian Republic of)": "VEN",
    "Micronesia (Federated States of)": "FSM",
    "Korea (Democratic People's Republic of)": "PRK",
    "Korea (Republic of)": "KOR",
    "Côte d'Ivoire": "CIV",
    "Cote D'Ivoire": "CIV",
    "Côte D'Ivoire": "CIV",
    # Common variants
    "Kosovo": "XKX",
    "Taiwan": "TWN",
    "Palestine": "PSE",
    "Palestinian Territory": "PSE",
    "State of Palestine": "PSE",
    "South Korea": "KOR",
    "Republic of Korea": "KOR",
    "Korea, Republic of": "KOR",
    "Korea, South": "KOR",
    "North Korea": "PRK",
    "Korea, North": "PRK",
    "UK": "GBR",
    "United Kingdom": "GBR",
    "Great Britain": "GBR",
    "England": "GBR",
    "USA": "USA",
    "United States": "USA",
    "United States of America": "USA",
    "US": "USA",
    "Czech Republic": "CZE",
    "Czechia": "CZE",
    "Türkiye": "TUR",
    "Turkey": "TUR",
    "Russia": "RUS",
    "Russian Federation": "RUS",
    "Belarus": "BLR",
    "Ivory Coast": "CIV",
    "Côte d'Ivoire": "CIV",
    "Cote d'Ivoire": "CIV",
    "Congo, Democratic Republic": "COD",
    "DR Congo": "COD",
    "Congo-Kinshasa": "COD",
    "Congo, Republic": "COG",
    "Congo-Brazzaville": "COG",
    "Iran": "IRN",
    "Iran, Islamic Republic of": "IRN",
    "Syria": "SYR",
    "Syrian Arab Republic": "SYR",
    "Venezuela": "VEN",
    "Bolivia": "BOL",
    "Tanzania": "TZA",
    "United Republic of Tanzania": "TZA",
    "Vietnam": "VNM",
    "Viet Nam": "VNM",
    "Laos": "LAO",
    "Lao PDR": "LAO",
    "Moldova": "MDA",
    "Republic of Moldova": "MDA",
    "North Macedonia": "MKD",
    "Macedonia": "MKD",
    "Brunei": "BRN",
    "Brunei Darussalam": "BRN",
    "Eswatini": "SWZ",
    "Swaziland": "SWZ",
    "Cape Verde": "CPV",
    "Cabo Verde": "CPV",
    "Timor-Leste": "TLS",
    "East Timor": "TLS",
    "Micronesia": "FSM",
    "Federated States of Micronesia": "FSM",
    "Saint Kitts and Nevis": "KNA",
    "St. Kitts and Nevis": "KNA",
    "Saint Lucia": "LCA",
    "St. Lucia": "LCA",
    "Saint Vincent and the Grenadines": "VCT",
    "St. Vincent and the Grenadines": "VCT",
    "Trinidad & Tobago": "TTO",
    "Antigua & Barbuda": "ATG",
    "Bosnia & Herzegovina": "BIH",
    "Bosnia and Herzegovina": "BIH",
}

_UNMAPPED_LOG = Path("data/interim/unmapped_countries.csv")
_logged_unmapped: set[str] = set()


def _log_unmapped(name: str) -> None:
    if name in _logged_unmapped:
        return
    _logged_unmapped.add(name)
    _UNMAPPED_LOG.parent.mkdir(parents=True, exist_ok=True)
    write_header = not _UNMAPPED_LOG.exists()
    with _UNMAPPED_LOG.open("a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["country_name", "note"])
        writer.writerow([name, "no iso3 match found"])
    logger.warning("Unmapped country name: %r — logged to %s", name, _UNMAPPED_LOG)


def to_iso3(name: str) -> str | None:
    """Return ISO 3166-1 alpha-3 code for a country name, or None if unknown.

    Tries manual override map first, then pycountry fuzzy search.
    Logs unmapped names to data/interim/unmapped_countries.csv.
    """
    if not name or not name.strip():
        return None

    cleaned = name.strip()

    if cleaned in _OVERRIDES:
        return _OVERRIDES[cleaned]

    # pycountry exact lookup by common/official name
    result = pycountry.countries.get(name=cleaned)
    if result:
        return result.alpha_3

    result = pycountry.countries.get(common_name=cleaned)
    if result:
        return result.alpha_3

    result = pycountry.countries.get(official_name=cleaned)
    if result:
        return result.alpha_3

    # pycountry fuzzy search (broader, may have false positives)
    try:
        matches = pycountry.countries.search_fuzzy(cleaned)
        if matches:
            return matches[0].alpha_3
    except LookupError:
        pass

    _log_unmapped(cleaned)
    return None


def is_valid_iso3(code: str) -> bool:
    """Return True if code is a known ISO 3166-1 alpha-3 code (or a custom code like XKX)."""
    _custom = {"XKX"}  # Kosovo
    if code in _custom:
        return True
    return pycountry.countries.get(alpha_3=code) is not None


def country_name_for_iso3(iso3: str) -> str | None:
    """Return English country name for an ISO 3166-1 alpha-3 code."""
    _custom_names = {"XKX": "Kosovo"}
    if iso3 in _custom_names:
        return _custom_names[iso3]
    result = pycountry.countries.get(alpha_3=iso3)
    if result:
        return getattr(result, "common_name", None) or result.name
    return None
