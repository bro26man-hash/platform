# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by tfrayner/beerfestdb - CBF_beer_price_calculator.py
# Computes total batch cost, cost-per-barrel, and recommended selling price
# based on a configurable margin percentage.


def calculate_batch_cost(
    grain_cost_per_lb: float,
    hops_cost_per_oz: float,
    yeast_cost_per_unit: float,
    packaging_cost_per_unit: float,
    grain_lbs: float,
    hops_oz: float,
    yeast_units: float,
    packaging_units: int,
    batch_size_barrels: float,
    margin_percent: float,
) -> dict:
    """
    Calculate the total cost, cost per barrel, and recommended selling price
    for a craft brewery batch.

    Parameters
    ----------
    grain_cost_per_lb : float  - price of grain per pound ($)
    hops_cost_per_oz   : float  - price of hops per ounce ($)
    yeast_cost_per_unit: float  - price of yeast per unit ($)
    packaging_cost_per_unit : float - price of packaging per unit ($)
    grain_lbs          : float  - pounds of grain used in the batch
    hops_oz            : float  - ounces of hops used in the batch
    yeast_units        : float  - number of yeast units used
    packaging_units    : int    - number of packaging units (bottles/cans/kegs)
    batch_size_barrels : float  - batch size in barrels (1 barrel = 31 US gallons)
    margin_percent     : float  - desired margin percentage (e.g. 30 for 30%)

    Returns
    -------
    dict with keys: grain_cost, hops_cost, yeast_cost, packaging_cost,
                    total_cost, cost_per_barrel, recommended_price_per_barrel
    """
    grain_cost = grain_cost_per_lb * grain_lbs
    hops_cost = hops_cost_per_oz * hops_oz
    yeast_cost = yeast_cost_per_unit * yeast_units
    packaging_cost = packaging_cost_per_unit * packaging_units

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost

    if batch_size_barrels <= 0:
        raise ValueError("batch_size_barrels must be greater than zero.")

    cost_per_barrel = total_cost / batch_size_barrels
    # Recommended selling price = cost_per_barrel * (1 + margin/100)
    recommended_price_per_barrel = cost_per_barrel * (1 + margin_percent / 100)

    return {
        "grain_cost": round(grain_cost, 2),
        "hops_cost": round(hops_cost, 2),
        "yeast_cost": round(yeast_cost, 2),
        "packaging_cost": round(packaging_cost, 2),
        "total_cost": round(total_cost, 2),
        "cost_per_barrel": round(cost_per_barrel, 2),
        "recommended_price_per_barrel": round(recommended_price_per_barrel, 2),
        "margin_percent": margin_percent,
        "batch_size_barrels": batch_size_barrels,
    }


def print_batch_report(results: dict) -> None:
    """Print a formatted cost breakdown report."""
    print("=" * 60)
    print("   CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"\n  Batch size            : {results['batch_size_barrels']} barrels")
    print(f"  Margin                : {results['margin_percent']}%")
    print("-" * 60)
    print("  INGREDIENT / MATERIAL COSTS")
    print("-" * 60)
    print(f"  Grain cost            : ${results['grain_cost']:.2f}")
    print(f"  Hops cost             : ${results['hops_cost']:.2f}")
    print(f"  Yeast cost            : ${results['yeast_cost']:.2f}")
    print(f"  Packaging cost        : ${results['packaging_cost']:.2f}")
    print("-" * 60)
    print("  SUMMARY")
    print("-" * 60)
    print(f"  Total batch cost      : ${results['total_cost']:.2f}")
    print(f"  Cost per barrel       : ${results['cost_per_barrel']:.2f}")
    print(f"  Recommended sale price: ${results['recommended_price_per_barrel']:.2f} / barrel")
    print("=" * 60)


if __name__ == "__main__":
    # Sample batch inputs
    sample = {
        "grain_cost_per_lb": 1.50,    # $/lb
        "hops_cost_per_oz": 0.80,     # $/oz
        "yeast_cost_per_unit": 5.00,  # $/unit
        "packaging_cost_per_unit": 0.25,  # $/unit (caps/labels)
        "grain_lbs": 200,        # lbs
        "hops_oz": 30,           # oz
        "yeast_units": 2,        # units
        "packaging_units": 120,  # bottles/cans
        "batch_size_barrels": 5, # barrels
        "margin_percent": 35,    # 35% margin
    }

    results = calculate_batch_cost(**sample)
    print_batch_report(results)
