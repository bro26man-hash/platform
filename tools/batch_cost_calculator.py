# batch_cost_calculator.py
# Craft Brewery Batch Cost Calculator
# Inspired by tfrayner/beerfestdb — CBF_beer_price_calculator.py
# https://github.com/tfrayner/beerfestdb/blob/master/tool_dashboard/CBF_beer_price_calculator.py
#
# The reference calculator derives a "cost price" from cask volume and price,
# then applies a sale coefficient.  Our version does the same idea at the batch
# level: total ingredient/packaging cost → cost-per-barrel → apply margin →
# recommended selling price per barrel.

from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Configuration constants (mirroring the "coefficients" in the reference)
# ---------------------------------------------------------------------------

# A standard US beer barrel = 31 US gallons = 58.67 litres
BARREL_TO_GALLONS = 31.0
BARREL_TO_LITRES = 58.67

# Default ingredient usage rates per barrel (homebrew-style all-grain)
DEFAULT_GRAIN_PER_BARREL_LB = 20.0    # lbs of malt per barrel
DEFAULT_HOPS_PER_BARREL_OZ = 1.0      # oz of hops per barrel
DEFAULT_YEAST_PER_BATCH_UNITS = 1.0   # one yeast packet/liquid culture per batch
DEFAULT_PACKAGING_PER_BARREL_UNITS = 1.0  # one bottle/can/bag per barrel


@dataclass
class BatchCostCalculator:
    """
    Calculate the total cost, cost-per-barrel, and recommended selling price
    for a single brewing batch.

    The logic is inspired by the beerfestdb calculator which computes:
        cost_price  = (cask_price / litres_per_cask) * sale_coefficient
        sale_price  = max(abv_price, cost_price)  rounded to nearest 20p

    Here we compute:
        total_cost       = grain_cost + hops_cost + yeast_cost + packaging_cost
        cost_per_barrel  = total_cost / batch_size_barrels
        sale_price_per_barrel = cost_per_barrel * (1 + margin_pct / 100)
    """

    # --- Batch parameters ---
    batch_size_barrels: float = 5.0  # a standard 5-gallon homebrew batch ≈ 0.159 bbl

    # --- Ingredient unit costs ---
    grain_cost_per_lb: float = 2.50
    hops_cost_per_oz: float = 1.25
    yeast_cost_per_unit: float = 5.00
    packaging_cost_per_unit: float = 0.75

    # --- Ingredient usage rates (per barrel, except yeast which is per batch) ---
    grain_lb_per_barrel: float = DEFAULT_GRAIN_PER_BARREL_LB
    hops_oz_per_barrel: float = DEFAULT_HOPS_PER_BARREL_OZ
    yeast_units_per_batch: float = DEFAULT_YEAST_PER_BATCH_UNITS
    packaging_units_per_barrel: float = DEFAULT_PACKAGING_PER_BARREL_UNITS

    # --- Pricing ---
    margin_pct: float = 30.0  # 30% margin

    # --- Results (populated after calculate) ---
    total_cost: float = 0.0
    cost_per_barrel: float = 0.0
    recommended_price_per_barrel: float = 0.0

    # ------------------------------------------------------------------
    def calculate(self) -> None:
        """Run all cost calculations and store results on the instance."""

        # Ingredient costs
        grain_cost = self.grain_lb_per_barrel * self.batch_size_barrels * self.grain_cost_per_lb
        hops_cost = self.hops_oz_per_barrel * self.batch_size_barrels * self.hops_cost_per_oz
        yeast_cost = self.yeast_units_per_batch * self.yeast_cost_per_unit
        packaging_cost = self.packaging_units_per_barrel * self.batch_size_barrels * self.packaging_cost_per_unit

        self.total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
        self.cost_per_barrel = self.total_cost / self.batch_size_barrels

        # Apply margin — same spirit as the reference's "sale coefficient"
        margin_multiplier = 1.0 + (self.margin_pct / 100.0)
        self.recommended_price_per_barrel = self.cost_per_barrel * margin_multiplier

        # Store intermediate values for display
        self._grain_cost = grain_cost
        self._hops_cost = hops_cost
        self._yeast_cost = yeast_cost
        self._packaging_cost = packaging_cost
        self._margin_multiplier = margin_multiplier

    # ------------------------------------------------------------------
    def summary(self) -> str:
        """Return a human-readable cost breakdown."""
        if not self.total_cost:
            self.calculate()

        lines = [
            "=" * 60,
            "  CRAFT BREWERY BATCH COST CALCULATOR",
            "=" * 60,
            f"\n  Batch size:            {self.batch_size_barrels:.2f} barrels "
            f"({self.batch_size_barrels * BARREL_TO_GALLONS:.1f} gal / {self.batch_size_barrels * BARREL_TO_LITRES:.1f} L)",
            f"\n  --- Ingredient Costs ---",
            f"  Grain:                 {self.grain_lb_per_barrel:.1f} lb/bbl × {self.batch_size_barrels:.2f} bbl "
            f"@ ${self.grain_cost_per_lb:.2f}/lb  =  ${self._grain_cost:.2f}",
            f"  Hops:                  {self.hops_oz_per_barrel:.2f} oz/bbl × {self.batch_size_barrels:.2f} bbl "
            f"@ ${self.hops_cost_per_oz:.2f}/oz   =  ${self._hops_cost:.2f}",
            f"  Yeast:                 {self.yeast_units_per_batch:.1f} units/batch "
            f"@ ${self.yeast_cost_per_unit:.2f}/unit             =  ${self._yeast_cost:.2f}",
            f"  Packaging:             {self.packaging_units_per_barrel:.1f} units/bbl × {self.batch_size_barrels:.2f} bbl "
            f"@ ${self.packaging_cost_per_unit:.2f}/unit =  ${self._packaging_cost:.2f}",
            f"\n  --- Totals ---",
            f"  Total Batch Cost:      ${self.total_cost:.2f}",
            f"  Cost per Barrel:       ${self.cost_per_barrel:.2f}",
            f"\n  --- Pricing ---",
            f"  Margin:                {self.margin_pct:.1f}%  (×{self._margin_multiplier:.2f})",
            f"  ★ Recommended Price:   ${self.recommended_price_per_barrel:.2f} / barrel",
            f"\n" + "=" * 60,
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Sample run — execute when the script is run directly
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n>>> SAMPLE RUN: 5-barrel batch, standard ingredient costs, 30% margin\n")

    calculator = BatchCostCalculator(
        batch_size_barrels=5.0,
        grain_cost_per_lb=2.50,
        hops_cost_per_oz=1.25,
        yeast_cost_per_unit=5.00,
        packaging_cost_per_unit=0.75,
        grain_lb_per_barrel=20.0,
        hops_oz_per_barrel=1.0,
        yeast_units_per_batch=1.0,
        packaging_units_per_barrel=1.0,
        margin_pct=30.0,
    )

    print(calculator.summary())

    # ------------------------------------------------------------------
    # Additional validation: test with different parameters
    # ------------------------------------------------------------------
    print("\n\n>>> VALIDATION: 10-barrel batch, premium ingredients, 40% margin\n")

    premium = BatchCostCalculator(
        batch_size_barrels=10.0,
        grain_cost_per_lb=4.00,
        hops_cost_per_oz=3.50,
        yeast_cost_per_unit=12.00,
        packaging_cost_per_unit=1.50,
        grain_lb_per_barrel=22.0,
        hops_oz_per_barrel=1.5,
        yeast_units_per_batch=2.0,
        packaging_units_per_barrel=1.0,
        margin_pct=40.0,
    )

    print(premium.summary())

    # ------------------------------------------------------------------
    # Assertions to confirm correctness
    # ------------------------------------------------------------------
    print("\n\n>>> RUNNING ASSERTIONS...")

    # Manual calculation for the sample:
    #   grain:  20 lb/bbl × 5 bbl × $2.50 = $250.00
    #   hops:   1 oz/bbl × 5 bbl × $1.25  = $6.25
    #   yeast:  1 unit × $5.00              = $5.00
    #   packaging: 1 unit/bbl × 5 bbl × $0.75 = $3.75
    #   total = 250 + 6.25 + 5 + 3.75 = $265.00
    #   cost/bbl = 265 / 5 = $53.00
    #   price/bbl = 53 × 1.30 = $68.90

    assert abs(calculator.total_cost - 265.00) < 0.01, f"Expected 265.00, got {calculator.total_cost}"
    assert abs(calculator.cost_per_barrel - 53.00) < 0.01, f"Expected 53.00, got {calculator.cost_per_barrel}"
    assert abs(calculator.recommended_price_per_barrel - 68.90) < 0.01, \
        f"Expected 68.90, got {calculator.recommended_price_per_barrel}"

    # Premium batch manual check:
    #   grain:  22 × 10 × 4.00 = 880
    #   hops:   1.5 × 10 × 3.50 = 52.50
    #   yeast:  2 × 12.00 = 24.00
    #   packaging: 1 × 10 × 1.50 = 15.00
    #   total = 880 + 52.50 + 24 + 15 = 971.50
    #   cost/bbl = 97.15
    #   price/bbl = 97.15 × 1.40 = 136.01
    assert abs(premium.total_cost - 971.50) < 0.01, f"Expected 971.50, got {premium.total_cost}"
    assert abs(premium.cost_per_barrel - 97.15) < 0.01, f"Expected 97.15, got {premium.cost_per_barrel}"
    assert abs(premium.recommended_price_per_barrel - 136.01) < 0.01, \
        f"Expected 136.01, got {premium.recommended_price_per_barrel}"

    print("✓ All assertions passed! Calculator is correct.\n")
