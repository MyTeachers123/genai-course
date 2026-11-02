# Week 6 Analysis

All numbers come from `notebook.ipynb`, run on 2026-11-02 with gpt-5.4-mini (images resized to 768 px wide).

## Part 1: Prompt variations

Task: read a family child care price-list flyer (image) and return JSON for a web price sheet.
Inputs: 5 real flyers from my work.

| Variation | Avg Correctness | Format Pass Rate | Avg Usefulness | Avg Tokens | Cost/1K calls |
|---|---|---|---|---|---|
| V1 zero-shot | 1.0 | 0% | 1 | 1,207 | $1.91 |
| V2 few-shot | 4.8 | 100% | 4 | 3,473 | $3.53 |
| V3 chain-of-thought | 1.0 | 0% | 1 | 1,309 | $1.81 |
| V4 role + structured | 4.4 | 100% | 3 | 1,788 | $2.15 |
| V5 hybrid | 4.8 | 100% | 5 | 2,288 | $2.54 |

Usefulness (1-5) is my own judgment of whether I could build the web price sheet from the reply without editing it: V1 = 1 (invented field names, every reply would need rewriting), V2 = 4 (correct, but three images per call make it the most expensive), V3 = 1 (wrong unit value on every flyer), V4 = 3 (right shape, but some ages and names needed manual fixes), V5 = 5 (I could generate the page directly from the JSON).

**Winner: V5 hybrid**, because it ties V2 for the best correctness (4.8, 100% format) at 28% lower cost
($2.54 vs $3.53 per 1K calls), since it teaches the format with written rules instead of two extra images.

Observations:
- **Format is the dividing line.** V1 and V3 read the flyers but never matched my schema (0% format pass).
  V1 invented its own field names (e.g. `business_name` instead of `program_name`). V3 used the right
  fields but wrote a `price_unit` value outside the allowed `month / week / day / hour`, which fails on every flyer.
  Everything that showed the schema or examples (V2, V4, V5) passed 100%.
- **Rules beat a bare schema for meaning.** V4 had the schema but no rules and scored 4.4; V5 added explicit
  rules (age conversion to months, line-level units, nulls) and scored 4.8. The schema fixes the shape;
  the rules fix what the values mean.
- **Image tokens dominate cost.** Text is only 19-1,147 tokens per call; the rest is about 1,100 image
  tokens per flyer. V2 sends three images, so it is the most expensive even though its text is short.

## Part 2: Failure analysis

Worst variation: **V1 zero-shot**. Adversarial inputs (real flyers edited to target one failure mode):

| Input | Targeted failure mode | Expected | V1 (original) | V6 (after iteration 3) |
|---|---|---|---|---|
| a1: "(monthly)" removed | Ambiguous instruction | `price_unit` null + a question | no valid JSON (1) | unit handled correctly, but `program_name_alt` = "MyTeachers123.com" (5) |
| a2: dim, blurred phone photo, address cut off | Ambiguous instruction (no rule for unreadable text) | address/phones null | no valid JSON (1) | `program_name` = "MyTeachers123.com", second name missed (4) |
| a3: one line "$25/hour" on a monthly sheet | Conflicting constraints | that line's unit = hour | no valid JSON (1) | matches (5) |

Iterations on V1 (average correctness / format pass on the adversarial set; original set in brackets):

| Version | Change | Correctness | Format |
|---|---|---|---|
| original | - | 1.00 (1.0) | 0% (0%) |
| iteration 1 | field list + "never assume monthly" | 1.00 (1.0) | 0% (0%) |
| iteration 2 | + "only what you can read, no outside knowledge" | 1.00 (1.0) | 0% (0%) |
| iteration 3 = V6 | + line-level units, age rules, phone format, exact JSON schema | 4.67 (4.6) | 100% (100%) |

Failure classification, using the five failure modes from the lecture (ambiguous instruction, missing
output format, context window overflow, tone drift in multi-turn, conflicting constraints):

- Every V1 failure, on all 8 inputs, was **missing output format**: valid content in the wrong shape
  (invented field names, unit values outside the schema). The targeted modes only became visible once the
  format was fixed.
- a1 (no unit printed) and a2 (unreadable photo) are **ambiguous instruction**: the prompt did not say what
  to do when information is missing or unreadable. a3 (hourly line on a monthly sheet) is **conflicting
  constraints**: one unit for the sheet vs. what the line prints.
- V6's new error (the **MyTeachers123.com** header taken as the program name) is also an **ambiguous
  instruction**: the prompt never said which text is the program name.
- Context window overflow and tone drift do not apply: each call is a single image in a single turn.
- The unverifiable license numbers fit none of the five: they are a model/knowledge limitation, not a
  prompt failure.

**Analysis (about 200 words).** The clearest pattern is that format failures hide every other failure.
Iterations 1 and 2 added exactly the semantic rules the adversarial flyers target, yet scores did not move,
because the model still invented field names and values; only iteration 3, which supplied the exact
schema, jumped from 1.0 to 4.67. Once the format was fixed, the semantic rules worked: V6 handled the
missing "(monthly)" and kept "$25/hour" as an hourly line on a monthly sheet. The class of inputs my best
prompt still struggles with is low-quality photos: on the blurred, cropped flyer the model grabbed the most
prominent readable text, our own MyTeachers123.com header, as the program name. Part of this is a prompting
limitation, fixable with one rule ("ignore the MyTeachers123.com header"). Part is a model limitation: when
the real name is too blurry to read, no instruction can make it readable, and the result is a confident
wrong answer. The license check shows the same boundary from another side: the model read all five numbers
correctly, but only one could be confirmed with CDSS, and no prompt can tell whether a printed license is
real. Those checks belong in code and in human review, not in the prompt.

### Error analysis: unverifiable license numbers (checked 2026-11-01)

| Flyer | License | CDSS check |
|---|---|---|
| f1 | 198021766 | Verified via a CCLD mirror: Wang Hua Family Child Care, West Covina, capacity 14, licensed 2025-07-25 |
| f2 | 198021713 | Not found |
| f3 | 198401327 | Not found |
| f4 | 304314565 | Not found |
| f5 | 304314798 | Not found |

The CDSS search API returned 503 for every number, the state open data stops at 2025-05-25, and a
third-party mirror confirmed only one license. This is a model limitation rather than a prompting
limitation: the model reads the number on the flyer correctly, but it has no way to know whether the
license exists, is pending, or was mistyped by the provider. Asking it to "verify" would only produce a
confident guess. The fix belongs outside the prompt: look the number up in code, publish only verified
price sheets, and send the rest to a human. The official name can also differ from the flyer (f1: "Wang Hua
Family Child Care" vs the provider's business name), which is expected, not an error.

## Part 3: LangChain

The chain (PromptTemplate + ChatOpenAI + PydanticOutputParser + OutputFixingParser, prompt = V5) produced a
valid `WebPriceSheet` for all 5 flyers, each scoring 5/5 against my expected answers, and generated 5 HTML
price sheets with QR codes.

**Analysis (about 150 words).** The LangChain version made the rules part of parsing instead of something I
checked by eye. As raw API calls, V5 averaged 4.8; inside the chain it scored 5 on every flyer, because the
parser's format instructions are stricter and a reply that fails validation is sent back with the error by
`OutputFixingParser` instead of being kept. A real case where Pydantic caught what JSON parsing would pass
came from Part 1: V3 returned valid JSON, but its `price_unit` value was not one of `month / week / day / hour`;
`json.loads` accepted it, while the `Literal` field rejected it on every flyer. With only JSON parsing, the
web page would have received a unit it cannot display. The notebook also shows three constructed replies
that `json.loads` accepts but my validators reject: ages "24 to 2" months, "$3500" misread as $35 per month,
and a license number with a missing digit. The concrete difference is that structured output checks
meaning, not only syntax.
