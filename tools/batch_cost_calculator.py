# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by: tfrayner/beerfestdb — CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)

Calculates the total cost of a brewing batch, cost per barrel,
and recommended selling price per barrel with a configurable margin.
"""

# ── Default ingredient cost constants (inspired by reference coeffs) ──nDEFAULT_GRAIN_COST_PER_LB   = 1.50   # $/lb
DEFAULT_HOPS_COST_PER_OZ    = 0.80   # $/oz
DEFAULT_YEAST_COST_PER_UNIT = 5.00   # $/unit  (per packet/plate)
DEFAULT_PACKAGING_PER_UNIT  = 3.00   # $/unit  (bottles/cans + labels + caps)
DEFAULT_BATCH_SIZE_BARRELS  = 5.0    # barrels
DEFAULT_MARGIN_PERCENT      = 30.0   # %

# Reference constants from CBF_beer_price_calculator.py (pence):
#   default_abv_coefficient = 70
#   default_abv_constant    = 230
#   default_l_coefficient   = 1.64
# Adapted here: margin is applied on top of total cost the same way
# the reference applies a coefficient + constant on top of cask cost.


def calculate_batch_cost(
    grain_cost_per_lb: float   = DEFAULT_GRAIN_COST_PER_LB,
    hops_cost_per_oz: float    = DEFAULT_HOPS_COST_PER_OZ,
    yeast_cost_per_unit: float = DEFAULT_YEAST_COST_PER_UNIT,
    packaging_per_unit: float  = DEFAULT_PACKAGING_PER_UNIT,
    grain_lbs: float           = 100.0,
    hops_oz: float             = 50.0,
    yeast_units: int           = 4,
    packaging_units: int       = 600,
    batch_size_barrels: float  = DEFAULT_BATCH_SIZE_BARRELS,
    margin_percent: float      = DEFAULT_MARGIN_PERCENT,
) -> dict:
    """Compute the full cost breakdown and recommended selling price."""

    # ── Ingredient costs
    grain_cost       = grain_cost_per_lb   * grain_lbs
    hops_cost        = hops_cost_per_oz    * hops_oz
    yeast_cost       = yeast_cost_per_unit * yeast_units
    packaging_cost   = packaging_per_unit  * packaging_units

    total_ingredient_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    # ── Per-barrel metrics
    cost_per_barrel = total_ingredient_cost / batch_size_barrels

    # ── Margin & selling price
    #    price = cost * (1 + margin/100), analogous to
    #    price = cost * l_coefficient in the original reference
    margin_multiplier = 1 + (margin_percent / 100.0)
    recommended_price_per_barrel = cost_per_barrel * margin_multiplier

    return {
        "grain_cost":              grain_cost,
        "hops_cost":               hops_cost,
        "yeast_cost":              yeast_cost,
        "packaging_cost":          packaging_cost,
        "total_ingredient_cost":   total_ingredient_cost,
        "batch_size_barrels":      batch_size_barrels,
        "cost_per_barrel":         cost_per_barrel,
        "margin_percent":          margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def print_report(r: dict) -> None:
    """Pretty-print the calculation report."""
    print("=" * 55)
    print("   CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 55)
    print()
    print("─── Ingredient Costs ───")
    print(f"  Grain           : ${r['grain_cost']:>10.2f}")
    print(f"  Hops            : ${r['hops_cost']:>10.2f}")
    print(f"  Yeast           : ${r['yeast_cost']:>10.2f}")
    print(f"  Packaging       : ${r['packaging_cost']:>10.2f}")
    print(f"  ─────────────────────────────")
    print(f"  Total Cost      : ${r['total_ingredient_cost']:>10.2f}")
    print()
    print("─── Per-Barrel Metrics ───")
    print(f"  Batch Size      : {r['batch_size_barrels']:.1f} barrels")
    print(f"  Cost / Barrel   : ${r['cost_per_barrel']:>10.2f}")
    print(f"  Margin          : {r['margin_percent']:.1f}%")
    print(f"  ─────────────────────────────")
    print(f"  Recommended Sale: ${r['recommended_price_per_barrel']:>10.2f} / barrel")
    print()
    print("=" * 55)


# ── Sample batch run ──
if __name__ == "__main__":
    results = calculate_batch_cost(
        grain_cost_per_lb   = 1.50,
        hops_cost_per_oz    = 0.80,
        yeast_cost_per_unit = 5.00,
        packaging_per_unit  = 3.00,
        grain_lbs           = 100.0,
        hops_oz             = 50.0,
        yeast_units         = 4,
        packaging_units     = 600,
        batch_size_barrels  = 5.0,
        margin_percent      = 30.0,
    )

    print_report(results)

    # ── Validation assertions
    expected_total   = 1.50*100 + 0.80*50 + 5.00*4 + 3.00*600
    expected_cpb     = expected_total / 5.0
    expected_price   = expected_cpb * 1.30

    assert abs(results["total_ingredient_cost"] - expected_total)            < 0.01
    assert abs(results["cost_per_barrel"] - expected_cpb)                   < 0.01
    assert abs(results["recommended_price_per_barrel"] - expected_price)   < 0.01

    print("\n✅ All assertions passed — script executes correctly!")
