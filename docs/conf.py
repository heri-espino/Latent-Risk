"""Sphinx documentation configuration for the installable package."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

project = "Latent Risk"
author = "Latent Risk research contributors"
release = "0.1.0"
extensions = ["myst_parser", "sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.viewcode"]
templates_path = []
exclude_patterns = ["_build"]
html_theme = "alabaster"
master_doc = "index"
autodoc_typehints = "description"
napoleon_google_docstring = False
napoleon_numpy_docstring = True
