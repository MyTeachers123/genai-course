"""USCIC affordable child care matching API.

Parent form -> Claude extraction -> encrypted storage -> anonymous requests to same-ZIP providers
-> provider accepts -> parent receives the provider's MyTeachers123.com page link.
"""
from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, ValidationError

from . import crypto
from .db import MatchRequest, Outbox, Parent, init_db, session
from .extract import extract
from .matching import PAGE, find_matches, load_providers
from .schemas import AnonymousRequest, IntakeIn

ROOT = Path(__file__).resolve().parent.parent
PROVIDERS = load_providers(os.environ.get("PROVIDERS_CSV", ROOT / "data" / "providers_sample.csv"))
MAX_REQUESTS = 5

app = FastAPI(title="USCIC Child Care Matching", version="0.1.0")
init_db()


@app.get("/", response_class=HTMLResponse)
def form():
    return (ROOT / "app" / "static" / "form.html").read_text()


@app.post("/api/intake")
def intake(body: IntakeIn):
    try:
        res = extract(body.answer)
    except (ValidationError, ValueError) as e:
        raise HTTPException(422, f"Could not understand the answer: {str(e)[:200]}")
    need = res.need
    matches, reasons = find_matches(need, PROVIDERS)
    with session() as s:
        parent = Parent(email_enc=crypto.encrypt(body.email), phone_enc=crypto.encrypt(body.phone),
                        language=need.language, need=need.model_dump())
        s.add(parent)
        s.flush()
        for m in matches[:MAX_REQUESTS]:
            s.add(MatchRequest(parent_id=parent.id, license=m.provider.license,
                               usual_price=m.usual_price, budget=need.monthly_budget_usd))
        s.commit()
        pid = parent.id
    return {"parent_id": pid, "language": need.language, "requests_sent": min(len(matches), MAX_REQUESTS),
            "excluded": reasons, "llm": {"model": res.model, "cost_usd": res.cost_usd, "repaired": res.repaired}}


@app.get("/api/provider/{license}/requests", response_model=list[AnonymousRequest])
def provider_requests(license: str):
    """What a provider sees: no name, email or phone."""
    with session() as s:
        rows = s.query(MatchRequest).filter_by(license=license, status="pending").all()
        out = []
        for r in rows:
            need = s.get(Parent, r.parent_id).need
            sch = need["schedule"]
            out.append(AnonymousRequest(
                request_id=r.id, zip_code=need["zip_code"], age_groups=need["age_groups"], days=sch["days"],
                hours=f"{sch['start']}-{sch['end']}", monthly_budget_usd=r.budget, usual_price_usd=r.usual_price,
                discount_pct=round(100 * max(0, r.usual_price - r.budget) / r.usual_price, 1)))
        return out


class Response(BaseModel):
    accept: bool


@app.post("/api/requests/{request_id}/respond")
def respond(request_id: int, body: Response):
    with session() as s:
        r = s.get(MatchRequest, request_id)
        if not r or r.status != "pending":
            raise HTTPException(404, "request not found or already answered")
        r.status = "accepted" if body.accept else "declined"
        if body.accept:
            link = PAGE.format(license=r.license)
            s.add(Outbox(parent_id=r.parent_id, body=(
                f"Good news: a licensed daycare near you can accept your budget of ${r.budget}/month. "
                f"See the program and book a visit: {link}")))
        s.commit()
        return {"request_id": request_id, "status": r.status}


@app.get("/api/parent/{parent_id}/messages")
def parent_messages(parent_id: int):
    """Staff view of the messages queued for one parent (contact data stays encrypted)."""
    with session() as s:
        return [{"body": m.body, "created_at": m.created_at.isoformat()}
                for m in s.query(Outbox).filter_by(parent_id=parent_id).all()]
