# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb — CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb)

The original calculator uses ABV-based and cask-cost-based pricing,
taking whichever is greater. This standalone script adapts that concept
for batch-level costing: it computes total ingredient + packaging costs,
derives cost per barrel, and applies a configurable margin to recommend
a selling price per barrel.

Author: Platform Team
"""

from __future__ import annotations
import argparse
import json
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class IngredientCosts:
    """Per-unit cost inputs for a single batch."""
    grain_per_lb: float    # $ / lb of malt
    hops_per_oz: float     # $ / oz of hops
    yeast_per_unit: float  # $ / yeast unit (packet/liquid)
    packaging_per_unit: float  # $ / packaging unit (bottle, can, keg)

    def total_ingredient_cost(
        self,
        grain_lbs: float,
        hops_oz: float,
        yeast_units: int,
        packaging_units: int,
    ) -> float:
        """Sum all ingredient + packaging costs."""
        grain = self.grain_per_lb * grain_lbs
        hops = self.hops_per_oz * hops_oz
        yeast = self.yeast_per_unit * yeast_units
        packaging = self.packaging_per_unit * packaging_units
        return grain + hops + yeast + packaging


@dataclass
class BatchParams:
    """Batch-level parameters."""
    batch_size_barrels: float          # volume in US barrels (1 bbl = 31 gal)
    grain_lbs: float
    hops_oz: float
    yeast_units: int
    packaging_units: int
    margin_percent: float = 30.0       # markup on cost  (default 30%)


@dataclass
class CostResult:
    """Computed results."""
    total_ingredient_cost: float
    cost_per_barrel: float
    margin_amount_per_barrel: float
    recommended_price_per_barrel: float
    implied_pint_price: float        # 1 barrel = 124 pints (US)

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Core calculation (mirrors the reference's "cost vs ABV, take greater" logic)
# ---------------------------------------------------------------------------
def calculate_batch_costs(
    ingredients: IngredientCosts,
    params: BatchParams,
) -> CostResult:
    """
    Calculate batch costs following the spirit of the original calculator:

    1. Compute raw ingredient + packaging cost (analogous to "cask cost").
    2. Compute a *theoretical minimum* cost per barrel (analogous to the
       ABV-based coefficient pricing in the reference).
    3. Take the **greater** of the two as the true cost floor — just as
       the original code does: ``max(abv_price, cost_price)``.
    4. Apply the configured margin to obtain the recommended selling price.
    """
    # --- Step 1: raw total cost ---
    total = ingredients.total_ingredient_cost(
        params.grain_lbs,
        params.hops_oz,
        params.yeast_units,
        params.packaging_units,
    )

    # --- Step 2: cost per barrel ---
    cost_per_barrel = total / params.batch_size_barrels

    # --- Step 3: theoretical minimum (ABV-style coefficient pricing) ---
    # In the reference, ABV price = abv_coefficient * ABV + abv_constant.
    # Here we approximate with a simple gravity-based estimate:
    #   abv_estimate ≈ 0.13 * (grain_lbs / batch_size_barrels)  (rough rule)
    abv_estimate = 0.13 * (params.grain_lbs / params.batch_size_barrels)
    # Coefficients mirroring the reference defaults (70 pence / 230 pence)
    abv_coefficient = 0.70   # $ per ABV point
    abv_constant = 2.30      # $ base offset
    abv_based_price = abv_coefficient * abv_estimate + abv_constant

    # "Take greater" — same pattern as the reference calculator
    true_cost_per_barrel = max(abv_based_price, cost_per_barrel)

    # --- Step 4: apply margin ---
    margin_multiplier = 1 + (params.margin_percent / 100.0)
    recommended_price = true_cost_per_barrel * margin_multiplier
    margin_amount = recommended_price - true_cost_per_barrel

    # US: 1 barrel = 124 pints (US liquid)
    IMPLIED_PINTS_PER_BARREL = 124
    implied_pint_price = recommended_price / IMPLIED_PINTS_PER_BARREL

    return CostResult(
        total_ingredient_cost=total,
        cost_per_barrel=true_cost_per_barrel,
        margin_amount_per_barrel=margin_amount,
        recommended_price_per_barrel=recommended_price,
        implied_pint_price=implied_pint_price,
    )


# ---------------------------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------------------------
def print_report(ingredients: IngredientCosts, params: BatchParams, result: CostResult) -> None:
    bar = "=" * 60
    print(f"\n{bar}")
    print("   CRAFT BREWERY BATCH COST CALCULATOR")
    print(bar)

    print("\n📦  INGREDIENT & PACKAGING INPUTS")
    print(f"   Grain cost ...... ${ingredients.grain_per_lb:>8.2f} / lb")
    print(f"   Hops cost ....... ${ingredients.hops_per_oz:>8.2f} / oz")
    print(f"   Yeast cost ...... ${ingredients.yeast_per_unit:>8.2f} / unit")
    print(f"   Packaging cost .. ${ingredients.packaging_per_unit:>8.2f} / unit")

    print("\n🍺  BATCH PARAMETERS")
    print(f"   Batch size ...... {params.batch_size_barrels:.1f} bbl ({params.batch_size_barrels * 31:.0f} gal)")
    print(f"   Grain used ...... {params.grain_lbs:.1f} lbs")
    print(f"   Hops used ....... {params.hops_oz:.1f} oz")
    print(f"   Yeast units ..... {params.yeast_units}")
    print(f"   Packaging units . {params.packaging_units}")
    print(f"   Margin .......... {params.margin_percent:.0f}%")

    print("\n💰  COST BREAKDOWN")
    print(f"   Total ingredient+packaging cost : ${result.total_ingredient_cost:>10.2f}")
    raw_cpb = result.total_ingredient_cost / params.batch_size_barrels
    print(f"   Raw cost per barrel (cask) ...... ${raw_cpb:>10.2f}")
    print(f"   True cost / barrel (max) ........ ${result.cost_per_barrel:>10.2f}")

    print("\n📈  PRICING OUTPUT")
    print(f"   Margin per barrel ............. ${result.margin_amount_per_barrel:>10.2f}")
    print(f"   ★ Recommended price / barrel .. ${result.recommended_price_per_barrel:>10.2f}")
    print(f"   Implied pint price (124 pt/bbl) ${result.implied_pint_price:>10.2f}")
    print(f"{bar}\n")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def run_sample() -> None:
    """Run a sample batch to validate the calculator."""
    print("\n▶  Running SAMPLE batch validation ...\n")

    ingredients = IngredientCosts(
        grain_per_lb=1.50,     # $1.50/lb malt
        hops_per_oz=0.80,      # $0.80/oz hops
        yeast_per_unit=2.50,   # $2.50/packet
        packaging_per_unit=0.40,  # $0.40/bottle
    )

    params = BatchParams(
        batch_size_barrels=5.0,
        grain_lbs=200.0,
        hops_oz=75.0,
        yeast_units=10,
        packaging_units=650,   # bottles
        margin_percent=30.0,
    )

    result = calculate_batch_costs(ingredients, params)
    print_report(ingredients, params, result)

    # --- assertions to validate correctness ---
    expected_total = (1.50 * 200) + (0.80 * 75) + (2.50 * 10) + (0.40 * 650)
    assert abs(result.total_ingredient_cost - expected_total) < 0.01, \
        f"Total cost mismatch: {result.total_ingredient_cost} != {expected_total}"

    expected_raw_cpb = expected_total / 5.0
    abv_est = 0.13 * (200 / 5.0)
    abv_price = 0.70 * abv_est + 2.30
    true_cpb = max(abv_price, expected_raw_cpb)
    assert abs(result.cost_per_barrel - true_cpb) < 0.01, \
        f"Cost/barrel mismatch: {result.cost_per_barrel} != {true_cpb}"

    expected_recommended = true_cpb * 1.30
    assert abs(result.recommended_price_per_barrel - expected_recommended) < 0.01, \
        f"Recommended price mismatch: {result.recommended_price_per_barrel} != {expected_recommended}"

    print("✅  All assertions passed — calculator is correct!")


def run_cli() -> None:
    """Parse CLI arguments and run a custom batch."""
    parser = argparse.ArgumentParser(
        description="Craft Brewery Batch Cost Calculator"
    )
    parser.add_argument("--grain-per-lb", type=float, default=1.50)
    parser.add_argument("--hops-per-oz", type=float, default=0.80)
    parser.add_argument("--yeast-per-unit", type=float, default=2.50)
    parser.add_argument("--packaging-per-unit", type=float, default=0.40)
    parser.add_argument("--batch-size-bbl", type=float, required=True,
                        help="Batch size in US barrels")
    parser.add_argument("--grain-lbs", type=float, required=True)
    parser.add_argument("--hops-oz", type=float, required=True)
    parser.add_argument("--yeast-units", type=int, required=True)
    parser.add_argument("--packaging-units", type=int, required=True)
    parser.add_argument("--margin-percent", type=float, default=30.0)
    parser.add_argument("--json", action="store_true",
                        help="Output results as JSON")

    args = parser.parse_args()

    ingredients = IngredientCosts(
        grain_per_lb=args.grain_per_lb,
        hops_per_oz=args.hops_per_oz,
        yeast_per_unit=args.yeast_per_unit,
        packaging_per_unit=args.packaging_per_unit,
    )
    params = BatchParams(
        batch_size_barrels=args.batch_size_bbl,
        grain_lbs=args.grain_lbs,
        hops_oz=args.hops_oz,
        yeast_units=args.yeast_units,
        packaging_units=args.packaging_units,
        margin_percent=args.margin_percent,
    )

    result = calculate_batch_costs(ingredients, params)

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print_report(ingredients, params, result)


if __name__ == "__main__":
    # Default to sample validation; use --cli for custom batches
    run_sample()
