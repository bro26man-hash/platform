"""Craft Brewery Batch Cost Calculator.

Calculates total batch cost, cost-per-barrel, and recommended selling price
for a craft brewery based on ingredient inputs and desired margin.

Inspired by: tfrayner/beerfestdb CBF_beer_price_calculator.py
Reference: https://github.com/tfrayner/beerfestdb/blob/main/tool_dashboard/CBF_beer_price_calculator.py
"""


class BatchCostCalculator:
    """Craft Brewery Batch Cost Calculator.

    Calculates total cost, cost-per-barrel, and recommended selling price
    for a craft brewery batch based on ingredient inputs and batch size.
    """

    # Approximate constants
    GALLONS_PER_BARREL = 31.0  # US standard barrel
    BOTTLES_PER_CASE = 24
    OZ_PER_BOTTLE = 12
    EPSILON = 1e-9

    def __init__(self):
        self.grain_cost_per_lb = 0.0      # $/lb
        self.hops_cost_per_oz = 0.0       # $/oz
        self.yeast_cost_per_unit = 0.0    # $/unit (packet/culture)
        self.packaging_cost_per_unit = 0.0  # $/unit (bottle/can/case)
        self.batch_size_barrels = 0.0
        self.margin_percent = 0.0

    def set_ingredient_costs(self, grain_cost_per_lb, hops_cost_per_oz,
                             yeast_cost_per_unit, packaging_cost_per_unit):
        """Set ingredient costs."""
        self.grain_cost_per_lb = grain_cost_per_lb
        self.hops_cost_per_oz = hops_cost_per_oz
        self.yeast_cost_per_unit = yeast_cost_per_unit
        self.packaging_cost_per_unit = packaging_cost_per_unit

    def calculate(self, batch_size_barrels, grain_lbs, hops_ozs, yeast_units,
                  packaging_units, margin_percent):
        """Calculate batch costs.

        Args:
            batch_size_barrels: Number of barrels in the batch
            grain_lbs: Total grain needed in pounds
            hops_ozs: Total hops needed in ounces
            yeast_units: Number of yeast units (packets/cultures)
            packaging_units: Number of packaging units (bottles/cans)
            margin_percent: Desired margin percentage (e.g., 40 for 40%)

        Returns:
            dict with cost breakdown and pricing
        """
        self.batch_size_barrels = batch_size_barrels
        self.margin_percent = margin_percent

        # Ingredient costs
        grain_cost = grain_lbs * self.grain_cost_per_lb
        hops_cost = hops_ozs * self.hops_cost_per_oz
        yeast_cost = yeast_units * self.yeast_cost_per_unit
        packaging_cost = packaging_units * self.packaging_cost_per_unit

        total_cost = grain_cost + hops_cost + yeast_cost + packaging_cost
        cost_per_barrel = total_cost / max(batch_size_barrels, self.EPSILON)

        # Recommended selling price = cost_per_barrel * (1 + margin)
        recommended_price = cost_per_barrel * (1 + margin_percent / 100.0)

        # Revenue and profit
        total_revenue = recommended_price * batch_size_barrels
        total_profit = total_revenue - total_cost

        gallons = batch_size_barrels * self.GALLONS_PER_BARREL
        cases = packaging_units / max(self.BOTTLES_PER_CASE, self.EPSILON)

        return {
            "ingredients": {
                "grain_cost": round(grain_cost, 2),
                "hops_cost": round(hops_cost, 2),
                "yeast_cost": round(yeast_cost, 2),
                "packaging_cost": round(packaging_cost, 2),
            },
            "total_cost": round(total_cost, 2),
            "cost_per_barrel": round(cost_per_barrel, 2),
            "margin_percent": margin_percent,
            "recommended_price_per_barrel": round(recommended_price, 2),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "batch_size": {
                "barrels": batch_size_barrels,
                "gallons": round(gallons, 1),
                "bottles": packaging_units,
                "cases": round(cases, 1),
            }
        }

    def display(self, result):
        """Pretty-print the calculation results."""
        print("=" * 60)
        print("  CRAFT BREWERY BATCH COST CALCULATOR")
        print("=" * 60)
        print()
        print(f"  Batch Size:       {result['batch_size']['barrels']} barrels "
              f"({result['batch_size']['gallons']} gallons)")
        print(f"  Bottles:          {result['batch_size']['bottles']} "
              f"({result['batch_size']['cases']} cases of 24)")
        print()
        print("  -- Ingredient Costs --")
        print(f"  Grain:            ${result['ingredients']['grain_cost']:.2f}")
        print(f"  Hops:             ${result['ingredients']['hops_cost']:.2f}")
        print(f"  Yeast:            ${result['ingredients']['yeast_cost']:.2f}")
        print(f"  Packaging:        ${result['ingredients']['packaging_cost']:.2f}")
        print()
        print(f"  Total Cost:       ${result['total_cost']:.2f}")
        print(f"  Cost/Barrel:      ${result['cost_per_barrel']:.2f}")
        print()
        print("  -- Pricing --")
        print(f"  Margin:           {result['margin_percent']:.0f}%")
        print(f"  Recommended Price:${result['recommended_price_per_barrel']:.2f}/barrel")
        print(f"  Total Revenue:    ${result['total_revenue']:.2f}")
        print(f"  Total Profit:     ${result['total_profit']:.2f}")
        print("=" * 60)


if __name__ == "__main__":
    calc = BatchCostCalculator()
    calc.set_ingredient_costs(
        grain_cost_per_lb=1.50,
        hops_cost_per_oz=0.75,
        yeast_cost_per_unit=3.50,
        packaging_cost_per_unit=0.15,
    )
    result = calc.calculate(
        batch_size_barrels=5,
        grain_lbs=1000,
        hops_ozs=50,
        yeast_units=3,
        packaging_units=1200,
        margin_percent=40,
    )
    calc.display(result)