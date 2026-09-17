#!/usr/bin/env python3
"""
batch_cost_calculator.py
================================================================================
Craft Brewery Batch Cost Calculator

Inspired by: tfrayner/beerfestdb - CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb)

The original tool uses cost-based pricing: it compares a cost-derived price
against an ABV-derived price and prices at the greater of the two. This script
adapts that philosophy for a single-batch costing model:

  1. Compute total ingredient / packaging cost for a batch.
  2. Divide by batch size (barrels) to get cost per barrel.
  3. Apply a configurable margin to recommend a selling price per barrel.

Usage:
    python batch_cost_calculator.py
"""

from dataclasses import dataclass

DEFAULT_MARGIN_perc = 30.0


@dataclass
class BatchInputs:
    """All costing inputs for a single brew batch."""
    grain_cost_per_lb: float       # $ / lb
    hops_cost_per_oz: float        # $ / oz
    yeast_cost_per_unit: float     # $ / unit
    packaging_cost_per_unit: float # $ / unit (kegs, bottles, cans)
    grain_lbs: float
    hops_oz: float
    yeast_units: int
    packaging_units: int
    batch_barrels: float
    margin_pct: float = DEFAULT_MARGIN_perc


def compute_batch(inputs: BatchInputs) -> dict:
    """Return a dict of computed costing metrics."""
    grain_total = inputs.grain_cost_per_lb * inputs.grain_lbs
    hops_total = inputs.hops_cost_per_oz * inputs.hops_oz
    yeast_total = inputs.yeast_cost_per_unit * inputs.yeast_units
    packaging_total = inputs.packaging_cost_per_unit * inputs.packaging_units

    ingredient_total = grain_total + hops_total + yeast_total
    total_cost = ingredient_total + packaging_total

    cost_per_barrel = total_cost / inputs.batch_barrels
    # Recommended selling price = cost * (1 + margin/100)
    recommended_price = cost_per_barrel * (1 + inputs.margin_pct / 100.0)
    margin_dollars = recommended_price - cost_per_barrel

    return {
        "grain_total": grain_total,
        "hops_total": hops_total,
        "yeast_total": yeast_total,
        "packaging_total": packaging_total,
        "ingredient_total": ingredient_total,
        "total_cost": total_cost,
        "cost_per_barrel": cost_per_barrel,
        "recommended_price": recommended_price,
        "margin_dollars": margin_dollars,
    }


def fmt(value: float) -> str:
    return f"${value:,.2f}"


def main():
    print("=" * 72)
    print("        CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 72)
    print("Inspired by: tfrayner/beerfestdb (CBF_beer_price_calculator.py)")
    print()

    # ---- Sample batch: 5-barrel all-grain pale ale ------------------------
    sample = BatchInputs(
        grain_cost_per_lb=1.25,
        hops_cost_per_oz=0.85,
        yeast_cost_per_unit=4.50,
        packaging_cost_per_unit=1.75,
        grain_lbs=120.0,
        hops_oz=25.0,
        yeast_units=3,
        packaging_units=3,
        batch_barrels=5.0,
        margin_pct=30.0,
    )

    results = compute_batch(sample)

    print("BATCH INPUTS")
    print("-" * 72)
    print(f"  Grain      : {sample.grain_lbs:,.1f} lb @ {fmt(sample.grain_cost_per_lb)}/lb")
    print(f"  Hops       : {sample.hops_oz:,.1f} oz @ {fmt(sample.hops_cost_per_oz)}/oz")
    print(f"  Yeast      : {sample.yeast_units} units @ {fmt(sample.yeast_cost_per_unit)}/unit")
    print(f"  Packaging  : {sample.packaging_units} units @ {fmt(sample.packaging_cost_per_unit)}/unit")
    print(f"  Batch size : {sample.batch_barrels:.1f} barrels")
    print(f"  Margin     : {sample.margin_pct:.1f}%")
    print()

    print("COST BREAKDOWN")
    print("-" * 72)
    print(f"  Grain cost      : {fmt(results['grain_total'])}")
    print(f"  Hops cost       : {fmt(results['hops_total'])}")
    print(f"  Yeast cost      : {fmt(results['yeast_total'])}")
    print(f"  Packaging cost  : {fmt(results['packaging_total'])}")
    print(f"  Ingredient total: {fmt(results['ingredient_total'])}")
    print(f"  TOTAL BATCH COST: {fmt(results['total_cost'])}")
    print()

    print("PRICING OUTPUT")
    print("-" * 72)
    print(f"  Cost per barrel        : {fmt(results['cost_per_barrel'])}")
    print(f"  Margin per barrel      : {fmt(results['margin_dollars'])}")
    print(f"  Recommended sell price : {fmt(results['recommended_price'])} / bbl")
    print()

    # ---- Validation ------------------------------------------------------
    assert results["total_cost"] == results["grain_total"] + results["hops_total"] \
        + results["yeast_total"] + results["packaging_total"], "Total mismatch"
    assert abs(results["cost_per_barrel"] - results["total_cost"] / 5.0) < 1e-9
    assert abs(results["recommended_price"] - results["cost_per_barrel"] * 1.30) < 1e-9
    print("=" * 72)
    print("VALIDATION: All assertions passed. Script executed successfully.")
    print("=" * 72)


if __name__ == "__main__":
    main()
