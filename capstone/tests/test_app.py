import os

os.environ["CAPSTONE_LLM"] = "mock"
os.environ["DATABASE_URL"] = "sqlite:///./test_capstone.db"

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app import crypto
from app.db import Base, engine
from app.main import PROVIDERS, app
from app.matching import find_matches
from app.schemas import CareNeed

Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
client = TestClient(app)


def need(**kw):
    base = dict(language="English", zip_code="91770", monthly_budget_usd=1300, age_groups=["infant"],
                schedule={"days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "start": "08:00", "end": "17:00"})
    base.update(kw)
    return CareNeed(**base)


def test_validators_reject_bad_values():
    with pytest.raises(ValidationError):
        need(zip_code="10001")
    with pytest.raises(ValidationError):
        need(monthly_budget_usd=0)
    with pytest.raises(ValidationError):
        need(schedule={"days": ["Mon"], "start": "17:00", "end": "08:00"})
    with pytest.raises(ValidationError):
        need(notes="call 626-555-0142")


def test_hours_per_week():
    assert need().schedule.hours_per_week == 45.0


def test_matching_same_zip_seat_hours_discount():
    matches, reasons = find_matches(need(), PROVIDERS)
    licenses = [m.provider.license for m in matches]
    assert licenses == ["197000003", "197000001"]          # 13.3% and 18.8% discount, smallest first
    assert reasons["no_seat"] == 1                           # Little Oak has no infant seat
    assert reasons["other_zip"] == 5


def test_discount_limit():
    matches, reasons = find_matches(need(monthly_budget_usd=500), PROVIDERS)
    assert matches == [] and reasons["discount_too_big"] == 2


def test_encryption_roundtrip():
    token = crypto.encrypt("parent@example.com")
    assert "parent" not in token and crypto.decrypt(token) == "parent@example.com"


def test_full_flow_provider_never_sees_contact():
    r = client.post("/api/intake", json={"email": "parent@example.com", "phone": "(626) 555-0142",
                                          "answer": "I live in 91770. My son is 10 months old. 8:00 to 17:00. I can pay $1,300 a month."})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["requests_sent"] == 2
    reqs = client.get("/api/provider/197000003/requests").json()
    assert len(reqs) == 1
    text = str(reqs)
    assert "example.com" not in text and "555" not in text
    assert reqs[0]["discount_pct"] == 13.3
    ok = client.post(f"/api/requests/{reqs[0]['request_id']}/respond", json={"accept": True})
    assert ok.json()["status"] == "accepted"
    msgs = client.get(f"/api/parent/{body['parent_id']}/messages").json()
    assert "https://MyTeachers123.com/197000003" in msgs[0]["body"]


def test_bad_phone_rejected():
    r = client.post("/api/intake", json={"email": "a@b.co", "phone": "123", "answer": "ZIP 91770 baby 10 months $1300"})
    assert r.status_code == 422
