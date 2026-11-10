# Week 3 Homework: Multi-Provider LLM Pipeline, Evaluation & Hallucination Audit

## What I built

- **Part 1:** one pipeline with retry on API errors that runs three tasks and records latency, token cost and a 1-5
  quality rating: (A) 3-sentence summary of a 1,400-word Wikipedia article ("Head Start (program)"), (B) entity
  extraction to JSON from the "CalWORKs" article, (C) chain-of-thought profit calculation for a family child care home.
  The code supports GPT-4o, Claude Sonnet 4.5 and Llama 3; this run used GPT-4o only (no Anthropic key in Secrets).
- **Part 2:** hallucination audit of GPT-4o at temperature 0 on 20 questions about landmark AI papers (authors, venues,
  volumes, pages, DOIs, benchmark numbers), graded against the original papers, plus a mitigation re-run.
- **Part 3:** four prompt strategies (zero-shot, few-shot with 2 examples, chain-of-thought, role + Pydantic) for a real
  recurring task at USCIC: turning a weekly intake-meeting transcript into decisions and action items.

## Key results

| | Result |
|---|---|
| Part 1 | Extraction 5/5 (valid JSON), reasoning 5/5 (exact numbers), summary 4/5 (added an unsupported statistic) |
| Part 2 | 0/20 hallucinated, 2/20 partially correct, 18/20 correct; the "I don't know" instruction changed nothing |
| Part 3 | Role + Pydantic wins (5/5/5); zero-shot misclassified an action as a decision, CoT dropped a decision |

## Files

| File | Contents |
|---|---|
| `notebook.ipynb` | All code and outputs |
| `analysis.md` | Part 1 model choice, Part 2 hallucination pattern, Part 3 recommendation memo |
| `results/` | All tables from the run (CSV and Markdown) |

## How to run

Open `notebook.ipynb` in Colab, add `OPENAI_API_KEY` (or `UCLA_OPENAI_API_KEY`) and `ANTHROPIC_API_KEY` to Secrets,
Run all. Optional `HF_TOKEN` adds Llama 3.

## What surprised me

- GPT-4o got every "trap" citation detail right (volumes, pages, the CACM DOI), yet inserted "over 1 million children"
  into a summary of an article that says about 820,000. The risk was in the easy-looking task, not the hard one.
- Its stated confidence was 95-100 on every answer, right or partial, so self-reported confidence was useless.
- My own sentence-count rule failed: it split "U.S." into two sentences. Automated checks need testing too.
