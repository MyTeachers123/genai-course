"""Rule-based matching: same ZIP, an open seat for every child, hours and days covered, discount within limit."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from .schemas import CareNeed

MAX_DISCOUNT = 0.40       # do not ask providers for more than 40% off their usual price
PAGE = "https://MyTeachers123.com/{license}"


@dataclass
class Provider:
    license: str
    name: str
    zip_code: str
    open_seats: dict[str, int]
    prices: dict[str, int]
    days: list[str]
    open_time: str
    close_time: str

    @property
    def page_url(self) -> str:
        return PAGE.format(license=self.license)


def load_providers(path: str | Path) -> list[Provider]:
    out = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            out.append(Provider(
                license=r["license"], name=r["name"], zip_code=r["zip"],
                open_seats={g: int(r[f"{g}_open"]) for g in ("infant", "toddler", "school_age")},
                prices={g: int(r[f"{g}_price"]) for g in ("infant", "toddler", "school_age")},
                days=r["days"].split("|"), open_time=r["open"], close_time=r["close"]))
    return out


@dataclass
class Match:
    provider: Provider
    usual_price: int
    discount_pct: float


def find_matches(need: CareNeed, providers: list[Provider]) -> tuple[list[Match], dict[str, int]]:
    """Return candidate providers (smallest discount first) and a count of why others were excluded."""
    reasons = {"other_zip": 0, "no_seat": 0, "hours_or_days": 0, "discount_too_big": 0}
    out = []
    for p in providers:
        if p.zip_code != need.zip_code:
            reasons["other_zip"] += 1
            continue
        wanted = {g: need.age_groups.count(g) for g in set(need.age_groups)}
        if any(p.open_seats.get(g, 0) < n for g, n in wanted.items()):
            reasons["no_seat"] += 1
            continue
        s = need.schedule
        if not (set(s.days) <= set(p.days) and p.open_time <= s.start and s.end <= p.close_time):
            reasons["hours_or_days"] += 1
            continue
        usual = sum(p.prices[g] for g in need.age_groups)
        discount = max(0.0, (usual - need.monthly_budget_usd) / usual)
        if discount > MAX_DISCOUNT:
            reasons["discount_too_big"] += 1
            continue
        out.append(Match(p, usual, round(discount, 3)))
    out.sort(key=lambda m: m.discount_pct)
    return out, reasons
