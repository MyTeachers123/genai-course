"""Validated records for the parent intake. Only the fields in the capstone pitch are stored."""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

AgeGroup = Literal["infant", "toddler", "school_age"]
Day = Literal["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class CareSchedule(BaseModel):
    days: list[Day] = Field(description="Days of care, e.g. ['Mon','Tue','Wed','Thu','Fri']")
    start: str = Field(description="Start time, 24h HH:MM")
    end: str = Field(description="End time, 24h HH:MM")

    @field_validator("start", "end")
    @classmethod
    def hhmm(cls, v: str) -> str:
        if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d", v):
            raise ValueError("time must be HH:MM (24h)")
        return v

    @model_validator(mode="after")
    def order(self) -> "CareSchedule":
        if self.end <= self.start:
            raise ValueError("end must be after start")
        if not self.days:
            raise ValueError("at least one day is required")
        return self

    @property
    def hours_per_week(self) -> float:
        h1, m1 = map(int, self.start.split(":"))
        h2, m2 = map(int, self.end.split(":"))
        return round(len(self.days) * ((h2 * 60 + m2) - (h1 * 60 + m1)) / 60, 1)


class CareNeed(BaseModel):
    """What the LLM extracts from the parent's free-text answer (any language)."""
    language: str = Field(description="Language the parent wrote in, English name, e.g. 'Spanish'")
    zip_code: str = Field(description="5-digit California ZIP code")
    monthly_budget_usd: int = Field(description="Most the family can pay per month for all children, in USD")
    age_groups: list[AgeGroup] = Field(description="One entry per child: infant (0-23 months), toddler (2-5 years), school_age (6+)")
    schedule: CareSchedule
    notes: str = Field(default="", description="Other needs in English, short; no names or contact details")

    @field_validator("zip_code")
    @classmethod
    def ca_zip(cls, v: str) -> str:
        v = v.strip()
        if not re.fullmatch(r"9[0-6]\d{3}", v):
            raise ValueError("must be a 5-digit California ZIP (90000-96199)")
        return v

    @field_validator("monthly_budget_usd")
    @classmethod
    def budget_range(cls, v: int) -> int:
        if not 0 < v <= 10000:
            raise ValueError("monthly budget must be between 1 and 10000 USD")
        return v

    @field_validator("age_groups")
    @classmethod
    def one_child_min(cls, v: list[str]) -> list[str]:
        if not 1 <= len(v) <= 6:
            raise ValueError("between 1 and 6 children")
        return v

    @field_validator("notes")
    @classmethod
    def no_contact_in_notes(cls, v: str) -> str:
        if re.search(r"@|\d{3}[-. )]*\d{3}[-. ]*\d{4}", v):
            raise ValueError("notes must not contain contact details")
        return v


class IntakeIn(BaseModel):
    """What the web form posts. Contact details are encrypted before storage."""
    email: str
    phone: str
    answer: str = Field(min_length=10, max_length=2000, description="Free-text answer in any language")

    @field_validator("email")
    @classmethod
    def email_ok(cls, v: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("invalid email")
        return v.strip().lower()

    @field_validator("phone")
    @classmethod
    def phone_ok(cls, v: str) -> str:
        digits = re.sub(r"\D", "", v)
        if len(digits) == 11 and digits.startswith("1"):
            digits = digits[1:]
        if len(digits) != 10:
            raise ValueError("phone must be a 10-digit US number")
        return digits


class AnonymousRequest(BaseModel):
    """What a provider sees: no name, email or phone."""
    request_id: int
    zip_code: str
    age_groups: list[AgeGroup]
    days: list[str]
    hours: str
    monthly_budget_usd: int
    usual_price_usd: int
    discount_pct: float
