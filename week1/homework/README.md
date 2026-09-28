# Week 1 Homework — Generative Models

For this homework, I trained a VAE on my custom music-note image dataset and explored its latent space. 

I also trained three GAN versions: a Standard GAN, an Unbalanced GAN, and WGAN-GP, and compared their FID scores, diversity, and training behavior. 

What surprised me most was that the Unbalanced GAN had a much lower FID (116.74) than the Standard GAN (175.39), even though its diversity score was lower. 

WGAN-GP achieved the lowest FID (116.65) and the highest diversity score (9.63). 

This experiment showed me that FID alone does not tell the whole story about the quality and diversity of generated data.
