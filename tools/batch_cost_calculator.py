# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by tfrayner/beerfestdb — CBF_beer_price_calculator.py
# Computes total batch cost, cost per barrel, and recommended selling price
# with a configurable margin.

# ── Configuration / Inputs ──────────────────────────────────────────────────

# Ingredient costs
GRAIN_COST_PER_LB      = 0.45   # $/lb  (e.g., two-row pale malt)
HOPS_COST_PER_OZ       = 0.12   # $/oz  (e.g., Cascade pellets)
YEAST_COST_PER_UNIT    = 1.50   # $/unit (liquid yeast pack)
PACKAGING_COST_PER_UNIT = 0.80  # $/unit (bottle, cap, or can)

# Batch parameters
BATCH_SIZE_BARRELS     = 5.0    # barrels (1 barrel = 31 US gallons)
MARGIN_PERCENT         = 30.0   # % markup on top of total cost

# Other practical constants
BARREL_TO_GALLONS      = 31.0
FININGS_PER_BATCH      = 1.0    # unit of finings (ossary/gelatin)
FININGS_COST           = 0.50   # $/unit

# ── Calculation Functions ────────────────────────────────────────────────────

def calculate_ingredient_costs(
    grain_cost_per_lb: float,
    hops_cost_per_oz: float,
    yeast_cost_per_unit: float,
    packaging_cost_per_unit: float,
    batch_size_barrels: float,
    margin_percent: float,
) -> dict:
    """
    Calculate the total and per-unit economics of a craft beer batch.

    Assumptions (standard 5 bbl homebrew / pilot scale):
      - Grain usage: ~6.0 lb per gallon of wort (typical mash efficiency)
      - Hops usage:   ~0.5 oz per gallon (moderate bittering + aroma)
      - Yeast:        1 unit per batch
      - Packaging:    capacity based on standard 12 oz bottles
                     (1 barrel ≈ 124 × 12 oz bottles)
    """
    gallons = batch_size_barrels * BARREL_TO_GALLONS

    # Grain cost (6 lb/gal is a standard ballpark for all-grain brewing)
    grain_lbs = gallons * 6.0
    grain_total = grain_lbs * grain_cost_per_lb

    # Hops cost (0.5 oz/gal typical for a balanced recipe)
    hops_oz = gallons * 0.5
    hops_total = hops_oz * hops_cost_per_oz

    # Yeast cost — one pitch per batch
    yeast_total = yeast_cost_per_unit * 1.0

    # Packaging: 124 × 12-oz bottles per barrel (standard)
    bottles_per_barrel = 124
    total_bottles = int(batch_size_barrels * bottles_per_barrel)
    packaging_total = total_bottles * packaging_cost_per_unit

    # Finings
    finings_total = FININGS_COST * FININGS_PER_BATCH

    # ── Totals ────────────────────────────────────────────────────────────
    ingredient_costs = {
        "grain":   {"qty": round(grain_lbs, 2), "unit": "lb",  "cost": round(grain_total, 2)},
        "hops":    {"qty": round(hops_oz, 2),   "unit": "oz",  "cost": round(hops_total, 2)},
        "yeast":   {"qty": 1,                    "unit": "unit","cost": round(yeast_total, 2)},
        "packaging":{"qty": total_bottles,       "unit": "bottles","cost": round(packaging_total, 2)},
        "finings": {"qty": FININGS_PER_BATCH,    "unit": "unit","cost": round(finings_total, 2)},
    }

    total_ingredient_cost = round(
        grain_total + hops_total + yeast_total + packaging_total + finings_total, 2
    )

    total_cost = total_ingredient_cost  # extend here with labour, overhead, etc.

    cost_per_barrel = round(total_cost / batch_size_barrels, 2) if batch_size_barrels else 0.0

    # Recommended selling price with margin
    recommended_price_per_barrel = round(total_cost * (1 + margin_percent / 100) / batch_size_barrels, 2)

    return {
        "batch_size_barrels": batch_size_barrels,
        "gallons": gallons,
        "ingredient_costs": ingredient_costs,
        "total_cost": total_cost,
        "cost_per_barrel": cost_per_barrel,
        "margin_percent": margin_percent,
        "recommended_price_per_barrel": recommended_price_per_barrel,
    }


def print_report(result: dict) -> None:
    """Pretty-print the batch calculation report."""
    print("=" * 64)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("  Inspired by tfrayner/beerfestdb — CBF_beer_price_calculator.py")
    print("=" * 64)

    print(f"\n── Batch Parameters ──────────────────────────────────────")
    print(f"  Batch size:          {result['batch_size_barrels']} barrels ({result['gallons']:.0f} US gal)")
    print(f"  Margin:              {result['margin_percent']:.1f}%")

    print(f"\n── Ingredient Costs ──────────────────────────────────────")
    for name, details in result["ingredient_costs"].items():
        print(f"  {name.capitalize():<12} {details['qty']:>8.2f} {details['unit']:<8} → ${details['cost']:>8.2f}")

    print(f"\n── Totals ────────────────────────────────────────────────")
    print(f"  Total batch cost:       ${result['total_cost']:>10.2f}")
    print(f"  Cost per barrel:        ${result['cost_per_barrel']:>10.2f}")
    print(f"  Recommended sale/bbl:   ${result['recommended_price_per_barrel']:>10.2f}  "
          f"(includes {result['margin_percent']:.0f}% margin)")

    print(f"\n{'=' * 64}")


# ── Run with sample batch ───────────────────────────────────────────────────
if __name__ == "__main__":
    result = calculate_ingredient_costs(
        grain_cost_per_lb=GRAIN_COST_PER_LB,
        hops_cost_per_oz=HOPS_COST_PER_OZ,
        yeast_cost_per_unit=YEAST_COST_PER_UNIT,
        packaging_cost_per_unit=PACKAGING_COST_PER_UNIT,
        batch_size_barrels=BATCH_SIZE_BARRELS,
        margin_percent=MARGIN_PERCENT,
    )
    print_report(result)
