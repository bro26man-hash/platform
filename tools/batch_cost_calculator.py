"""
Craft Brewery Batch Cost Calculator

Calculates total batch cost, cost per barrel, and the recommended selling
price per barrel given a configurable target margin.

Ingredients priced per unit:
  - Grain ($/lb)
  - Hops ($/oz)
  - Yeast ($/unit)
  - Packaging ($/unit)

Batch size is expressed in barrels. Inspired by the CBF beer price
calculator logic in tfrayner/beerfestdb.

Reference: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py
"""

def get_positive_float(prompt: str) -> float:
    """Read a non-negative float from stdin, reprompting on bad input."""
    while True:
        try:
            val = float(input(prompt).strip())
            if val < 0:
                print("Please enter a non-negative number.")
                continue
            return val
        except ValueError:
            print("Invalid input. Please enter a number.")


def calculate_batch(
    grain_cost_per_lb: float,
    grain_lbs: float,
    hops_cost_per_oz: float,
    hops_oz: float,
    yeast_cost_per_unit: float,
    yeast_units: float,
    packaging_cost_per_unit: float,
    packaging_units: float,
    batch_size_bbls: float,
    margin_pct: float,
) -> dict:
    """Return per-item, total, per-barrel, and margin-adjusted sale price."""
    grain = grain_cost_per_lb * grain_lbs
    hops = hops_cost_per_oz * hops_oz
    yeast = yeast_cost_per_unit * yeast_units
    packaging = packaging_cost_per_unit * packaging_units
    total = grain + hops + yeast + packaging
    if batch_size_bbls <= 0:
        raise ValueError("Batch size must be greater than 0.")
    cost_per_barrel = total / batch_size_bbls
    selling_price_per_barrel = cost_per_barrel * (1 + margin_pct / 100.0)
    return {
        "grain": grain,
        "hops": hops,
        "yeast": yeast,
        "packaging": packaging,
        "total_cost": total,
        "cost_per_barrel": cost_per_barrel,
        "selling_price_per_barrel": selling_price_per_barrel,
        "margin_pct": margin_pct,
        "batch_size_bbls": batch_size_bbls,
    }


def print_report(r: dict) -> None:
    """Print a human-readable cost report."""
    print("=" * 50)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 50)
    print(f"  Batch size:        {r['batch_size_bbls']} bbl")
    print("-" * 50)
    print("  Ingredient costs:")
    print(f"    Grain:           ${r['grain']:.2f}")
    print(f"    Hops:            ${r['hops']:.2f}")
    print(f"    Yeast:           ${r['yeast']:.2f}")
    print(f"    Packaging:       ${r['packaging']:.2f}")
    print("-" * 50)
    print(f"  Total cost:        ${r['total_cost']:.2f}")
    print(f"  Cost per barrel:   ${r['cost_per_barrel']:.2f}")
    print(f"  Target margin:     {r['margin_pct']:.1f}%")
    print(f"  >> Sell price/bbl: ${r['selling_price_per_barrel']:.2f}")
    print("=" * 50)


if __name__ == "__main__":
    print("Welcome! Enter ingredient costs and batch details.\n")
    grain_pp = get_positive_float("Grain price per lb ($): ")
    grain_w = get_positive_float("Total grain weight (lb): ")
    hops_pp = get_positive_float("Hops price per oz ($): ")
    hops_w = get_positive_float("Total hops weight (oz): ")
    yeast_pc = get_positive_float("Yeast price per unit ($): ")
    yeast_q = get_positive_float("Number of yeast units: ")
    pack_pc = get_positive_float("Packaging price per unit ($): ")
    pack_q = get_positive_float("Number of packaging units: ")
    batch = get_positive_float("Batch size (barrels): ")
    margin = get_positive_float("Target margin percentage (e.g. 70): ")
    result = calculate_batch(
        grain_pp, grain_w, hops_pp, hops_w,
        yeast_pc, yeast_q, pack_pc, pack_q, batch, margin,
    )
    print_report(result)
