# Memo: Can "AI Background Generation" Ship at 1 Second on 2x A10G?

**To:** Product and Engineering
**From:** ML Engineering
**Re:** Latency plan for real-time 512x512 background generation (6-week timeline)

## 1. Summary

Standard DDPM with 1,000 steps cannot meet the 1-second target on 2x A10G; it misses by roughly 80x. Plain step-skipping (DDIM) is not enough either. I recommend a distilled few-step model: **SD-Turbo** as primary (1-4 steps, ~0.3-0.5 s end to end) and **LCM-LoRA on SD-1.5** as fallback (4 steps, ~0.4-0.6 s). Both use existing open weights, so this is integration work, not research.

## 2. Why standard DDPM cannot meet 1 second

A 512x512 image is generated in a 64x64 latent space by an SD-1.5-class U-Net (~860M parameters). Benchmarks show ~31 steps/s on an A100 with classifier-free guidance (CFG); an A10G has about a third of that fp16 throughput. I assume **~80 ms per step** on one A10G.

- 1,000 steps x 80 ms = **80 s per image**.
- A second GPU does not help a single request: step t needs the output of step t+1, so steps are sequential. Two GPUs double throughput, not latency; even a perfect split gives 40 s.
- Budget: 1,000 ms - text encoder (~10 ms) - VAE decode (~80 ms) - network/queueing (~100 ms) = **~800 ms for the U-Net, i.e. at most ~10 steps at 80 ms.**

Fewer steps alone are not the answer: in my Lab 2, DDIM held quality at 50 steps (FID 21.1 vs 16.5 for DDPM) but collapsed at 5 steps (FID 73.1). Under ~10 steps we need a model distilled for few-step sampling.

| Component | Standard DDPM (ms) | SD-Turbo, 4 steps (ms) |
|---|---|---|
| Text encoder | 10 | 10 |
| U-Net | 1,000 x 80 = 80,000 | 4 x 40 = 160 |
| VAE decode | 80 | 80 |
| Network + queueing | 100 | 100 |
| **Total** | **~80,200** | **~350** |

## 3. Option A: SD-Turbo (Adversarial Diffusion Distillation)

- **Technique:** a model distilled from Stable Diffusion to sample in 1-4 steps at native 512x512. It does not use CFG, so each step is one forward pass (~40 ms).
- **Expected latency:** 1 step ~0.25 s, 4 steps ~0.35 s end to end; ~6 images/s across both GPUs.
- **Quality cost:** published results show 1-4 step quality close to the 50-step teacher, but there is no FID on our data yet; expect a few FID points of loss and lower diversity. Must be measured on our eval set against the FID < 30 bar before launch.
- **Complexity:** ~60 hours (integration 16, TensorRT optimisation 16, 2-GPU serving 16, FID harness 12).
- **Risk:** license is Stability's community license; commercial use requires accepting Stability membership terms. Legal must sign off in week 1.

## 4. Option B: LCM-LoRA on SD-1.5 (Latent Consistency distillation)

- **Technique:** a small LoRA adapter that turns SD-1.5 into a 4-6 step sampler; guidance 1-2 (effectively no CFG cost).
- **Expected latency:** 4 x ~45 ms + overhead = ~0.4 s; 6 steps ~0.5 s.
- **Quality cost:** authors report 4-6 steps as satisfactory, 1 step lacks texture, 8 steps look over-saturated. Typically softer detail than SD-Turbo; FID delta must be measured.
- **Complexity:** ~50 hours; same serving work as Option A, simpler model swap. SD-1.5 base weights are OpenRAIL-M (commercial use allowed); confirm the adapter license.

## 5. Recommendation

**Primary: SD-Turbo. Fallback: LCM-LoRA.** SD-Turbo leaves the most headroom under 1 s (~0.35 s), absorbing network spikes and serving more users per GPU. LCM-LoRA is the fallback if legal blocks the license or SD-Turbo misses FID < 30; it shares most of the serving code, so switching costs about a week. Training our own distilled model is research and out of scope for 6 weeks.

Plan: week 1 license review + baseline FID harness; weeks 2-3 SD-Turbo integration and optimisation; week 4 load test on 2x A10G; week 5 quality gate and UX; week 6 staged rollout. LCM-LoRA is prototyped in parallel in week 2.

## 6. Quality risk and user-facing mitigation

**Risk:** few-step models are less diverse and can produce flat, over-saturated or artefact-heavy backgrounds. My homework showed the same failure: at guidance w = 15, the share of saturated pixels jumped from 67% to 77% and garments turned into flat white shapes. Also, regenerating on every keystroke makes the background "jump".

**Mitigation:** generate 300 ms after the user stops typing, keep the previous image until the new one passes an automatic saturation and safety check, offer a "Regenerate" button, and track FID weekly on 1,000 fixed prompts with an alert above 30.

## 7. Assumptions and sources

- ~80 ms/step for SD-1.5 512x512 with CFG on A10G: estimated from fal-ai benchmarks (A100, ~31 it/s) and A10G reports (~7 it/s, SD 2.1, 768x768).
- SD-Turbo: Stability AI model card (1-4 steps, 512x512, no guidance, community license).
- LCM-LoRA: Luo et al. 2023 and the Hugging Face LCM-LoRA blog.
- Lab 2 FID numbers: my `week2/lab2.ipynb`.
