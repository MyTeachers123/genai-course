# Week 7 Homework: Production RAG with Evaluation & Failure Audit

## Domain

US and California family-support programs (child care, cash aid, food, health and tax credits). This is the
knowledge my nonprofit (USCIC) uses when helping multilingual parents understand public programs.

## What I built

- **Knowledge base:** 12+ public Wikipedia articles (CalWORKs, Head Start, CCDBG, TANF, PRWORA, AFDC, Child and
  Dependent Care Credit, WIC, SNAP, EITC, Child Tax Credit, Medi-Cal, ...), chunked (800 characters, 100 overlap),
  embedded with all-MiniLM-L6-v2 and indexed in FAISS.
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
