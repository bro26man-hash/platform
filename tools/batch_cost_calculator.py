#!/usr/bin/env python3
"""
batch_cost_calculator.py - Craft brewery batch cost calculator.

Inspired by the beer price calculator in tfrayner/beerfestdb:
    https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py

That tool prices beers based on the greater of an ABV-based value or the
cask cost. This script follows the same philosophy for a brewing batch:
compute the true ingredient cost per batch, then add a configurable margin
to recommend a selling price per barrel.

Units
-----
1 barrel (bbl) = 31 US gallons
1 US gallon   = 3.78541 liters
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

# --------------------------------------------------------------------------- #
# Conversion constants
# --------------------------------------------------------------------------- #
BBL_TO_GALLONS = 31.0
GALLON_TO_LITERS = 3.78541


@dataclass
class Recipe:
    """Ingredient usage rates and unit prices for one beer recipe."""
    grain_lb_per_bbl: float          # lb of grain per barrel
    grain_price_per_lb: float        # $/lb
    hops_oz_per_bbl: float           # oz of hops per barrel
    hops_price_per_oz: float         # $/oz
    yeast_units_per_batch: float     # yeast units (flasks/packs) per batch
    yeast_price_per_unit: float      # $/unit
    packaging_units_per_bbl: float   # cans/kegs/etc. per barrel
    packaging_price_per_unit: float  # $/unit


def calculate_batch_cost(
    recipe: Recipe,
    batch_size_bbl: float,
    margin_pct: float = 25.0,
) -> Dict[str, float]:
    """Compute total batch cost, cost per barrel, and recommended price.

    Args:
        recipe: usage rates and unit prices for ingredients.
        batch_size_bbl: batch size in barrels.
        margin_pct: configurable margin percentage (e.g. 25.0 for 25%).

    Returns:
        Dictionary with the full cost breakdown and pricing.
    """
    if batch_size_bbl <= 0:
        raise ValueError("batch_size_bbl must be positive")
    if margin_pct < 0:
        raise ValueError("margin_pct must be non-negative")

    grain_cost        = recipe.grain_lb_per_bbl      * recipe.grain_price_per_lb      * batch_size_bbl
    hops_cost         = recipe.hops_oz_per_bbl       * recipe.hops_price_per_oz       * batch_size_bbl
    yeast_cost        = recipe.yeast_units_per_batch * recipe.yeast_price_per_unit
    packaging_cost    = recipe.packaging_units_per_bbl * recipe.packaging_price_per_unit * batch_size_bbl

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_bbl = total_cost / batch_size_bbl

    recommended_price_per_bbl = cost_per_bbl * (1.0 + margin_pct / 100.0)

    return {
        "batch_size_bbl": batch_size_bbl,
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_cost": total_cost,
        "cost_per_bbl": cost_per_bbl,
        "margin_pct": margin_pct,
        "recommended_price_per_bbl": recommended_price_per_bbl,
    }


def _fmt(value: float) -> str:
    return f"${value:,.2f}"


def print_report(result: Dict[str, float]) -> None:
    """Print a human-readable batch cost report."""
    print("=" * 54)
    print("       CRAFT BREWERY BATCH COST REPORT")
    print("=" * 54)
    print(f"Batch size............ {result['batch_size_bbl']:.1f} bbl")
    print("-" * 54)
    print(f"Grain ................. {_fmt(result['grain_cost'])}")
    print(f"Hops  ................. {_fmt(result['hops_cost'])}")
    print(f"Yeast ................. {_fmt(result['yeast_cost'])}")
    print(f"Packaging ............. {_fmt(result['packaging_cost'])}")
    print("-" * 54)
    print(f"TOTAL COST ............ {_fmt(result['total_cost'])}")
    print(f"COST PER BARREL ....... {_fmt(result['cost_per_bbl'])}")
    print(f"MARGIN ................ {result['margin_pct']:.1f}%")
    print("-" * 54)
    print(f"RECOMMENDED SELL PRICE PER BARREL ... {_fmt(result['recommended_price_per_bbl'])}")
    print("=" * 54)


if __name__ == "__main__":
    # --- Sample batch: 5 bbl hop-forward pale ale -------------------------
    sample_recipe = Recipe(
        grain_lb_per_bbl=12.0, grain_price_per_lb=1.25,     # 12 lb/bbl @ $1.25/lb
        hops_oz_per_bbl=1.2, hops_price_per_oz=9.00,        # 1.2 oz/bbl @ $9.00/oz
        yeast_units_per_batch=2.0, yeast_price_per_unit=3.75,  # 2 units @ $3.75/unit
        packaging_units_per_bbl=330.0, packaging_price_per_unit=0.40,  # ~330 cans/bbl @ $0.40/can
    )

    result = calculate_batch_cost(
        recipe=sample_recipe,
        batch_size_bbl=5.0,
        margin_pct=25.0,
    )
    print_report(result)
