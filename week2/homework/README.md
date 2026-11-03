# Week 2 Homework - Diffusion: Schedules, Conditioning, and Latency

<!-- Delete every comment line before submitting. Write in your own words. -->

## What I built

- **Part 1:** <!-- one or two sentences: FashionMNIST, three schedules, 40 epochs, FID -->
- **Part 2:** <!-- class conditioning + classifier-free guidance -->
- **Part 3:** <!-- latency memo, see memo.md -->

## Results

| Variant | Epoch 20 FID | Epoch 40 FID | Training time |
|---|---|---|---|
| A - linear | | | |
| B - cosine (s = 0.008) | | | |
| C - cosine (s = 0.04) | | | |

<!-- Copy from images/part1_fid_table.md -->

## Files

| File | Contents |
|---|---|
| `notebook.ipynb` | Parts 1 and 2, runs end-to-end on a Colab T4 GPU |
| `images/` | Part 1 sample grids, Part 2 demo and guidance sweeps |
| `memo.md` | Part 3 latency memo |
| `results.json` | All numbers produced by the notebook |

## What surprised me

<!-- 2-4 bullets from your own runs -->

## How to run

Open `notebook.ipynb` in Colab, choose Runtime -> Change runtime type -> T4 GPU, then Run all.
Checkpoints are saved to Google Drive, so after a disconnect, Run all again continues training.
