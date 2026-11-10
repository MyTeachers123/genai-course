# Week 3 Homework: Analysis

**Run note.** The notebook ran end to end on GPT-4o (`gpt-4o`, 2026-11-09). No Anthropic key or Hugging Face token was
set in Colab Secrets, so Claude Sonnet 4.5 and Llama 3 did not run. Part 1 therefore has one provider; the code already
supports Claude and Llama (`MODELS` list) and only needs `ANTHROPIC_API_KEY` to add the second column.

## Part 1: Multi-task pipeline

| Task | Model | Latency (s) | Cost ($) | Quality 1-5 | Rule check | Key observation |
|---|---|---|---|---|---|---|
| A. 3-sentence summary of "Head Start (program)" (1,400 words) | GPT-4o | 1.94 | 0.0055 | 4 | 3 sentences (the checker counted 4 because it split on "U.S.") | Covered founding, growth and governance, but added "over 1 million children annually"; the article says about 820,000 in 2023 |
| B. Entity extraction from "CalWORKs" | GPT-4o | 2.75 | 0.0046 | 5 | valid JSON | 6 organisations, 2 dates, 5 correct claims; correctly returned an empty `people` list |
| C. Chain-of-thought child care budget case | GPT-4o | 5.72 | 0.0073 | 5 | numbers correct | Profit $6,696 -> $6,996 (+$300), every step shown |

Cost uses $2.50 / $10.00 per 1M input / output tokens. Quality is a rubric-based GPT-4o judge score that I reviewed.

**Model choice (analysis, 200 words).** On this run GPT-4o was strong on the two tasks where the answer can be checked
mechanically: extraction (valid JSON, nothing invented) and arithmetic reasoning (exact numbers). It was weakest on the
open-ended task: the summary was fluent and the right length but added a statistic from its own training ("over 1 million
children") instead of the article's 820,000. That pattern decides model selection more than raw quality: for extraction
and calculation I would pick the cheaper, faster model that passes the schema and number checks, because the checks catch
its mistakes. For summarisation of policy text that families will read, I would pick the model with the best faithfulness
record and add a faithfulness check, even if it is slower. So yes, I would mix models in one pipeline: a fast model for
extraction and routing, a stronger long-context model for summaries, with validators between steps. The planned second
provider (Claude Sonnet 4.5, $3/$15 per 1M) costs 20% more per input token and 50% more per output token than GPT-4o; it is worth
it only if it removes the unsupported-claim problem in Task A, which is what the second run will test.

## Part 2: Hallucination audit (GPT-4o, temperature 0)

Domain: history of AI research (authors, venues, volumes, pages, DOIs, benchmark numbers); 20 questions with answers from
the original papers. Full table: `results/part2_audit.md`.

| Grade | Judge (Claude unavailable, GPT-4o graded) | After my review |
|---|---|---|
| Hallucinated | 0/20 | 0/20 |
| Partially correct | 3/20 | 2/20 |
| Correct | 17/20 | 18/20 |

Taxonomy: fabricated citation 0, wrong statistic 0, plausible-but-incorrect 0, confident uncertainty avoidance 0.
My review changed Q13 (largest GPT-2: "1.5 billion") from partial to correct: 1.5B is the standard rounding of 1,542M.
Remaining partials: Q15 (Turing 1950: right journal, volume and pages, missing issue 236) and Q20 (latent diffusion:
right authors and title, said "arXiv preprint, 2022" instead of CVPR 2022; the arXiv version is from 2021).

**Mitigation.** With fewer than 3 hallucinations, the experiment used the 3 highest-confidence partial answers (Q13,
Q15, Q20, confidence 95-100). Adding "If you are not certain, say I don't know" changed nothing: the same answers, the
same omissions, and the model never said "I don't know".

**Analysis (200 words).** The pattern is about how famous the fact is, not how hard it looks. Every question was about a
landmark paper that appears thousands of times in the training data, and GPT-4o got even "trap" fields right: Nature 323
pp. 533-536, Neural Computation 9(8) 1735-1780, JMLR 15 1929-1958, and the CACM DOI 10.1145/3065386. Its only errors were
omissions at the edge of a citation (an issue number, the venue of a paper whose arXiv version is better known), and it
stated them with the same 95-100 confidence as correct answers, so self-reported confidence carried no signal. The
uncertainty instruction did not help because the model was not uncertain. The failures I did see elsewhere were of a
different kind: in Lab 3 it described the provisions of a treaty that does not exist, and in Task A it inserted a number
not in the article. The risk for deployment is therefore not well-known facts but long-tail and false-premise questions,
and summaries where training knowledge leaks into the output. For my domain (California child care rules, which change
yearly and are rarely written about) I would expect much higher error rates, so I would ground answers in retrieved
documents and check every number against the source.

## Part 3: Recommendation memo

Task: turn the weekly USCIC intake-meeting transcript into decisions and action items for the team chat. Same transcript
for all versions, GPT-4o.

| Version | Correctness | Format | Usefulness | Tokens | Notes |
|---|---|---|---|---|---|
| V1 zero-shot | 4 | 4 | 4 | 447 | Listed an action ("Fix the Spanish form") as a decision; "Due by Wednesday" breaks the requested format |
| V2 few-shot (2 examples) | 4 | 5 | 4 | 579 | Exact format copied from the examples; the summary got vaguer ("issues noted") |
| V3 chain-of-thought | 3 | 3 | 3 | 615 | Reasoning correct, but the final output dropped the Vietnamese decision (filed as an open question) and the reasoning must be cut before pasting |
| V4 role + Pydantic | 5 | 5 | 5 | 711 | All 2 decisions and 4 actions with owners and dates; kept details ("four licensed homes in 91770 and 91776"); validation passed |

First-pass scores came from a GPT-4o judge; I lowered V1 (judge 5/5/5) and V3 (judge 4/4/4) after reading the outputs.

**Memo (300 words).** I recommend Version 4, the role prompt with a Pydantic schema, for our weekly meeting notes. It was
the only version that was complete, correctly classified and in the exact format on the first try, and because the output
is validated JSON, a missing owner or due date is caught by code rather than by a colleague reading the chat. The extra
cost is small: 711 tokens versus 447 for zero-shot, well under one cent per meeting.

The other strategies each failed in a specific, repeatable way. Zero-shot (V1) looked good at a glance and the judge gave
it full marks, but it put an action item ("fix the Spanish form") in the Decisions list and wrote "Due by Wednesday"
instead of the requested "Owner - task - due date". In a weekly note those slips make the decision list unreliable,
which is the part the board reads. Few-shot (V2) fixed the format perfectly, which shows examples are the cheapest way to
teach layout, but it imitated the short example summaries so closely that the summary lost information (it said "issues
noted" instead of naming them). Chain-of-thought (V3) reasoned correctly in its scratch work, but then treated "we decide
about Vietnamese after October" as an open question and dropped it from Decisions, and its output includes a Reasoning
section that someone must delete before posting. CoT helps when the task needs calculation; for extraction it adds tokens
and a second place for the answer to diverge.

Deployment plan: V4 as the default, with one few-shot example added to the system prompt to anchor the summary length,
and a validator rule that every action item has an owner from the attendee list and a due date. If validation fails,
re-ask once with the error message (the OutputFixingParser pattern from Week 6) before a human reviews it.
