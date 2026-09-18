# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Inspired by tfrayner/beerfestdb's CBF_beer_price_calculator.py
(https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py)

The original used ABV coefficients/constants and a "cost vs ABV price — take the
greater" approach. This standalone script adapts that philosophy: it lets you
configure ingredient costs, batch size, and a margin to compute the total batch
cost, cost per barrel, and a recommended selling price per barrel.

Reference:
    - ABV coefficient + constant model from the reference code (rows priced per
      litre, adjusted by an ABV premium).
    - "Whichever is greater" logic: we offer BOTH a cost-based floor and an
      ABV/premium-based price, then recommend the higher — mirroring the
      original max(abv_price, cost_price) pattern.
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Configuration ────────────────────────────────────────────────────────────
# Default coefficients inspired by the reference (pence-based, adapted to USD)
DEFAULT_ABV_COEFFICIENT = 0.70   # $ premium per ABV point (analogous to 70 pence)
DEFAULT_ABV_CONSTANT    = 2.30   # $ fixed ABV premium    (analogous to 230 pence)
DEFAULT_MARGIN_PERCENT  = 30.0   # 30 % margin on top of cost


@dataclass
class IngredientCosts:
    """Per-unit ingredient cost inputs."""
    grain_per_lb:   float = 0.0   # $ / lb
    hops_per_oz:    float = 0.0   # $ / oz
    yeast_per_unit: float = 0.0   # $ / unit (per pack/vial)
    packaging_per_unit: float = 0.0  # $ / unit (bottles, cans, caps …)


@dataclass
class BatchParams:
    """Batch sizing & usage parameters."""
    batch_size_barrels: float            # total batch volume in barrels (bbl)
    grain_lbs_per_bbl:  float = 25.0    # lbs of grain per barrel
    hops_oz_per_bbl:    float = 1.0     # oz of hops per barrel
    yeast_units_per_bbl: float = 1.0    # yeast packs per barrel
    packaging_units_per_bbl: float = 0.0 # packaging units per barrel (0 if included in yeast/pkging)
    abv:                float = 5.0     # ABV in percent (used for premium pricing)


class BatchCostCalculator:
    """
    Calculate total batch cost, cost per barrel, and recommended selling price.

    Pricing philosophy (carried over from the reference):
        - cost_price  = total ingredient cost / batch volume
        - abv_price   = abv_coefficient * ABV + abv_constant
        - floor_price = max(cost_price, abv_price)          # "whichever is greater"
        - sell_price  = floor_price * (1 + margin / 100)    # apply configurable margin
    """

    def __init__(
        self,
        ingredients: IngredientCosts,
        params: BatchParams,
        margin_percent: float = DEFAULT_MARGIN_PERCENT,
        abv_coefficient: float = DEFAULT_ABV_COEFFICIENT,
        abv_constant: float = DEFAULT_ABV_CONSTANT,
    ):
        self.ingredients   = ingredients
        self.params        = params
        self.margin_pct    = margin_percent
        self.abv_coef      = abv_coefficient
        self.abv_const     = abv_constant

    # ── Ingredient breakdown ─────────────────────────────────────────────────
    def grain_cost_total(self)   -> float:
        return self.ingredients.grain_per_lb * self.params.grain_lbs_per_bbl * self.params.batch_size_barrels

    def hops_cost_total(self)    -> float:
        return self.ingredients.hops_per_oz * self.params.hops_oz_per_bbl * self.params.batch_size_barrels

    def yeast_cost_total(self)   -> float:
        return self.ingredients.yeast_per_unit * self.params.yeast_units_per_bbl * self.params.batch_size_barrels

    def packaging_cost_total(self) -> float:
        return self.ingredients.packaging_per_unit * self.params.packaging_units_per_bbl * self.params.batch_size_barrels

    def total_batch_cost(self)   -> float:
        return (
            self.grain_cost_total()
            + self.hops_cost_total()
            + self.yeast_cost_total()
            + self.packaging_cost_total()
        )

    # ── Per-barrel calculations ──────────────────────────────────────────────
    def cost_per_barrel(self)    -> float:
        if self.params.batch_size_barrels <= 0:
            raise ValueError("Batch size must be greater than zero.")
        return self.total_batch_cost() / self.params.batch_size_barrels

    def abv_premium_price(self)  -> float:
        """ABV-based price per barrel (coefficient × ABV + constant)."""
        return self.abv_coef * self.params.abv + self.abv_const

    def floor_price_per_barrel(self) -> float:
        """Greater of cost-based or ABV-based price — mirrors the reference logic."""
        return max(self.cost_per_barrel(), self.abv_premium_price())

    # ── Recommended selling price ────────────────────────────────────────────
    def recommended_sell_price(self) -> float:
        """
        sell_price = floor_price × (1 + margin / 100)
        Captures the reference's philosophy of using the *greater* of cost or
        ABV premium as the floor, then applying a configurable margin.
        """
        return self.floor_price_per_barrel() * (1 + self.margin_pct / 100)

    # ── Pretty report ───────────────────────────────────────────────────────
    def report(self) -> str:
        lines = [
            "═══════════════════════════════════════════════════════════",
            "       CRAFT BREWERY BATCH COST CALCULATOR",
            "═══════════════════════════════════════════════════════════",
            "",
            "─── Batch Parameters ──────────────────────────────────────",
            f"  Batch size:            {self.params.batch_size_barrels:.1f} bbl",
            f"  ABV:                   {self.params.abv:.1f}%",
            f"  Grain usage:           {self.params.grain_lbs_per_bbl:.1f} lb/bbl",
            f"  Hops usage:            {self.params.hops_oz_per_bbl:.1f} oz/bbl",
            f"  Yeast usage:           {self.params.yeast_units_per_bbl:.1f} units/bbl",
            f"  Packaging usage:       {self.params.packaging_units_per_bbl:.1f} units/bbl",
            "",
            "─── Ingredient Costs ──────────────────────────────────────",
            f"  Grain:                 ${self.ingredients.grain_per_lb:.3f}/lb",
            f"  Hops:                  ${self.ingredients.hops_per_oz:.3f}/oz",
            f"  Yeast:                 ${self.ingredients.yeast_per_unit:.3f}/unit",
            f"  Packaging:             ${self.ingredients.packaging_per_unit:.3f}/unit",
            "",
            "─── Cost Breakdown ────────────────────────────────────────",
            f"  Grain cost (total):    ${self.grain_cost_total():,.2f}",
            f"  Hops cost (total):     ${self.hops_cost_total():,.2f}",
            f"  Yeast cost (total):    ${self.yeast_cost_total():,.2f}",
            f"  Packaging cost (total): ${self.packaging_cost_total():,.2f}",
            f"  ─────────────────────────────────────",
            f"  TOTAL BATCH COST:      ${self.total_batch_cost():,.2f}",
            f"  COST PER BARREL:        ${self.cost_per_barrel():,.2f}",
            "",
            "─── Pricing ───────────────────────────────────────────────",
            f"  ABV premium price:     ${self.abv_premium_price():,.2f}/bbl",
            f"  Floor price (max):     ${self.floor_price_per_barrel():,.2f}/bbl",
            f"  Margin:                {self.margin_pct:.1f}%",
            f"  ─────────────────────────────────────",
            f"  ★ RECOMMENDED SELL:    ${self.recommended_sell_price():,.2f}/bbl",
            "",
            "═══════════════════════════════════════════════════════════",
        ]
        return "\n".join(lines)


# ────────────────────────────────────────────────────────────────────────────
# SAMPLE RUN — a 10-barrel pale ale batch
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":

    ingredients = IngredientCosts(
        grain_per_lb=1.50,      # e.g. 2-row malt
        hops_per_oz=0.80,       # e.g. Cascade
        yeast_per_unit=2.50,    # e.g. Wyeast 1056
        packaging_per_unit=0.30, # bottles + caps
    )

    params = BatchParams(
        batch_size_barrels=10.0,
        grain_lbs_per_bbl=25.0,
        hops_oz_per_bbl=1.0,
        yeast_units_per_bbl=1.0,
        packaging_units_per_bbl=120.0,  # 120 bottles for 10 bbl
        abv=5.0,
    )

    calc = BatchCostCalculator(
        ingredients=ingredients,
        params=params,
        margin_percent=30.0,
        abv_coefficient=DEFAULT_ABV_COEFFICIENT,
        abv_constant=DEFAULT_ABV_CONSTANT,
    )

    print(calc.report())

    # ── Assertions for validation ────────────────────────────────────────────
    assert abs(calc.grain_cost_total()   - (1.50 * 25.0 * 10.0))   < 0.001
    assert abs(calc.hops_cost_total()    - (0.80 * 1.0  * 10.0))   < 0.001
    assert abs(calc.yeast_cost_total()   - (2.50 * 1.0  * 10.0))   < 0.001
    assert abs(calc.packaging_cost_total() - (0.30 * 120.0 * 10.0)) < 0.001
    assert abs(calc.total_batch_cost()   - (375.0 + 8.0 + 25.0 + 360.0)) < 0.001
    assert abs(calc.cost_per_barrel()    - (768.0 / 10.0))         < 0.001
    assert abs(calc.abv_premium_price()  - (0.70 * 5.0 + 2.30))    < 0.001   # = 5.80
    # floor = max(76.80, 5.80) = 76.80
    assert abs(calc.floor_price_per_barrel() - 76.80)               < 0.001
    # sell = 76.80 × 1.30 = 99.84
    assert abs(calc.recommended_sell_price() - 99.84)              < 0.001

    print("\n✅ All assertions passed — calculator validated!")
