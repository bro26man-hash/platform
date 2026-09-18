# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
=====================================
Inspired by tfrayner/beerfestdb — CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb)

Computes total batch cost, cost per barrel, and a recommended
selling price per barrel based on a configurable margin.

Inputs
------
  - grain_cost      : $ / lb
  - hops_cost       : $ / oz
  - yeast_cost      : $ / unit (per fermentation cycle)
  - packaging_cost  : $ / unit (per keg / cask)
  - batch_size_bbl  : batch volume in US barrels (1 bbl = 31 US gal)
  - grain_lbs       : pounds of grain used
  - hops_oz         : ounces of hops used
  - yeast_units     : number of yeast units (packets/containers)
  - packaging_units : number of packaging units (kegs/casks)
  - margin_pct      : desired margin as a percentage (e.g. 30 = 30%)

Outputs
-------
  - total_cost          : raw cost of the batch
  - cost_per_barrel     : total_cost / batch_size_bbl
  - recommended_price   : cost_per_barrel * (1 + margin_pct/100)
"""

from dataclasses import dataclass


@dataclass
class BatchInputs:
    """All configurable inputs for a single brew batch."""
    grain_cost: float      = 0.50   # $/lb
    hops_cost: float       = 1.20   # $/oz
    yeast_cost: float      = 1.50   # $/unit
    packaging_cost: float  = 8.00   # $/unit (keg or cask)
    batch_size_bbl: float  = 5.0    # US barrels
    grain_lbs: float       = 100.0  # pounds of grain
    hops_oz: float         = 2.0    # ounces of hops
    yeast_units: int       = 1      # yeast packets/containers
    packaging_units: int   = 1      # kegs/casks
    margin_pct: float      = 30.0   # desired margin percentage


def calculate_batch_cost(inp: BatchInputs) -> dict:
    """Return a dict with all computed cost figures."""
    grain_total       = inp.grain_cost * inp.grain_lbs
    hops_total        = inp.hops_cost  * inp.hops_oz
    yeast_total       = inp.yeast_cost * inp.yeast_units
    packaging_total   = inp.packaging_cost * inp.packaging_units
    total_cost        = grain_total + hops_total + yeast_total + packaging_total

    if inp.batch_size_bbl <= 0:
        raise ValueError("batch_size_bbl must be greater than zero.")

    cost_per_barrel   = total_cost / inp.batch_size_bbl
    margin_multiplier = 1.0 + (inp.margin_pct / 100.0)
    recommended_price = cost_per_barrel * margin_multiplier

    return {
        "grain_total":      grain_total,
        "hops_total":       hops_total,
        "yeast_total":      yeast_total,
        "packaging_total":  packaging_total,
        "total_cost":       total_cost,
        "cost_per_barrel":  cost_per_barrel,
        "margin_pct":       inp.margin_pct,
        "recommended_price": recommended_price,
    }


def format_results(res: dict) -> str:
    """Pretty-print the calculation results."""
    lines = [
        "=" * 55,
        "      CRAFT BREWERY BATCH COST CALCULATOR",
        "=" * 55,
        "",
        "  INGREDIENT COSTS",
        "    Grain        :  ${:>8.2f}".format(res["grain_total"]),
        "    Hops         :  ${:>8.2f}".format(res["hops_total"]),
        "    Yeast        :  ${:>8.2f}".format(res["yeast_total"]),
        "    Packaging    :  ${:>8.2f}".format(res["packaging_total"]),
        "    -----------------------------",
        "    TOTAL COST   :  ${:>8.2f}".format(res["total_cost"]),
        "",
        "  PER-BARREL METRICS",
        "    Cost/Barrel  :  ${:>8.2f}".format(res["cost_per_barrel"]),
        "    Margin       :  {:>8.1f}%".format(res["margin_pct"]),
        "    Recommended  :  ${:>8.2f} / bbl".format(res["recommended_price"]),
        "",
        "=" * 55,
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    sample = BatchInputs(
        grain_cost=0.50,
        hops_cost=1.20,
        yeast_cost=1.50,
        packaging_cost=8.00,
        batch_size_bbl=5.0,
        grain_lbs=100.0,
        hops_oz=2.0,
        yeast_units=1,
        packaging_units=1,
        margin_pct=30.0,
    )

    results = calculate_batch_cost(sample)
    print(format_results(results))

    # Validation assertions
    assert results["grain_total"]        == 50.00
    assert results["hops_total"]         == 2.40
    assert results["yeast_total"]        == 1.50
    assert results["packaging_total"]    == 8.00
    assert results["total_cost"]         == 61.90
    assert abs(results["cost_per_barrel"] - 12.38) < 0.01
    assert abs(results["recommended_price"] - 16.094) < 0.01

    print("\n[OK] All assertions passed - calculator validated successfully!")
