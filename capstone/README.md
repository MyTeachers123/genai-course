# Capstone: Affordable Child Care Matching for USCIC

Many low-income families in California are denied or wait-listed for subsidized child care (including CalWORKs child
care) but still cannot pay market rates, while many licensed family child care homes have empty seats. This project
is the intake form, database and matching service for **USCIC** (uscic.us), a nonprofit serving multilingual families.

## How it works

1. **Parent form** (`/`): the parent writes their needs in any language, plus email and phone.
2. **Extraction with Claude**: LangChain `ChatAnthropic` + `PydanticOutputParser` turns the answer into a validated
   `CareNeed` record (language, ZIP, monthly budget, children's age groups, days and hours). If the output does not
   parse, `OutputFixingParser` makes one repair call. Field validators reject bad values (non-California ZIP, end
   time before start, contact details in notes).
3. **Privacy**: email and phone are encrypted with Fernet before storage and are never shown to providers.
4. **Rule-based matching** (`app/matching.py`): same ZIP, an open seat for every child's age group, days and hours
   covered, and a discount of at most 40% from the provider's usual price.
5. **Anonymous request**: each matched provider sees only ZIP, age groups, schedule, budget and the discount asked.
6. **Provider says yes**: the parent receives a link to the provider's page, `https://MyTeachers123.com/<license>`,
   and contacts the provider directly to book a visit.

```
parent answer ──> Claude + Pydantic ──> CareNeed ──> rule-based match ──> anonymous requests
                                  │                                          │ provider accepts
                         encrypted contact ───────────────────────────> link to MyTeachers123.com page
```

## Files

| Path | Contents |
|---|---|
| `app/schemas.py` | Pydantic models and validators (`CareNeed`, `IntakeIn`, `AnonymousRequest`) |
| `app/extract.py` | Claude extraction chain with repair, token and cost tracking |
| `app/matching.py` | Matching rules and provider loader |
| `app/db.py`, `app/crypto.py` | SQLAlchemy models (SQLite or Postgres), field encryption |
| `app/main.py`, `app/static/form.html` | FastAPI service and parent form |
| `data/providers_sample.csv` | Sample providers with fictional license numbers (replace with real openings) |
| `eval/cases.json`, `eval/run_eval.py` | 12 multilingual test answers with expected records; metrics script |
| `evaluation.ipynb` | Colab notebook comparing a rule-based baseline, Claude Sonnet 4.5, Claude Haiku 4.5 and GPT-4o |
| `tests/test_app.py` | Unit and end-to-end tests (offline, mock extractor) |

## Run

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=...            # or CAPSTONE_LLM=openai with OPENAI_API_KEY
export USCIC_FERNET_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
uvicorn app.main:app --reload           # open http://127.0.0.1:8000
CAPSTONE_LLM=mock pytest -q             # tests, no API key needed
```

## Evaluation

Metrics from the pitch: extraction accuracy, match rate, cost per request (plus privacy violations).
Run `evaluation.ipynb` in Colab; results are written to `eval/results.md`.

| Config | Field accuracy | Fully correct records | Privacy violations | Match rate | Cost / 1,000 requests |
|---|---|---|---|---|---|
| Rule-based baseline (no LLM) | 0.75 | 4/12 | 0 | 0.60 | $0 |
| Claude / GPT-4o | see `eval/results.md` | | | | |

The baseline only understands English and Spanish keywords and fixed time formats; it fails on Vietnamese, Korean
and Tagalog answers, weekly or hourly budgets, and "mornings" or "full day". That gap is the reason to use an LLM.

## Limits and next steps

- Provider openings are sample data; production would read openings that providers confirm on MyTeachers123.com.
- Messages are queued in an `outbox` table; email/SMS delivery and provider login are not built yet.
- Matching does not yet consider distance between nearby ZIP codes or license capacity rules by age.
