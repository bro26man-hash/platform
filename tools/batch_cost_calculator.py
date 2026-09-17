#!/usr/bin/env python3
"""
batch_cost_calculator.py
========================
A craft brewery batch cost calculator inspired by tfrayner/beerfestdb's
CBF_beer_price_calculator.py (which prices beer based on ABV or cask cost,
whichever is greater).

This CLI version computes the total cost of a single production batch from
raw ingredient inputs, derives the cost per barrel, and applies a configurable
margin to recommend a selling price per barrel.

Reference: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py
"""

from dataclasses import dataclass, field

# A standard US beer barrel = 31 US gallons.
BARREL_TO_GALLONS = 31.0
# Ounces per gallon (for hopping rates expressed in oz/gal).
OUNCE_PER_GALLON = 128.0


@dataclass
class IngredientCosts:
    """Per-unit cost inputs for a single batch."""
    grain_per_lb: float = 0.0        # $ / lb of grain
    hops_per_oz: float = 0.0         # $ / oz of hops
    yeast_per_unit: float = 0.0      # $ / unit of yeast
    packaging_per_unit: float = 0.0  # $ / unit of packaging (bottles/kegs)


@dataclass
class BatchInputs:
    """Full set of inputs describing one production batch."""
    batch_size_barrels: float             # size of the batch in barrels
    grain_lbs: float                      # total grain used in the batch (lbs)
    hops_oz: float                        # total hops used in the batch (oz)
    yeast_units: float = 1.0              # yeast units (packs/liquid yeast)
    packaging_units: float = 0.0          # packaging units (bottles or kegs)
    margin_percent: float = 30.0          # target margin as a percentage
    costs: IngredientCosts = field(default_factory=IngredientCosts)


class BatchCostCalculator:
    """Compute batch cost, cost-per-barrel, and recommended sale price."""

    def __init__(self, inputs: BatchInputs):
        self.inputs = inputs

    # -- Component costs ----------------------------------------------------
    def grain_cost(self) -> float:
        return self.inputs.grain_lbs * self.inputs.costs.grain_per_lb

    def hops_cost(self) -> float:
        return self.inputs.hops_oz * self.inputs.costs.hops_per_oz

    def yeast_cost(self) -> float:
        return self.inputs.yeast_units * self.inputs.costs.yeast_per_unit

    def packaging_cost(self) -> float:
        return self.inputs.packaging_units * self.inputs.costs.packaging_per_unit

    def total_ingredient_cost(self) -> float:
        return (self.grain_cost() + self.hops_cost()
                + self.yeast_cost() + self.packaging_cost())

    # -- Per-barrel maths ---------------------------------------------------
    def total_cost(self) -> float:
        """Total cost of the entire batch (USD)."""
        return self.total_ingredient_cost()

    def cost_per_barrel(self) -> float:
        """Cost attributed to a single barrel."""
        if self.inputs.batch_size_barrels <= 0:
            raise ValueError("batch_size_barrels must be greater than zero")
        return self.total_cost() / self.inputs.batch_size_barrels

    def recommended_price_per_barrel(self) -> float:
        """Sale price per barrel after applying the target margin."""
        margin = self.inputs.margin_percent / 100.0
        return self.cost_per_barrel() * (1.0 + margin)

    # -- Report -------------------------------------------------------------
    def report(self) -> str:
        lines = []
        lines.append("=" * 55)
        lines.append("       CRAFT BREWERY BATCH COST CALCULATOR")
        lines.append("=" * 55)
        b = self.inputs
        lines.append(f"Batch size          : {b.batch_size_barrels:.2f} bbl "
                     f"({b.batch_size_barrels * BARREL_TO_GALLONS:.0f} gal)")
        lines.append(f"Grain               : {b.grain_lbs:.1f} lbs @ "
                     f"${b.costs.grain_per_lb:.3f}/lb")
        lines.append(f"Hops                : {b.hops_oz:.1f} oz @ "
                     f"${b.costs.hops_per_oz:.3f}/oz")
        lines.append(f"Yeast               : {b.yeast_units:.1f} units @ "
                     f"${b.costs.yeast_per_unit:.3f}/unit")
        lines.append(f"Packaging           : {b.packaging_units:.0f} units @ "
                     f"${b.costs.packaging_per_unit:.3f}/unit")
        lines.append(f"Target margin       : {b.margin_percent:.1f}%")
        lines.append("-" * 55)
        lines.append(f"Grain cost          : ${self.grain_cost():,.2f}")
        lines.append(f"Hops cost           : ${self.hops_cost():,.2f}")
        lines.append(f"Yeast cost          : ${self.yeast_cost():,.2f}")
        lines.append(f"Packaging cost      : ${self.packaging_cost():,.2f}")
        lines.append("-" * 55)
        lines.append(f"TOTAL BATCH COST    : ${self.total_cost():,.2f}")
        lines.append(f"COST PER BARREL     : ${self.cost_per_barrel():,.2f}")
        lines.append(f"REC. SELL PRICE/bbl : ${self.recommended_price_per_barrel():,.2f}")
        lines.append("=" * 55)
        return "\n".join(lines)


def run_sample():
    """Run the calculator against a representative sample batch."""
    sample = BatchInputs(
        batch_size_barrels=10.0,
        grain_lbs=600.0,
        hops_oz=16.0,
        yeast_units=4.0,
        packaging_units=228.0,   # 228 bottles for 10 bbl
        margin_percent=30.0,
        costs=IngredientCosts(
            grain_per_lb=1.60,
            hops_per_oz=8.50,
            yeast_per_unit=1.25,
            packaging_per_unit=0.30,
        ),
    )
    calc = BatchCostCalculator(sample)
    print(calc.report())


if __name__ == "__main__":
    run_sample()
