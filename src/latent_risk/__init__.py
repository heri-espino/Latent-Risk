"""Latent Risk: methods for reproducible financial-risk index research.

This package deliberately separates index measurement from any proposed
likelihood-based trend smoother and the subsequent forecast evaluation.
"""
from .indices import fit_pca, fit_signed_composite

__all__ = ["fit_pca", "fit_signed_composite"]
__version__ = "0.1.0"
