# Week 2 Homework - Diffusion: Schedules, Conditioning, and Latency

## What I built

- **Part 1:** trained the Lab 2 U-Net (5.5M parameters) on FashionMNIST with three noise schedules - linear, cosine (s = 0.008) and cosine (s = 0.04) - for 40 epochs each, with 5x5 sample grids at epochs 10/20/30/40 and FID (1,000 generated vs 1,000 real test images, Inception-v3 features).
- **Part 2:** added class conditioning (a class embedding added to the time embedding, with an 11th "null" class) and classifier-free guidance: 15% label dropout in training, two forward passes per step at inference. Swept guidance w = 1, 3, 7, 15 and measured class adherence, diversity and saturation.
- **Part 3:** a latency memo for real-time 512x512 generation on 2x A10G - see [memo.md](memo.md).

## Results

| Variant | Epoch 20 FID | Epoch 40 FID | Training time |
|---|---|---|---|
| A - linear | 41.60 | **36.98** | 20.3 min |
| B - cosine (s = 0.008) | 43.67 | 44.55 | 20.4 min |
| C - cosine (s = 0.04) | 41.74 | 37.82 | 20.5 min |
| Real vs real (floor) | 22.10 | 22.10 | - |

| Guidance w | T-shirt adherence | Sneaker adherence | T-shirt diversity | Saturated pixels |
|---|---|---|---|---|
| 1 | 88% | 96% | 16.86 | 64.1% |
| 3 | 100% | 100% | 13.80 | 64.7% |
| 7 | 100% | 100% | 12.78 | 66.8% |
| 15 | 100% | 100% | 13.15 | 77.2% |

## Files

| File | Contents |
|---|---|
| [notebook.ipynb](notebook.ipynb) | Parts 1 and 2 with outputs and analysis, runs end-to-end on a Colab T4 GPU |
| [images/](images/) | 12 Part 1 sample grids, FID table, T-shirt / Sneaker demo, guidance sweeps |
| [memo.md](memo.md) | Part 3 latency memo |
| [results.json](results.json) | All numbers produced by the notebook |

## What surprised me

- **Linear beat cosine on FashionMNIST**, the opposite of my MNIST lab (cosine 16.48 vs linear 17.35). Cosine with s = 0.008 even got slightly worse from epoch 20 to 40.
- **Larger s did not preserve more early signal.** At t = T/10, s = 0.04 keeps alpha_bar = 0.959 versus 0.972 for s = 0.008 - the opposite of what the assignment describes - and it still scored better.
- **Training was fast:** 20 minutes per 40-epoch run on a T4 with mixed precision, while every FID measurement needed 1,000 images x 1,000 denoising steps. Sampling, not training, is the expensive part - which is exactly the problem the Part 3 memo is about.
- **Guidance saturates quickly:** w = 3 already gave 100% class adherence; going to w = 15 only added blown-out white areas.

## How to run

Open [notebook.ipynb in Colab](https://colab.research.google.com/github/MyTeachers123/genai-course/blob/main/week2/homework/notebook.ipynb), choose Runtime -> Change runtime type -> T4 GPU, then Run all. Checkpoints are saved to Google Drive, so after a disconnect, Run all again continues training.
