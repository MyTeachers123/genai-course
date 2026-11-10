# Week 7 Homework: Production RAG with Evaluation & Failure Audit

## Domain

US and California family-support programs (child care, cash aid, food, health and tax credits). This is the
knowledge my nonprofit (USCIC) uses when helping multilingual parents understand public programs.

## What I built

- **Knowledge base:** 10 public Wikipedia articles (CalWORKs, Head Start, CCDBG, TANF, PRWORA, AFDC, Child and
  Dependent Care Credit, WIC, SNAP, EITC; 174 chunks of 800 characters with 100 overlap), embedded with
  all-MiniLM-L6-v2 and indexed in FAISS. 14 titles were requested; 4 were skipped after HTTP 429 rate limits.
- **RAG chain:** LangChain retriever (k=4) + GPT-4o with a benefits-navigator system prompt: context only, an exact
  "Not found in the knowledge base." refusal, correct false premises, 3 sentences + Source line, no eligibility decisions.
- **Evaluation:** 20 questions (10 answerable, 5 not answerable, 5 adversarial) scored for retrieval, answer quality,
  faithfulness, correctness and format.
- **Failure audit:** every failure classified as A (retrieval), B (faithfulness), C (format) or D (over-refusal), with
  the retrieved chunks, root cause and a specific fix.
- **Memory:** the same 6-turn case-worker conversation run with slot tracking, full history and summary compression.

## Files

| File | Contents |
|---|---|
| `notebook.ipynb` | Full pipeline and outputs |
| `evaluation_table.md` | 20-question evaluation table |
| `failure_audit.md` | Part 2 failure classification and analysis |
| `memo.md` | Part 3 memory strategy comparison and recommendation |
| `results/` | All tables as CSV/Markdown, including each strategy's conversation |

## Key findings

| | Result |
|---|---|
| 20-question test | 19/20 by the judge (positive 9/10, negative 5/5, adversarial 5/5); 18/20 fully correct after my review |
| Failures | 2, both Type A at the ingestion step: Medi-Cal article never indexed (HTTP 429), WIC indexed as a disambiguation page |
| Evaluation tooling | The sentence counter, the keyword gold check and both LLM judges each missed or invented a failure |
| Memory | Slots: 115 memory tokens, most facts kept; full history: 483 tokens; summary: 89 tokens, lost the children's ages. Slots and summary both recommended TANF after a CalWORKs denial (CalWORKs is California's TANF) |
| Recommendation | Slot tracking, storing the reason with each ruled-out program, plus the last two turns verbatim |
