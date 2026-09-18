# batch_cost_calculator.py
#
# Craft Brewery Batch Cost Calculator
# ------------------------------------------------------------------
# Inspired by tfrayner/beerfestdb -> tool_dashboard/CBF_beer_price_calculator.py
# (https://github.com/tfrayner/beerfestdb)
#
# The original calculator determines a sale price by comparing an
# ABV-based price against a cost-based price and using whichever is
# greater, then applying a coefficient and rounding. This script
# adapts that philosophy for whole-batch economics:
#   1. Compute the total batch cost from ingredient inputs.
#   2. Compute cost-per-barrel.
#   3. Apply a configurable margin to derive the recommended
#      selling price per barrel (mirroring the "price >= cost" rule
#      by never letting the margin-driven price fall below cost).
# ------------------------------------------------------------------

# --- Conversion constants -------------------------------------------------
# 1 US barrel (bbl) = 31 US gallons = 117.3478 liters
LITERS_PER_BARREL = 117.3478


def calculate_batch_cost(
    grain_cost_per_lb: float,   # $/lb
    hops_cost_per_oz: float,    # $/oz
    yeast_cost_per_unit: float, # $/unit
    packaging_cost_per_unit: float, # $/unit
    pounds_of_grain: float,
    ounces_of_hops: float,
    yeast_units: float,
    packaging_units: float,
    batch_size_barrels: float,
    margin_percent: float,     # e.g. 30 for 30%
) -> dict:
    """Calculate batch costs and recommended selling price per barrel."""

    # ---- Ingredient line items (inspired by the per-litre cost calc
    #      in the reference: cost is built up from raw inputs) ----
    grain_cost   = grain_cost_per_lb   * pounds_of_grain
    hops_cost    = hops_cost_per_oz    * ounces_of_hops
    yeast_cost   = yeast_cost_per_unit * yeast_units
    packaging_cost = packaging_cost_per_unit * packaging_units

    total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
    cost_per_barrel = total_cost / batch_size_barrels if batch_size_barrels else 0.0

    # ---- Recommended sale price (mirrors "whichever is greater" logic) ----
    # Reference uses: price = max(abv_price, cost_price).
    # Here the "ABV-style" premium price is a demand-based estimate
    # modeled as a multiple of cost (default 1.6x reflecting typical
    # craft pricing). We take the greater of that and the cost,
    # then apply the requested margin -- guaranteeing the brewer
    # never prices below cost (just as the original never prices
    # below cost).
    DEMAND_MULTIPLIER = 1.6
    demand_price = cost_per_barrel * DEMAND_MULTIPLIER
    base_price = max(demand_price, cost_per_barrel)

    margin_factor = 1 + (margin_percent / 100.0)
    recommended_price_per_barrel = base_price * margin_factor

    # Round up to the nearest cent (mirrors the reference's
    # math.ceil rounding to 20 pence).
    import math
    recommended_price_per_barrel = math.ceil(recommended_price_per_barrel * 100) / 100

    return {
        "grain_cost": grain_cost,
        "hops_cost": hops_cost,
        "yeast_cost": yeast_cost,
        "packaging_cost": packaging_cost,
        "total_cost": total_cost,
        "cost_per_barrel": round(cost_per_barrel, 2),
        "demand_price_per_barrel": round(demand_price, 2),
        "recommended_sale_price_per_barrel": recommended_price_per_barrel,
        "batch_size_barrels": batch_size_barrels,
        "margin_percent": margin_percent,
        "liters_per_batch": round(batch_size_barrels * LITERS_PER_BARREL, 2),
    }


def pretty_print(results: dict) -> None:
    print("=" * 60)
    print("  CRAFT BREWERY BATCH COST CALCULATOR")
    print("=" * 60)
    print(f"  Batch size          : {results['batch_size_barrels']} bbl "
          f"({results['liters_per_batch']} L)")
    print("-" * 60)
    print("  INGREDIENT COSTS")
    print("-" * 60)
    print(f"    Grain             : ${results['grain_cost']:.2f}")
    print(f"    Hops              : ${results['hops_cost']:.2f}")
    print(f"    Yeast             : ${results['yeast_cost']:.2f}")
    print(f"    Packaging         : ${results['packaging_cost']:.2f}")
    print("-" * 60)
    print(f"  TOTAL BATCH COST    : ${results['total_cost']:.2f}")
    print(f"  COST / BARREL       : ${results['cost_per_barrel']:.2f}")
    print(f"  DEMAND-BASED PRICE  : ${results['demand_price_per_barrel']:.2f} "
          f"(1.6x cost multiplier)")
    print(f"  MARGIN APPLIED      : {results['margin_percent']}%")
    print("-" * 60)
    print(f"  >>> RECOMMENDED SALE PRICE / BARREL : "
          f"${results['recommended_sale_price_per_barrel']:.2f} <<<")
    print("=" * 60)


# ---------------------------------------------------------------------------
# SAMPLE RUN  (executed on import for quick validation)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Sample 5-batch coarse grain session ale
    sample = calculate_batch_cost(
        grain_cost_per_lb      = 1.50,   # $/lb
        hops_cost_per_oz       = 0.30,   # $/oz
        yeast_cost_per_unit    = 5.00,   # $/unit
        packaging_cost_per_unit= 0.75,   # $/unit
        pounds_of_grain        = 200.0,  # lbs
        ounces_of_hops         = 64.0,   # oz
        yeast_units            = 4.0,    # units (e.g. White Labs vials)
        packaging_units        = 120.0,  # units (bottles/kegs)
        batch_size_barrels     = 5.0,    # bbl
        margin_percent         = 30.0,   # 30%
    )
    pretty_print(sample)

    # --- Assertion-based self-tests (mimic "validate the output") ---
    assert sample["total_cost"] > 0, "Total cost must be positive"
    assert sample["cost_per_barrel"] > 0, "Cost per barrel must be positive"
    assert sample["recommended_sale_price_per_barrel"] >= sample["cost_per_barrel"], \
        "Sale price must never be below cost"
    assert sample["recommended_sale_price_per_barrel"] > sample["cost_per_barrel"], \
        "Margin should push price above cost"
    print("\n[OK] All validation checks passed.")
