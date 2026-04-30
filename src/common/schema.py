"""Pydantic models for the three unified output tables.

These define the canonical schema; per-source normalizers must produce
DataFrames that match the column names and types defined here.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator


class PolicyType(str, Enum):
    strategy = "strategy"
    legislation = "legislation"
    regulation = "regulation"
    guideline = "guideline"
    principle = "principle"
    funding = "funding"
    other = "other"


class PolicyStatus(str, Enum):
    proposed = "proposed"
    enacted = "enacted"
    enforced = "enforced"
    superseded = "superseded"


class PolicyRow(BaseModel):
    """One row per (country, policy) pair in the `policies` table."""

    country_iso3: str = Field(min_length=3, max_length=3)
    country_name: str
    policy_id: str
    policy_name: str
    policy_type: PolicyType
    policy_status: PolicyStatus
    target_sector: str | None = None
    risk_focus: list[str] = Field(default_factory=list)
    enacted_date: date | None = None
    source_url: str
    source: str
    raw_text: str | None = None  # always None — project policy is metadata+URL only
    retrieved_at: datetime

    @field_validator("country_iso3")
    @classmethod
    def iso3_uppercase(cls, v: str) -> str:
        return v.upper()


class IndicatorRow(BaseModel):
    """One row per (country, year, indicator) in the `indicators` table."""

    country_iso3: str = Field(min_length=3, max_length=3)
    year: int = Field(ge=2015, le=2030)
    indicator_id: str
    indicator_name: str
    value: float
    unit: str
    source: str
    methodology_url: str
    retrieved_at: datetime

    @field_validator("country_iso3")
    @classmethod
    def iso3_uppercase(cls, v: str) -> str:
        return v.upper()


class PublicOpinionRow(BaseModel):
    """One row per (country, year, question, response_value) in `public_opinion`."""

    country_iso3: str = Field(min_length=3, max_length=3)
    year: int = Field(ge=2015, le=2030)
    survey: str
    question_id: str
    question_text: str
    response_category: str
    value: float
    n: int | None = None
    weighted: bool
    source_url: str
    retrieved_at: datetime

    @field_validator("country_iso3")
    @classmethod
    def iso3_uppercase(cls, v: str) -> str:
        return v.upper()


# Polars-compatible schema dicts (column_name -> dtype string).
# Used by normalizers to cast DataFrames to canonical types.

POLICIES_SCHEMA: dict[str, Any] = {
    "country_iso3": str,
    "country_name": str,
    "policy_id": str,
    "policy_name": str,
    "policy_type": str,
    "policy_status": str,
    "target_sector": str,
    "risk_focus": list,
    "enacted_date": str,
    "source_url": str,
    "source": str,
    "raw_text": str,
    "retrieved_at": str,
}

INDICATORS_SCHEMA: dict[str, Any] = {
    "country_iso3": str,
    "year": int,
    "indicator_id": str,
    "indicator_name": str,
    "value": float,
    "unit": str,
    "source": str,
    "methodology_url": str,
    "retrieved_at": str,
}

PUBLIC_OPINION_SCHEMA: dict[str, Any] = {
    "country_iso3": str,
    "year": int,
    "survey": str,
    "question_id": str,
    "question_text": str,
    "response_category": str,
    "value": float,
    "n": int,
    "weighted": bool,
    "source_url": str,
    "retrieved_at": str,
}

VALID_TABLE_KEYS = frozenset({"policies", "indicators", "public_opinion"})
