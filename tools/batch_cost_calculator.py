"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/master/tool_dashboard/CBF_beer_price_calculator.py)

That reference computes a sale price as the greater of an ABV-based value or
the cask cost, then rounds it to a clean price point. This script adapts that
cost-vs-price philosophy to a full brewing batch:

  1. Accumulate ingredient & packaging costs (grain, hops, yeast, packaging).
  2. Derive the total batch cost.
  3. Normalize to a cost per barrel.
  4. Apply a configurable margin to recommend a selling price per barrel.

Constants
---------
1 US barrel (bbl) = 31 gallons
"""

from typing import Dict

GALLONS_PER_BARREL = 31.0


def calculate_batch_cost(
    batch_size_barrels: float,
    grain_cost_per_lb: float, grain_lbs: float,
    hops_cost_per_oz: float, hops_oz: float,
    yeast_cost_per_unit: float, yeast_units: float,
    packaging_cost_per_unit: float, packaging_units: float,
    margin_percent: float,
) -> Dict[str, float]:
    """Compute batch economics. All monetary inputs are in USD."""
    # ---- Ingredient / packaging line items ----
    grain_total = grain_cost_per_lb * grain_lbs
    hops_total = hops_cost_per_oz * hops_oz
    yeast_total = yeast_cost_per_unit * yeast_units
    packaging_total = packaging_cost_per_unit * packaging_units

    # ---- Aggregates ----
    total_cost = grain_total + hops_total + yeast_total + packaging_total
    cost_per_barrel = total_cost / batch_size_barrels

    # ---- Recommended sale price (apply margin on top of cost) ----
    recommended_price = cost_per_barrel * (1.0 + margin_percent / 100.0)

    return {
        "grain_total": grain_total,
        "hops_total": hops_total,
        "yeast_total": yeast_total,
        "packaging_total": packaging_total,
        "total_cost": total_cost,
        "cost_per_barrel": cost_per_barrel,
        "recommended_price_per_barrel": recommended_price,
        "batch_volume_gallons": batch_size_barrels * GALLONS_PER_BARREL,
    }


if __name__ == "__main__":
    # ---- Sample batch (a 5 bbl pilot run) ----
    batch = calculate_batch_cost(
        batch_size_barrels=5.0,
        grain_cost_per_lb=0.40, grain_lbs=200.0,
        hops_cost_per_oz=0.75, hops_oz=16.0,
        yeast_cost_per_unit=1.50, yeast_units=4.0,
        packaging_cost_per_unit=0.35, packaging_units=200.0,
        margin_percent=35.0,
    )

    print("=" * 55)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)
    print(f"Batch size ............ {5.0} bbl ({batch['batch_volume_gallons']:.0f} gal)")
    print("-" * 55)
    print(f"Grain cost ............ ${batch['grain_total']:.2f}")
    print(f"Hops cost ............. ${batch['hops_total']:.2f}")
    print(f"Yeast cost ............ ${batch['yeast_total']:.2f}")
    print(f"Packaging cost ........ ${batch['packaging_total']:.2f}")
    print("-" * 55)
    print(f"TOTAL COST ............ ${batch['total_cost']:.2f}")
    print(f"COST / BARREL ......... ${batch['cost_per_barrel']:.2f}")
    print("-" * 55)
    print(f"Margin ................ 35.0%")
    print(f"RECOMMENDED PRICE ..... ${batch['recommended_price_per_barrel']:.2f} / bbl")
    print("=" * 55)
