#!/usr/bin/env python3
"""
batch_cost_calculator.py
=========================
Craft Brewery Batch Cost Calculator

Inspired by tfrayner/beerfestdb CBF_beer_price_calculator.py
https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py

Pricing philosophy (adapted from reference):
  - ABV-based price  = (abv_percent * abv_coefficient) + abv_constant
  - Cost-based price = cost_per_barrel * (1 + margin_percent / 100)
  - Recommended price = max(cost-based, ABV-based)

Inputs:
  (a) grain ($/lb), hops ($/oz), yeast ($/unit), packaging ($/unit)
  (b) batch size in barrels
  (c) total cost & cost-per-barrel
  (d) configurable margin % -> recommended selling price per barrel
"""

import math
import json


def calculate_batch_cost(
    grain_per_lb: float,
    hops_per_oz: float,
    yeast_per_unit: float,
    packaging_per_unit: float,
    grain_lbs: float,
    hops_oz: float,
    yeast_units: float,
    packaging_units: float,
    batch_size_barrels: float,
    abv_percent: float,
    margin_percent: float,
    abv_coefficient: float = 1.5,
    abv_constant: float = 5.0,
) -> dict:
    """
    Calculate total batch cost, cost per barrel, and recommended
    selling price per barrel.

    Reference pricing model (from CBF_beer_price_calculator.py):
      abv_price  = product_abv * abv_coefficient + abv_constant
      cost_price = cask_price_per_litre * l_coefficient
      sale_price = max(abv_price, cost_price)

    Adapted here for a brewery batch:
      ingredient_totals -> total_cost / batch_size = cost_per_barrel
      base_price  = cost_per_barrel * (1 + margin / 100)
      abv_price   = abv_percent * abv_coefficient + abv_constant
      recommended = max(base_price, abv_price)
    """
    grain_total     = grain_per_lb      * grain_lbs
    hops_total      = hops_per_oz       * hops_oz
    yeast_total     = yeast_per_unit    * yeast_units
    packaging_total = packaging_per_unit * packaging_units

    total_cost = grain_total + hops_total + yeast_total + packaging_total

    if batch_size_barrels <= 0:
        raise ValueError("Batch size must be greater than 0")

    cost_per_barrel       = total_cost / batch_size_barrels
    base_price_per_barrel  = cost_per_barrel * (1 + margin_percent / 100)
    abv_adjusted_price     = (abv_percent * abv_coefficient) + abv_constant
    recommended_price      = round(max(base_price_per_barrel, abv_adjusted_price), 2)

    return {
        "batch_size_barrels":          batch_size_barrels,
        "abv_percent":                 abv_percent,
        "margin_percent":              margin_percent,
        "grain_total":                round(grain_total, 2),
        "hops_total":                 round(hops_total, 2),
        "yeast_total":                round(yeast_total, 2),
        "packaging_total":            round(packaging_total, 2),
        "total_cost":                 round(total_cost, 2),
        "cost_per_barrel":            round(cost_per_barrel, 2),
        "base_price_per_barrel":      round(base_price_per_barrel, 2),
        "abv_adjusted_price":         round(abv_adjusted_price, 2),
        "recommended_price_per_barrel": recommended_price,
    }


def print_results(r: dict):
    """Pretty-print the calculation results."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\n  Batch Size : {r['batch_size_barrels']} barrels")
    print(f"  ABV        : {r['abv_percent']}%")
    print(f"  Margin     : {r['margin_percent']}%")
    print("\n  --- Ingredient Costs ---")
    print(f"    Grain       :  ${r['grain_total']:>10.2f}")
    print(f"    Hops        :  ${r['hops_total']:>10.2f}")
    print(f"    Yeast       :  ${r['yeast_total']:>10.2f}")
    print(f"    Packaging   :  ${r['packaging_total']:>10.2f}")
    print(f"\n  Total Batch Cost   :  ${r['total_cost']:>10.2f}")
    print(f"  Cost per Barrel     :  ${r['cost_per_barrel']:>10.2f}")
    print("\n  --- Pricing Breakdown ---")
    print(f"    Base Price (cost+margin)  :  ${r['base_price_per_barrel']:>10.2f}")
    print(f"    ABV-Adjusted Price         :  ${r['abv_adjusted_price']:>10.2f}")
    print(f"    >> Recommended Price/Barrel:  ${r['recommended_price_per_barrel']:>10.2f}")
    print("\n" + "=" * 60)
    print("  Pricing note: Recommended = max(cost+margin, ABV-adjusted)")
    print("  Inspired by tfrayner/beerfestdb CBF_beer_price_calculator.py")
    print("=" * 60)


# ── Sample batch execution ───────────────────────────────────────────────
if __name__ == "__main__":
    results = calculate_batch_cost(
        grain_per_lb=2.50,
        hops_per_oz=8.00,
        yeast_per_unit=5.00,
        packaging_per_unit=0.75,
        grain_lbs=200,
        hops_oz=5,
        yeast_units=2,
        packaging_units=3000,
        batch_size_barrels=10,
        abv_percent=6.0,
        margin_percent=30,
        abv_coefficient=1.5,
        abv_constant=5.0,
    )
    print_results(results)
    print("\n--- JSON Output ---")
    print(json.dumps(results, indent=2))

    # Validation assertions
    assert results["grain_total"] == 500.0
    assert results["hops_total"] == 40.0
    assert results["yeast_total"] == 10.0
    assert results["packaging_total"] == 2250.0
    assert results["total_cost"] == 2800.0
    assert results["cost_per_barrel"] == 280.0
    assert results["base_price_per_barrel"] == 364.0
    assert results["abv_adjusted_price"] == 14.0
    assert results["recommended_price_per_barrel"] == 364.0
    print("\n--- Validation ---")
    print("All 9 assertions passed. Script executed successfully.")
