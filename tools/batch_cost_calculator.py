# batch_cost_calculator.py
# Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
# A standalone craft brewery batch cost calculator.

import math


def calculate_batch_cost(
    grain_cost_per_lb: float,
    hops_cost_per_oz: float,
    yeast_cost_per_unit: float,
    packaging_cost_per_unit: float,
    grain_lbs: float,
    hops_oz: float,
    yeast_units: float,
    packaging_units: float,
    batch_size_barrels: float,
    margin_percent: float,
) -> dict:
    """
    Calculate the total cost, cost per barrel, and recommended selling price
    for a craft brewery batch.

    Inspired by the cost-based pricing logic in CBF_beer_price_calculator.py
    where the sale price is derived from the greater of ABV-based pricing or
    raw cost, then margins and rounding are applied.

    Args:
        grain_cost_per_lb:      Price of grain per pound ($)
        hops_cost_per_oz:       Price of hops per ounce ($)
        yeast_cost_per_unit:    Price of yeast per unit ($)
        packaging_cost_per_unit: Price of packaging (bottles/kegs) per unit ($)
        grain_lbs:              Pounds of grain used
        hops_oz:                Ounces of hops used
        yeast_units:            Number of yeast units (containers/packs)
        packaging_units:        Number of packaging units (bottles, kegs, etc.)
        batch_size_barrels:     Batch size in US barrels (1 barrel = 31 gallons)
        margin_percent:         Desired margin as a percentage (e.g. 30 for 30%)

    Returns:
        Dictionary with all cost and pricing breakdown.
    """

    # --- Ingredient cost breakdown ---
    grain_total      = grain_cost_per_lb * grain_lbs
    hops_total       = hops_cost_per_oz * hops_oz
    yeast_total      = yeast_cost_per_unit * yeast_units
    packaging_total  = packaging_cost_per_unit * packaging_units

    # --- Total batch cost ---
    total_cost = grain_total + hops_total + yeast_total + packaging_total

    # --- Cost per barrel ---
    if batch_size_barrels <= 0:
        raise ValueError("Batch size must be greater than zero.")
    cost_per_barrel = total_cost / batch_size_barrels

    # --- Recommended selling price with margin ---
    # Same philosophy as reference: ensure price covers cost, then apply margin.
    # sale_price = cost_per_barrel * (1 + margin_percent / 100)
    recommended_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100)

    # Round up to the nearest cent (similar to the reference's math.ceil rounding)
    recommended_price_per_barrel = math.ceil(recommended_price_per_barrel * 100) / 100

    return {
        "grain_total":      round(grain_total, 2),
        "hops_total":       round(hops_total, 2),
        "yeast_total":      round(yeast_total, 2),
        "packaging_total":  round(packaging_total, 2),
        "total_cost":       round(total_cost, 2),
        "batch_size_barrels": batch_size_barrels,
        "cost_per_barrel":  round(cost_per_barrel, 2),
        "margin_percent":   margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def print_results(results: dict) -> None:
    """Pretty-print the calculation results."""
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print("\n--- Ingredient Costs ---")
    print(f"  Grain:       ${results['grain_total']:>8.2f}")
    print(f"  Hops:        ${results['hops_total']:>8.2f}")
    print(f"  Yeast:       ${results['yeast_total']:>8.2f}")
    print(f"  Packaging:   ${results['packaging_total']:>8.2f}")
    print(f"  {'─' * 42}")
    print(f"  TOTAL COST:  ${results['total_cost']:>8.2f}")
    print(f"\n--- Batch Info ---")
    print(f"  Batch Size:  {results['batch_size_barrels']} barrels")
    print(f"  Cost/Barrel: ${results['cost_per_barrel']:>8.2f}")
    print(f"\n--- Pricing ---")
    print(f"  Margin:      {results['margin_percent']:.1f}%")
    print(f"  Recommended Price per Barrel: ${results['recommended_price_per_barrel']:>8.2f}")
    print(f"\n--- Per-Barrel Breakdown ---")
    per_barrel_ingredient = results['total_cost'] / results['batch_size_barrels']
    print(f"  Raw ingredient cost/bbl: ${per_barrel_ingredient:.2f}")
    print(f"  With margin:             ${results['recommended_price_per_barrel']:.2f}")
    print("=" * 60)


# ──────────────────────────────────────────────────────────────
# SAMPLE BATCH — run immediately to validate
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Sample: a 5-barrel IPA batch
    sample = calculate_batch_cost(
        grain_cost_per_lb       = 1.50,    # $1.50 / lb for 2-row Malt
        hops_cost_per_oz        = 0.85,    # $0.85 / oz for Cascade
        yeast_cost_per_unit     = 5.00,    # $5.00 / yeast packet
        packaging_cost_per_unit = 2.00,    # $2.00 / keg
        grain_lbs               = 200,     # 200 lbs grain
        hops_oz                 = 30,      # 30 oz hops
        yeast_units             = 2,       # 2 yeast packets
        packaging_units         = 5,       # 5 kegs
        batch_size_barrels      = 5,       # 5 barrels
        margin_percent          = 35,      # 35% margin
    )

    print_results(sample)

    # ── Assertions to validate correctness ──
    assert sample["grain_total"]     == 300.00, f"Expected 300.00, got {sample['grain_total']}"
    assert sample["hops_total"]      == 25.50,  f"Expected 25.50, got {sample['hops_total']}"
    assert sample["yeast_total"]     == 10.00,  f"Expected 10.00, got {sample['yeast_total']}"
    assert sample["packaging_total"] == 10.00,  f"Expected 10.00, got {sample['packaging_total']}"
    assert sample["total_cost"]      == 345.50, f"Expected 345.50, got {sample['total_cost']}"
    assert sample["cost_per_barrel"] == 69.10,  f"Expected 69.10, got {sample['cost_per_barrel']}"
    # 69.10 * 1.35 = 93.285 -> ceil(9328.5)/100 = 93.29
    assert sample["recommended_price_per_barrel"] == 93.29, \
        f"Expected 93.29, got {sample['recommended_price_per_barrel']}"
    assert sample["batch_size_barrels"] == 5
    assert sample["margin_percent"]     == 35

    print("\n✅ All assertions passed! Calculator is working correctly.")
