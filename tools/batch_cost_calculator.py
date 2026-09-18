# batch_cost_calculator.py
# Inspired by tfrayner/beerfestdb (CBF_beer_price_calculator.py)
# Dual-pricing approach: cost-based vs. value-based, take the greater.

"""
Craft Brewery Batch Cost Calculator
====================================
Calculates the total cost of a brewing batch, the cost per barrel,
and -- using a configurable margin -- the recommended selling price
per barrel.  Inspired by the dual-pricing logic in
CBF_beer_price_calculator.py (beerfestdb) which compares an
ABV-based price against a cost-based price and uses whichever is
greater.

Inputs
------
grain_cost_per_lb : float   -- price of malt/grain per pound
hops_cost_per_oz  : float   -- price of hops per ounce
yeast_cost_per_unit: float  -- price of yeast per unit (1 packet/vial)
packaging_cost_per_unit : float -- price of cans/bottles per unit
batch_size_barrels : float  -- volume of the batch in US barrels (1 bbl = 31 US gal)
margin_percent      : float  -- desired profit margin (e.g. 30 for 30%)

Optional brew-day constants:
grain_usage_lbs     : float  -- pounds of grain used
hops_usage_oz       : float  -- ounces of hops used
yeast_units         : int    -- number of yeast units used
packaging_units     : int    -- number of cans/bottles used
abv_points          : float  -- beer ABV percentage (drives value-based pricing)

Outputs
-------
total_ingredient_cost : float
cost_per_barrel       : float
value_based_price     : float   -- analogue of ABV-based pricing
cost_based_price      : float   -- raw ingredient cost per barrel
recommended_price     : float   -- greater of cost vs. value, then margin-applied
"""

from dataclasses import dataclass, field


# -- Reference constants (inspired by beerfestdb defaults) -----------------
# In the original code:
#   default_abv_coefficient = 70    (pence per ABV point)
#   default_abv_constant   = 230   (pence minimum ABV uplift)
#   default_l_coefficient  = 1.64  (pence per litre of saleable volume)
# We translate these into a *value-based* pricing model for beer:
#   value_per_barrel = (abv_points * abv_coefficient + abv_constant) * barrels
#                         + l_coefficient * total_litres
# Then we take the greater of cost-based and value-based, just as
# the reference does  max(abv_price, cost_price).

DEFAULT_ABV_COEFFICIENT = 0.70    # $ per ABV point per barrel  (was 70 pence)
DEFAULT_ABV_CONSTANT     = 2.30   # $ minimum ABV uplift per barrel (was 230 pence)
DEFAULT_L_COEFFICIENT   = 0.0528 # $ per litre (was 1.64 pence/litre)

# Conversion: 1 US barrel = 117.348 litres
BARREL_TO_LITRES = 117.348


@dataclass
class BrewBatch:
    """Container for all batch parameters and computed results."""

    # -- Ingredient unit costs --------------------------------------------
    grain_cost_per_lb: float = 0.50
    hops_cost_per_oz: float = 1.00
    yeast_cost_per_unit: float = 5.00
    packaging_cost_per_unit: float = 0.75

    # -- Batch size -------------------------------------------------------
    batch_size_barrels: float = 5.0

    # -- Usage quantities -------------------------------------------------
    grain_usage_lbs: float = 100.0
    hops_usage_oz: float = 2.0
    yeast_units: int = 1
    packaging_units: int = 200

    # -- Pricing model ----------------------------------------------------
    abv_points: float = 12.0       # e.g. 12% ABV
    margin_percent: float = 30.0   # desired profit margin

    # -- Coefficients (override defaults if needed) -----------------------
    abv_coefficient: float = DEFAULT_ABV_COEFFICIENT
    abv_constant: float = DEFAULT_ABV_CONSTANT
    l_coefficient: float = DEFAULT_L_COEFFICIENT

    # -- Computed fields --------------------------------------------------
    total_ingredient_cost: float = field(init=False)
    cost_per_barrel: float = field(init=False)
    value_based_price: float = field(init=False)
    cost_based_price: float = field(init=False)
    recommended_price: float = field(init=False)

    def __post_init__(self):
        # --- Ingredient Costs ---
        grain_cost    = self.grain_usage_lbs * self.grain_cost_per_lb
        hops_cost     = self.hops_usage_oz   * self.hops_cost_per_oz
        yeast_cost    = self.yeast_units     * self.yeast_cost_per_unit
        packaging_cost = self.packaging_units * self.packaging_cost_per_unit
        self.total_ingredient_cost = (
            grain_cost + hops_cost + yeast_cost + packaging_cost
        )

        # --- Cost-per-barrel ---
        self.cost_per_barrel = (
            self.total_ingredient_cost / self.batch_size_barrels
            if self.batch_size_barrels > 0 else 0.0
        )

        # --- Value-based price (analogue of ABV pricing in reference) ---
        total_litres = self.batch_size_barrels * BARREL_TO_LITRES
        abv_component = (
            self.abv_points * self.abv_coefficient + self.abv_constant
        )
        l_component = self.l_coefficient * total_litres
        self.value_based_price = abv_component + l_component

        # --- Cost-based price (per barrel) ---
        self.cost_based_price = self.cost_per_barrel

        # --- Take the greater (mirrors reference: max(abv_price, cost_price)) ---
        base_price = max(self.value_based_price, self.cost_based_price)

        # --- Apply margin ---
        self.recommended_price = base_price * (1 + self.margin_percent / 100.0)

    def summary(self) -> str:
        lines = [
            "=" * 60,
            "  CRAFT BREWERY BATCH COST CALCULATOR",
            "=" * 60,
            "",
            "--- INPUTS ----------------------------------------------",
            f"  Batch size:              {self.batch_size_barrels:.1f} bbl",
            f"  Grain:                   {self.grain_usage_lbs:.0f} lbs  "
            f"@ ${self.grain_cost_per_lb:.2f}/lb  = "
            f"${self.grain_usage_lbs * self.grain_cost_per_lb:.2f}",
            f"  Hops:                    {self.hops_usage_oz:.1f} oz   "
            f"@ ${self.hops_cost_per_oz:.2f}/oz   = "
            f"${self.hops_usage_oz * self.hops_cost_per_oz:.2f}",
            f"  Yeast:                   {self.yeast_units} unit(s) "
            f"@ ${self.yeast_cost_per_unit:.2f}/unit = "
            f"${self.yeast_units * self.yeast_cost_per_unit:.2f}",
            f"  Packaging:               {self.packaging_units} units "
            f"@ ${self.packaging_cost_per_unit:.2f}/unit = "
            f"${self.packaging_units * self.packaging_cost_per_unit:.2f}",
            f"  Beer ABV:                {self.abv_points:.1f}%",
            f"  Desired margin:          {self.margin_percent:.0f}%",
            "",
            f"  ABV coefficient:         ${self.abv_coefficient:.2f}/pt/bbl",
            f"  ABV constant:            ${self.abv_constant:.2f}/bbl",
            f"  Litre coefficient:       ${self.l_coefficient:.4f}/l",
            "",
            "--- COST BREAKDOWN --------------------------------------",
            f"  Total ingredient cost : ${self.total_ingredient_cost:.2f}",
            f"  Cost per barrel        : ${self.cost_per_barrel:.4f}",
            "",
            "--- PRICING (dual-model, take greater) ------------------",
            f"  Value-based (ABV) price : "
            f"${self.value_based_price:.4f}  /  bbl",
            f"  Cost-based price         : "
            f"${self.cost_based_price:.4f}  /  bbl",
            f"  > Selected base price     : "
            f"${max(self.value_based_price, self.cost_based_price):.4f}",
            f"  * RECOMMENDED SELL PRICE : "
            f"${self.recommended_price:.2f}  /  bbl",
            "",
            "=" * 60,
        ]
        return "\n".join(lines)


# ======================================================================
#  SAMPLE RUN  --  5-bbl pale ale batch
# ======================================================================
if __name__ == "__main__":

    batch = BrewBatch(
        # Ingredient unit costs
        grain_cost_per_lb    = 0.60,    # $/lb malt
        hops_cost_per_oz     = 1.50,    # $/oz hops
        yeast_cost_per_unit  = 4.00,    # $/packet
        packaging_cost_per_unit = 0.80, # $/can

        # Batch size
        batch_size_barrels   = 5.0,     # 5 US barrels

        # Usage quantities
        grain_usage_lbs      = 120.0,   # lbs of grain
        hops_usage_oz        = 3.5,     # oz of hops
        yeast_units          = 2,       # 2 packets of yeast
        packaging_units      = 240,     # 240 cans

        # Beer properties
        abv_points           = 12.0,    # 12% ABV

        # Margin
        margin_percent       = 30.0,    # 30% margin
    )

    print(batch.summary())
