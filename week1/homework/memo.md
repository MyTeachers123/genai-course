Given the need to generate synthetic data—derived from an existing set of 800 fundus images across five imbalanced disease grades—to safely assist in training a diagnostic classifier, I recommend using a VAE.

I am not prioritizing GANs because the small, imbalanced dataset raises significant concerns regarding mode collapse; nor am I prioritizing diffusion models, due to current constraints on data and computational budget. Indeed, the course materials themselves compare these three model families based on these typical trade-offs.

While VAEs carry the risk of producing blurry outputs—which, in medical imaging, could obscure subtle yet critical disease features—the limited data volume and relatively constrained image domain make a high rate of human clinical review feasible. Consequently, generated images cannot be automatically added to the training set but must undergo both human clinical review and quantitative evaluation. Thus, the VAE is the most suitable choice for this specific use case.

The ultimate success criterion is not merely generating visually appealing images or achieving a low FID score; rather, it is ensuring that the inclusion of VAE-generated synthetic data reduces the classifier's false negative rate on an independent real-world fundus test set, without causing unacceptable degradation in other performance metrics.

In terms of overall visual feature distribution, VAE-generated images can still closely resemble real fundus photographs. While FID measures visual fidelity ("how realistic do the images look?"), the false negative rate addresses the clinical outcome ("did the inclusion of synthetic data reduce missed diagnoses?"). Therefore, the VAE aligns more closely with the ultimate goal of this medical application.

Given the relatively consistent anatomical structure of fundus images and the availability of five existing disease labels, future development could incorporate a Conditional VAE (CVAE) to better tailor the synthetic data generation to specific labels, bringing the training process closer to the ideal state.
