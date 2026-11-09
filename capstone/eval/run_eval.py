"""Measure extraction accuracy, privacy, match rate and cost per request on eval/cases.json.

Usage:  CAPSTONE_LLM=claude CAPSTONE_MODEL=claude-sonnet-4-5 python -m eval.run_eval
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from pathlib import Path

import pandas as pd
from pydantic import ValidationError

from app.extract import extract
from app.matching import find_matches, load_providers

ROOT = Path(__file__).resolve().parent.parent
FIELDS = ["language", "zip_code", "monthly_budget_usd", "age_groups", "days", "start", "end"]


def field_ok(f, got, exp):
    if f == "monthly_budget_usd":
        return abs(got - exp) <= 0.05 * exp           # 5% tolerance for weekly/hourly conversions
    if f == "age_groups":
        return Counter(got) == Counter(exp)
    return got == exp


def run(cases_path=ROOT / "eval" / "cases.json"):
    cases = json.loads(Path(cases_path).read_text())
    providers = load_providers(ROOT / "data" / "providers_sample.csv")
    rows = []
    for c in cases:
        row = {"id": c["id"]}
        try:
            r = extract(c["answer"])
        except Exception as e:   # validation errors and unparseable output both count as rejected
            row.update({"result": "rejected", "correct_fields": 0 if c["expect"] != "reject" else len(FIELDS),
                        "all_correct": c["expect"] == "reject", "privacy_ok": True, "matches": 0,
                        "cost_usd": None, "detail": str(e).splitlines()[0][:80]})
            rows.append(row)
            continue
        n = r.need
        got = {"language": n.language, "zip_code": n.zip_code, "monthly_budget_usd": n.monthly_budget_usd,
               "age_groups": n.age_groups, "days": n.schedule.days, "start": n.schedule.start, "end": n.schedule.end}
        blob = json.dumps(n.model_dump())
        privacy_ok = not re.search(r"@|\d{3}[-. )]*\d{3}[-. ]*\d{4}|maria|lopez", blob, re.I)
        if c["expect"] == "reject":
            ok = {f: False for f in FIELDS}
        else:
            ok = {f: field_ok(f, got[f], c["expect"][f]) for f in FIELDS}
        matches, _ = find_matches(n, providers)
        wrong = [f"{f}={got[f]}" for f in FIELDS if not ok[f]]
        row.update({"result": "parsed", "correct_fields": sum(ok.values()), "all_correct": all(ok.values()),
                    "privacy_ok": privacy_ok, "matches": len(matches), "cost_usd": r.cost_usd,
                    "repaired": r.repaired, "latency_s": r.latency_s, "detail": "; ".join(wrong)[:120],
                    **{f"ok_{f}": ok[f] for f in FIELDS}})
        rows.append(row)
    df = pd.DataFrame(rows)
    valid = df[df.result == "parsed"]
    summary = {
        "model": os.environ.get("CAPSTONE_MODEL", "default"),
        "cases": len(df),
        "field_accuracy": round(df.correct_fields.sum() / (len(df) * len(FIELDS)), 3),
        "records_fully_correct": f"{int(df.all_correct.sum())}/{len(df)}",
        "privacy_violations": int((~df.privacy_ok).sum()),
        "match_rate": round((valid.matches > 0).mean(), 3) if len(valid) else 0,
        "avg_cost_per_request_usd": round(valid.cost_usd.mean(), 5) if len(valid) else 0,
        "cost_per_1000_requests_usd": round(1000 * valid.cost_usd.mean(), 2) if len(valid) else 0,
    }
    return df, summary


if __name__ == "__main__":
    df, summary = run()
    print(df.to_markdown(index=False))
    print(json.dumps(summary, indent=2))
