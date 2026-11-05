"""Base year, policy years and the declared basis, read from years.json.

The basis is declared once here and shown once on the Method tab. Every
figure in results.json is on this basis (retro lesson: declare the basis
once).
"""

import json
from pathlib import Path

_CONFIG = json.loads((Path(__file__).parent / "years.json").read_text())

BASE_YEAR: int = _CONFIG["base_year"]
BUDGET_YEAR: int = _CONFIG["budget_year"]
POLICY_YEARS: list[int] = list(_CONFIG["policy_years"])
BASIS: dict[str, str] = dict(_CONFIG["basis"])


def fiscal_year_label(year: int) -> str:
    """2027 -> '2027-28'."""
    return f"{year}-{str(year + 1)[-2:]}"
