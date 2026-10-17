#!/usr/bin/env python3
"""Fetch initial cross-country sources with audited raw-data manifests.

Run `python scripts/download_data.py --end 2026-10-17` after installing
`pip install -e ".[data]"`. See `data/README.md` for data and leakage limits.
"""

from latent_risk.data.acquisition import main

if __name__ == "__main__":
    raise SystemExit(main())
