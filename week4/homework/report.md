# Week 4 Homework, Part 3: Comparative Evaluation Report

## Setup

Five prompts, each chosen to stress one skill: text rendering (P1 "OPEN SEATS" sign), counting (P2 three apples and two
pears), spatial relations (P3 blue cup left of yellow bowl), style (P4 watercolor reading nook) and photorealistic scene
(P5 single-story house with backyard playground).

| Config | What ran |
|---|---|
| A | SDXL base 1.0, DPM++ 2M, 30 steps, guidance 7.5, seed 42 |
| B | Same + Canny ControlNet (scale 0.7) on a simple layout sketch drawn for each prompt |
| C | Planned: DALL-E 3. Both OpenAI image calls returned HTTP 400 (`response_format` no longer accepted by `dall-e-3`; `gpt-image-1` not available to the account), so the notebook used the assignment's fallback, **SDXL Turbo at 4 steps** |

Metrics: CLIP score (openai/clip-vit-base-patch32, 100 x cosine), LPIPS (AlexNet) against the highest-CLIP image for the
same prompt (0 = that image), and a 1-5 rating. Ratings were first produced by GPT-4o vision with a strict rubric; I then
checked every image and changed three (marked *).

## Evaluation table

| Config | Prompt | CLIP | LPIPS vs best | Rating 1-5 | Notes |
|---|---|---|---|---|---|
| A | P1 storefront "OPEN SEATS" | 32.54 | 0.600 | 2 | Sign reads "Open S Seatss" |
| B | P1 | 32.91 | 0.000 | 5 | Sign reads "OPEN SEATS" correctly; clean storefront |
| C | P1 | 31.03 | 0.729 | 2 | Sign reads "OPEN ATE" |
| A | P2 3 apples + 2 pears | 34.37 | 0.000 | 2 | Seven pears and four apples in a bowl |
| B | P2 | 32.38 | 0.657 | 2 | Two red apples, three green apples, two pears |
| C | P2 | 31.54 | 0.806 | 2 | One red and two green apples, no pears |
| A | P3 blue cup left of yellow bowl | 35.45 | 0.000 | 2 | Blue bowl, yellow bowl and yellow cup; cup is the wrong colour |
| B | P3 | 33.81 | 0.405 | 2 | Blue bowl and a blue/yellow bowl, no cup |
| C | P3 | 34.36 | 0.587 | 1* | One blue-and-yellow bowl only (judge: 2) |
| A | P4 watercolor reading nook | 40.18 | 0.000 | 3 | Lovely watercolor, but a sofa instead of a beanbag |
| B | P4 | 36.35 | 0.561 | 5 | Beanbag and bookshelf, watercolor, matches the prompt |
| C | P4 | 36.50 | 0.611 | 3 | Armchair instead of a beanbag |
| A | P5 house + backyard playground | 32.00 | 0.719 | 3* | Modern single-story house and fence, but no playground (judge: 5) |
| B | P5 | 31.18 | 0.776 | 3 | House and fence, no playground |
| C | P5 | 34.22 | 0.000 | 4* | Fence, slide and climbing frame at golden hour; the house is raised like a treehouse (judge: 3) |

| Config | Mean CLIP | Mean LPIPS vs best | Mean rating (reviewed) | Mean rating (GPT-4o judge) |
|---|---|---|---|---|
| A SDXL 30 steps | **34.91** | **0.26** | 2.4 | 2.8 |
| B SDXL + ControlNet | 33.33 | 0.48 | **3.4** | 3.4 |
| C SDXL Turbo 4 steps | 33.53 | 0.55 | 2.4 | 2.4 |

## Report

**Which configuration performed best?** It depends on the metric, and the disagreement is the main finding. Config A
(full SDXL) had the highest mean CLIP score (34.91) and was the reference image for three of five prompts, so it is the
best at putting the requested concepts into the picture. But Config B (SDXL + ControlNet) had the best ratings (3.4 vs
2.4) because it produced the only two images that fully followed their prompts: the only correctly spelled "OPEN SEATS"
sign, and the only reading nook with an actual beanbag. The layout sketch gave the model a fixed box for the sign and a
round shape for the beanbag, and the model filled them correctly. CLIP did not reward this: B's correct sign scored 32.91,
almost the same as A's misspelled one (32.54). CLIP checks that "storefront", "sign" and "open" are present, not that the
letters are right.

**Where every configuration failed.** Counting (P2) and spatial relations (P3) failed in all 15 attempts that targeted
them: no image had exactly three apples and two pears, and no image had a blue cup to the left of a yellow bowl. ControlNet
did not fix this, because my sketch only fixed shapes, not colours or object identity. These are compositional skills
that come from the text encoder and training data, not from the sampler or the number of steps.

**Config A vs Config C.** Config A beat SDXL Turbo on CLIP for P2, P3 and P4 (P4 by 3.7 points) and on rating for P2,
P3 and P4. Turbo won P5 (CLIP 34.22 vs 32.00, and the only image with a playground) while using only 4 denoising steps
instead of 30. So a 4-step distilled model is competitive on simple, common scenes and loses on detail, text
and prompts with several constraints.

**Open weights vs closed APIs.** I could not test that comparison directly, because the closed API calls failed, so both
A and C are open-weights models. What this run does show is that, for an open-weights model, the controllable parts of
the pipeline matter more than model size or step count: a cheap layout sketch plus ControlNet fixed text rendering, which
is usually given as the main reason to pay for a closed API. Closed models are generally reported to be stronger at
counting, spatial relations and spelling without extra conditioning, and my P2/P3 failures are exactly where I would
expect DALL-E 3 or a newer OpenAI image model to win. For a product like my capstone flyers, where layout is known in
advance, open weights + ControlNet is competitive and runs locally; for free-form prompts with counts and text, a closed
API would likely be worth the cost. Re-running Config C with the current OpenAI image API is the next step to confirm it.
