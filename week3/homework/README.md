# Week 3 Homework: Multi-Provider LLM Pipeline, Evaluation & Hallucination Audit

## What I built

- **Part 1:** one pipeline that runs three tasks on GPT-4o and Claude Sonnet 4.5 (and Llama 3.1 8B when a
  Hugging Face token is set), with retry on API errors, latency, token cost and a 1-5 quality rating per run.
  - Task A: summarise a 1,000+ word article (Wikipedia, "Head Start (program)") in exactly 3 sentences.
  - Task B: extract people, organisations, dates and key claims from the "CalWORKs" article as JSON.
  - Task C: chain-of-thought business case for a family child care home (profit before/after swapping a toddler
    seat for an infant seat), with a known correct answer.
- **Part 2:** hallucination audit of GPT-4o at temperature 0 on 20 questions about the history of AI research
  (authors, venues, volumes, pages, DOIs, benchmark numbers), graded against the original papers, plus a
  mitigation re-run with "If you are not certain, say I don't know".
- **Part 3:** four prompt strategies (zero-shot, few-shot with 2 examples, chain-of-thought, role + Pydantic) for a
  real recurring task at my nonprofit: turning a weekly intake-meeting transcript into decisions and action items.

## Files

| File | Contents |
|---|---|
| `notebook.ipynb` | All code and outputs |
| `analysis.md` | Part 1 model choice, Part 2 hallucination pattern, Part 3 recommendation memo |
| `results/` | Tables from the run (CSV and Markdown) |

## How to run

Open `notebook.ipynb` in Colab, add `OPENAI_API_KEY` (or `UCLA_OPENAI_API_KEY`) and `ANTHROPIC_API_KEY` to
Secrets, Run all. Optional `HF_TOKEN` adds Llama 3.

## What surprised me

See `analysis.md`.
