# batch_cost_calculator.py
"""
Craft Brewery Batch Cost Calculator
====================================
Calculates the total production cost, cost-per-barrel, and recommended
selling price per barrel for a craft beer batch.

Inspiration: tfrayner/beerfestdb — CBF_beer_price_calculator.py
  (cost-based pricing with margin, similar to the reference's approach
   of computing cost_price and applying a coefficient to derive sale price).
"""

from dataclasses import dataclass, field
from typing import Optional


# ── Constants ───────────────────────────────────────────────────────────────
BARREL_TO_GALLONS = 31.0        # US fluid gallons per barrel
BARREL_TO_LITERS  = 159.0       # litres per barrel (approx)


@dataclass
class BatchIngredients:
    """Per-batch ingredient and packaging quantities and unit costs."""
    grain_lbs      : float = 0.0   # pounds of malt/grain
    grain_cost_lb  : float = 0.0   # $ per pound
    hops_oz        : float = 0.0   # ounces of hops
    hops_cost_oz   : float = 0.0   # $ per ounce
    yeast_units    : float = 1.0   # number of yeast packets/units
    yeast_cost_unit: float = 0.0   # $ per unit
    packaging_units: float = 0.0   # bottles / cans / kegs
    packaging_cost_unit: float = 0.0  # $ per packaging unit


@dataclass
class BatchConfig:
    """Batch size and pricing margin."""
    batch_size_barrels : float = 5.0       # batch size in US barrels
    margin_percent     : float = 30.0      # markup on cost (%)


class BatchCostCalculator:
    """
    Compute total cost, cost-per-barrel, and recommended selling price
    for a single production batch.
    """

    def __init__(self, ingredients: BatchIngredients, config: BatchConfig):
        self.ingredients = ingredients
        self.config      = config

    # ── Individual cost lines ────────────────────────────────────────────
    @property
    def grain_cost(self)      -> float: return self.ingredients.grain_lbs * self.ingredients.grain_cost_lb
    @property
    def hops_cost(self)       -> float: return self.ingredients.hops_oz * self.ingredients.hops_cost_oz
    @property
    def yeast_cost(self)      -> float: return self.ingredients.yeast_units * self.ingredients.yeast_cost_unit
    @property
    def packaging_cost(self)  -> float: return self.ingredients.packaging_units * self.ingredients.packaging_cost_unit
    @property
    def total_cost(self)      -> float:
        return self.grain_cost + self.hops_cost + self.yeast_cost + self.packaging_cost

    @property
    def cost_per_barrel(self) -> float:
        if self.config.batch_size_barrels == 0:
            return 0.0
        return self.total_cost / self.config.batch_size_barrels

    @property
    def margin_multiplier(self) -> float:
        return 1.0 + (self.config.margin_percent / 100.0)

    @property
    def recommended_price_per_barrel(self) -> float:
        """Selling price = cost-per-barrel × (1 + margin%)."""
        return self.cost_per_barrel * self.margin_multiplier

    @property
    def total_recommended_revenue(self) -> float:
        """Total revenue if entire batch is sold at recommended price."""
        return self.recommended_price_per_barrel * self.config.batch_size_barrels

    # ── Display helpers ─────────────────────────────────────────────────
    def print_summary(self) -> None:
        print("=" * 60)
        print("  CRAFT BREWERY BATCH COST CALCULATOR")
        print("=" * 60)

        print(f"\n📦  BATCH SIZE:            {self.config.batch_size_barrels:.1f} barrels")
        print(f"   (≈ {self.config.batch_size_barrels * BARREL_TO_GALLONS:.0f} gal / "
              f"{self.config.batch_size_barrels * BARREL_TO_LITERS:.0f} L)")

        print("\n🌾  INGREDIENT & PACKAGING BREAKDOWN")
        print(f"   Grain       : {self.ingredients.grain_lbs:.1f} lb × "
              f"${self.ingredients.grain_cost_lb:.3f}/lb  =  ${self.grain_cost:.2f}")
        print(f"   Hops        : {self.ingredients.hops_oz:.1f} oz × "
              f"${self.ingredients.hops_cost_oz:.3f}/oz   =  ${self.hops_cost:.2f}")
        print(f"   Yeast       : {self.ingredients.yeast_units:.1f} units × "
              f"${self.ingredients.yeast_cost_unit:.3f}/unit =  ${self.yeast_cost:.2f}")
        print(f"   Packaging   : {self.ingredients.packaging_units:.1f} units × "
              f"${self.ingredients.packaging_cost_unit:.3f}/unit =  ${self.packaging_cost:.2f}")

        print("\n💰  COST SUMMARY")
        print(f"   Total Production Cost        :  ${self.total_cost:.2f}")
        print(f"   Cost per Barrel              :  ${self.cost_per_barrel:.2f}")

        print(f"\n📈  PRICING")
        print(f"   Margin Percentage            :  {self.config.margin_percent:.1f}%")
        print(f"   Recommended Price / Barrel   :  ${self.recommended_price_per_barrel:.2f}")
        print(f"   Est. Total Revenue (full btch): ${self.total_recommended_revenue:.2f}")
        print(f"   Gross Profit                 :  ${self.total_recommended_revenue - self.total_cost:.2f}")

        print("\n" + "=" * 60)


# ═══════════════════════════════════════════════════════════════════════════
# SAMPLE RUN — 5-barrel IPA batch
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    # Sample 5-barrel batch ingredients (typical American IPA)
    sample_ingredients = BatchIngredients(
        grain_lbs       = 120.0,   # ~120 lbs of malt for 5 bbl
        grain_cost_lb   = 0.85,    # $0.85 / lb
        hops_oz         = 25.0,    # ~25 oz of hops (Citra, Mosaic, etc.)
        hops_cost_oz    = 12.00,   # $12.00 / oz
        yeast_units     = 4.0,     # 4 packets of liquid yeast
        yeast_cost_unit = 8.50,    # $8.50 / packet
        packaging_units = 660,     # 660 cans (approx 5 bbl)
        packaging_cost_unit = 0.45  # $0.45 / can
    )

    sample_config = BatchConfig(
        batch_size_barrels = 5.0,
        margin_percent     = 30.0   # 30% margin
    )

    calculator = BatchCostCalculator(sample_ingredients, sample_config)
    calculator.print_summary()

    # ── Assertions to validate correctness ──────────────────────────────
    assert abs(calculator.grain_cost      - 102.00) < 0.01,  f"grain: {calculator.grain_cost}"
    assert abs(calculator.hops_cost       - 300.00) < 0.01,  f"hops: {calculator.hops_cost}"
    assert abs(calculator.yeast_cost      - 34.00)  < 0.01,  f"yeast: {calculator.yeast_cost}"
    assert abs(calculator.packaging_cost  - 297.00) < 0.01,  f"packaging: {calculator.packaging_cost}"
    assert abs(calculator.total_cost      - 733.00) < 0.01,  f"total: {calculator.total_cost}"
    assert abs(calculator.cost_per_barrel - 146.60) < 0.01,  f"cpb: {calculator.cost_per_barrel}"
    assert abs(calculator.recommended_price_per_barrel - 190.58) < 0.05, \
        f"rppb: {calculator.recommended_price_per_barrel}"

    print("\n✅  All assertions passed — calculations verified correct.")
