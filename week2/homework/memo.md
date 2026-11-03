# Memo: Can "AI Background Generation" Ship at 1 Second on 2x A10G?

**To:** Product and Engineering
**From:** <your name>, ML Engineering
**Date:** <date>
**Re:** Latency plan for real-time 512x512 background generation (6-week timeline)

<!-- Target length: 500-700 words. Delete every comment line before submitting. -->

## 1. Summary

<!-- 2-3 sentences: Can standard DDPM meet the target? (No.) What do you recommend? -->

## 2. Why standard DDPM (1,000 steps) cannot meet 1 second

<!-- Show the math. Suggested structure:
     - Measured in Lab 2 (my notebook): 28x28 MNIST U-Net, DDPM-1000 = 444 ms per image at batch 100.
     - At 512x512 (latent 64x64, SD-1.5 class U-Net) on one A10G: assume X ms per denoising step
       (state your source / assumption, include CFG = 2 forward passes).
     - 1,000 steps x X ms = ? seconds.
     - Why a second GPU does not help: steps are sequential (step t needs the output of step t+1).
       Best case with 2 GPUs is still ? seconds, i.e. ?x over budget.
     - Latency budget: 1,000 ms - text encoding - VAE decode - network = ? ms left for the U-Net,
       so the maximum step count is about ?. -->

| Component | Time (ms) |
|---|---|
| Text encoder | |
| U-Net, N steps x ms/step | |
| VAE decode | |
| Network + queueing | |
| **Total** | |

## 3. Option A: <technique name>

<!-- Technique, expected latency (with the math), expected quality cost (FID delta if known),
     implementation complexity (hours, broken down). -->

## 4. Option B: <technique name>

<!-- Same four items as Option A. -->

## 5. Recommendation

<!-- Primary = ?, Fallback = ?. Tie the reasoning to the 6-week timeline:
     what can be integrated, load-tested and shipped in 6 weeks without a research project.
     Include a rough week-by-week plan. -->

## 6. Quality risk and user-facing mitigation

<!-- One risk (e.g., few-step models lose diversity / produce artifacts, FID > 30 on our data,
     prompt changes cause the background to "jump"). One mitigation (UX pattern, quality gate, or fallback). -->

## 7. Assumptions and sources

<!-- List the numbers you assumed and where they came from. -->
