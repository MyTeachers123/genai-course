# Week 7 Homework, Part 3: Memory Strategy Comparison and Recommendation

Same 6-turn conversation for all three strategies: a USCIC case worker describes a mother in Los Angeles County with a
10-month-old and a 4-year-old who works part-time and was denied CalWORKs, asks about food, preschool, infant care and
tax credits, and in turn 6 asks for a 4-bullet action plan "using everything I told you". Same retriever and GPT-4o.

| Strategy | Prompt tokens at turn 6 | Memory tokens at turn 6 | Coherence 1-5 | Key information retained | Key information lost / wrong |
|---|---|---|---|---|---|
| Slot tracking (my first choice) | 747 | 115 | 4 | Both children's ages, CalWORKs ruled out, Head Start / Early Head Start, Child and Dependent Care Credit, SNAP, EITC | No mention of Los Angeles County or part-time work in the plan; **recommends TANF**, which is the program CalWORKs implements in California |
| Full history | 1,040 | 483 | 4 | Both ages, part-time work (used to justify the care credit), SNAP, Head Start for the 4-year-old and Early Head Start for the baby | No mention of county; does not repeat the CalWORKs denial, but correctly does not suggest TANF |
| Summary compression | 721 | 89 | 4 | Part-time work, Head Start / Early Head Start, care credit, SNAP, EITC | Children's ages not used in the plan; **recommends TANF** like slots |

Coherence scores are from a GPT-4o judge; it gave all three 4/5 and did not notice the TANF problem, so I added it after
reading the answers. "WIC" was in my list of facts to check, but no strategy ever mentioned it in any turn, because the
WIC document in the index is a disambiguation page; that is an index gap, not memory loss. Memory tokens grow from 1 to
483 with full history, while slots stay at 42-115 and summaries at 87-103.

## Recommendation (200 words)

For USCIC case-worker conversations I would deploy **slot tracking**, but with one change the test made obvious. Our
conversations are short (5-10 turns), and what must persist is a small, known set of facts: county, children's ages,
work status, and programs already ruled out. Slots kept the most facts (both ages, the denial, five programs) at 115
memory tokens, a quarter of full history, and the cost stays flat as the conversation grows. The structured slot is
also what our intake database stores, so the same object can be saved.

The failure: slots stored "CalWORKs ruled out" but not why, and the model then recommended TANF, which in California is
CalWORKs. Full history avoided this because the original sentence ("denied because her income is slightly over the
limit") was still in the prompt. A slot that loses the reason behind a fact lets the model contradict it.

Fallback: store the reason with each ruled-out program ("CalWORKs: denied, income over limit"), keep the last two turns
verbatim alongside the slots, and add a rule mapping California program names to federal ones (CalWORKs = TANF,
Medi-Cal = Medicaid, CalFresh = SNAP). If a conversation exceeds 10 turns or the slots fail validation, switch to full
history for that session.
