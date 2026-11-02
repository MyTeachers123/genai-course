# Week 6 Analysis

> DRAFT. Numbers marked TODO come from the real run in `notebook.ipynb`. Edit the wording so it is your own.

## Part 1: Prompt variations

Task: read a family child care price-list flyer (image) and return JSON for a web price sheet.
Inputs: 5 real flyers from my work. Model: gpt-5.4-mini, images resized to 768 px wide.

| Variation | Avg Correctness | Format Pass Rate | Avg Usefulness | Avg Tokens | Cost/1K calls |
|---|---|---|---|---|---|
| V1 zero-shot | TODO | TODO | TODO | TODO | TODO |
| V2 few-shot | TODO | TODO | TODO | TODO | TODO |
| V3 chain-of-thought | TODO | TODO | TODO | TODO | TODO |
| V4 role + structured | TODO | TODO | TODO | TODO | TODO |
| V5 hybrid | TODO | TODO | TODO | TODO | TODO |

**Winner:** TODO, because TODO.

Notes to check against the results:
- Most tokens in this task are **image tokens**. V2 sends three images (two examples and the flyer),
  so it should cost roughly three times as much as the others. Is the accuracy gain worth it?
- The age conversion ("2 - 4 years" becomes 24 to 59 months) only appears in V3 (as a step), V5 (as a rule)
  and V2 (through examples). V1 and V4 have to guess the convention. Did their age ranges differ?
- Which fields failed most often: names in Chinese, phone language labels, or prices?

## Part 2: Failure analysis (about 200 words)

Worst variation: TODO. Adversarial inputs and results:

| Input | Failure mode | Expected | Actual (worst prompt) |
|---|---|---|---|
| a1: no unit printed | Ambiguous instruction | price_unit null + a question | TODO |
| a2: dim phone photo, address cut off | Missing context | address and phones null | TODO |
| a3: one line "$25/hour" on a monthly sheet | Conflicting constraints | that line's unit = hour | TODO |

Iterations: (1) field list + "never assume monthly": TODO result; (2) "only what you can read, no outside
knowledge": TODO result; (3) line-level units, age rules, schema = V6: TODO result.

Draft paragraph (edit after the run):

The failures share one pattern: when the flyer leaves something out or contradicts itself, the model
fills the gap with the most typical value instead of saying it does not know. With no unit printed it
assumed "monthly"; with the address cut off it TODO; with one hourly line on a monthly sheet it TODO.
These are prompting problems, because each one improved once the prompt said what to do in that
situation (iterations 1-3). A class of inputs my best prompt still struggles with is TODO (for example
low-quality phone photos, where digits like 3 and 8 are misread). No instruction fixes that. It is a
limit of the model's vision at this image size, so it has to be handled outside the prompt:
a larger image, a validator that rejects implausible prices, and a human check before publishing.
Prompting can define behavior for missing or conflicting information; it cannot make unreadable
pixels readable.

### Error analysis: unverifiable license numbers (checked 2026-11-01)

| Flyer | License | CDSS check |
|---|---|---|
| f1 | 198021766 | Verified via a CCLD mirror: Wang Hua Family Child Care, West Covina, capacity 14, licensed 2025-07-25 |
| f2 | 198021713 | Not found |
| f3 | 198401327 | Not found |
| f4 | 304314565 | Not found |
| f5 | 304314798 | Not found |

The CDSS search API returned 503 for every number, the state open data stops at 2025-05-25, and a
third-party mirror confirmed only one license. This is the clearest case of a model limitation rather than
a prompting limitation: the model can read the number on the flyer perfectly, but it has no way to know
whether the license exists, is pending, or was mistyped by the provider. Asking it to "verify" would
only produce a confident guess (hallucination). The fix belongs outside the prompt: look the number up
in code, publish only verified price sheets, and send the rest to a human. The official name can also
differ from the flyer (f1: "Wang Hua Family Child Care" vs the provider's business name), which is
expected, not an error.

## Part 3: LangChain (about 150 words)

Draft paragraph (edit after the run):

Running the winning prompt as a LangChain chain showed problems that raw API calls had hidden. As raw
calls, I only checked that the reply was JSON. With `PydanticOutputParser`, the business rules became part
of parsing: license numbers must have 9 digits, a minimum age cannot be above the maximum, and a price must be
plausible for its unit. The notebook shows three replies that `json.loads` accepts but Pydantic rejects:
"2 years old +" stored as ages 24 to 2, "$3500" misread as 35 per month, and a license number with a missing
digit. JSON parsing would have passed all three and published a wrong price sheet. TODO: say whether this
happened on a real flyer. `OutputFixingParser` sends the error back to the model, so most of these are fixed
automatically. The concrete difference is that LangChain's structured output checks meaning, not only syntax.
