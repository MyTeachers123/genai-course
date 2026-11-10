# Week 7 Homework, Part 2: Failure Mode Audit

The pipeline answered 19/20 questions correctly according to the judge (all 5 negative and all 5 adversarial questions
passed). The automatic classifier found 2 failures (`results/failure_table.md`). Reading the retrieved chunks shows that
both have a different root cause than the label suggests, and it surfaces one more problem the scores missed.

## Failure classification table

| # | Question | Failure type | Root cause | Proposed fix |
|---|---|---|---|---|
| 6 | What is Medi-Cal? | **A: Retrieval** (coverage) | The Medi-Cal article was never indexed: the Wikipedia API returned HTTP 429 (rate limit) for 4 of 14 titles (Medi-Cal, Child tax credit, Transitional kindergarten, CHIP), and the loader skipped them silently. All 4 retrieved chunks came from CalWORKs. The model's refusal was actually correct for this index. My test-suite check passed because it only looked for the word "medicaid", which appears in other articles. | Retry each download with exponential backoff on 429 and `assert len(DOCS) == len(TITLES)` before building the index; validate each positive question by checking that the full gold answer ("California's Medicaid program") occurs in one chunk, not a single keyword. |
| 7 | Who can receive WIC benefits? | Flagged **C: Format**; actually a measurement error plus **A: Retrieval** (thin document) | The format check split "U.S." into two sentences, so a 3-sentence answer counted as 4: a false positive. The real problem: "WIC" resolved to a 162-word disambiguation page, so the context only says WIC is "the U.S. Special Supplemental Nutrition Program for Women, Infants and Children". The answer restated the name and did not list who is eligible (pregnant, breastfeeding and postpartum women, infants, children under 5). The judge still marked it correct and faithful. | Count sentences with a tokenizer that knows abbreviations (`nltk.sent_tokenize`); fetch the full article title "Special Supplemental Nutrition Program for Women, Infants, and Children"; drop documents under 300 words at ingestion; tighten the judge rubric to require the specific eligibility groups. |

Types B (faithfulness) and D (over-refusal) did not occur in this run: no answer used outside knowledge according to the
faithfulness gate, and the only refusal on a positive question (Q6) was correct given the index.

## Type A example: Q6 "What is Medi-Cal?"

Retrieved chunks (k=4), all from the CalWORKs article:
- "only 9 months of benefits. == Effects == While the long-term effects of CalWORKs..."
- "effects for low-income families as programs in comparable states..."
- "...the Public Policy Institute of California's California Poverty Measure (CPM)..."
- "The California Work Opportunities and Responsibility to Kids (CalWORKs) program is the California welfare implementation..."

Answer: "Not found in the knowledge base. Source: CalWORKs". The first chunk that contains "medicaid" ranks 6th in the
top 20, outside k=4, so the automatic fix "raise k to 6" would not help: that chunk mentions Medicaid but does not
define Medi-Cal. The fix is at ingestion, not at retrieval time.

## Type C example (false positive): Q7 "Who can receive WIC benefits?"

Answer: "WIC benefits are part of the U.S. Special Supplemental Nutrition Program for Women, Infants, and Children. This
program is designed to support women, infants, and children with nutritional assistance. For specific eligibility
criteria, it is best to confirm with the local WIC agency. Source: WIC" - three sentences and a Source line, which
meets the format rule. The problem is content: "designed to support women, infants, and children" is a restatement of
the program name, not an eligibility answer, because the retrieved WIC document is a disambiguation list.

## Problem the scores missed (from Part 3)

In the multi-turn test, the slot and summary strategies recommended TANF to a mother whose CalWORKs application was
denied. CalWORKs is California's TANF program, which is stated in the CalWORKs article, so this is a reasoning error
across documents, not a retrieval error. The coherence judge scored those answers 4/5 and did not catch it.

## Analysis (250 words)

The most common failure type in my pipeline is Type A, and both cases trace back to the ingestion step, not to the
embedding model or k. One document never reached the index because of an HTTP 429 rate limit that the loader logged and
skipped, and one document was a 162-word disambiguation page instead of the real article. The generator behaved well in
both cases: it refused when the index had nothing (Q6) and stayed within its thin context (Q7). This is why the
adversarial and negative questions all passed: the strict system prompt ("use only the context", exact refusal
sentence, correct false premises) works, so the weak point moves upstream to the data.

The second lesson is that my evaluation tools failed more often than the pipeline. The keyword check that validated
the test suite passed a question whose document was missing, the sentence counter misread "U.S.", the judge accepted a
vague WIC answer as correct and faithful, and the coherence judge missed a TANF/CalWORKs contradiction. With 19/20 on
the headline score, these would all have gone unnoticed without reading the retrieved chunks.

The architectural change that would most improve accuracy is a validated ingestion stage: retry with backoff, a
document manifest that must match the index, minimum length and "not a disambiguation page" checks, and a per-question
gold-chunk check before evaluation. After that, a hybrid retriever (BM25 + embeddings) would help acronym-heavy
questions like "Medi-Cal" or "WIC", where short names embed poorly with MiniLM.
