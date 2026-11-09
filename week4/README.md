# Week 4: Text-to-Image & Latent Space Exploration

![ControlNet comparison](lab4_images/controlnet_comparison.png)

Lab 4 (`lab4.ipynb`, T4 GPU): SDXL with the fp16-fixed VAE.

| Part | What | Output |
|---|---|---|
| 1 | CFG sweep 1.5 / 4 / 7.5 / 12 / 20 on the same seed; DPM-Solver vs DDIM timing | `lab4_images/cfg_sweep.png`, `lab4_images/scheduler_compare.png` |
| 2 | Canny ControlNet at conditioning scale 0 / 0.5 / 1.0 | `lab4_images/controlnet_comparison.png` |
| 3 | Linear interpolation of final latents vs slerp of starting noise (seeds 0 and 99) | `lab4_images/interp_linear.png`, `lab4_images/interp_slerp.png` |
| 4 | CLIP score table for every image | `lab4_images/clip_scores.csv` |

Best images: ![CFG sweep](lab4_images/cfg_sweep.png)
![Noise slerp](lab4_images/interp_slerp.png)

Homework: [`homework/`](homework/).
