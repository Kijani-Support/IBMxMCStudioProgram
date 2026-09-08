import unittest

from coach import generate_financial_advice
from finance import calculate_finances
from investments import calculate_investment


class CoreLogicTests(unittest.TestCase):
    def test_demo_finances(self):
        result = calculate_finances(80_000, {
            "Rent": 25_000,
            "Food": 15_000,
            "Transport": 8_000,
            "Utilities": 5_000,
            "Entertainment": 5_000,
        })
        self.assertEqual(result["expenses"], 58_000)
        self.assertEqual(result["savings"], 22_000)
        self.assertAlmostEqual(result["savings_rate"], 27.5)
        self.assertEqual(result["largest_expense_category"], "Rent")

    def test_zero_income_and_empty_expenses(self):
        result = calculate_finances(0, {})
        self.assertEqual(result["savings_rate"], 0)
        self.assertEqual(result["largest_expense_category"], "None")

    def test_demo_investment(self):
        result = calculate_investment(100, 20, 25.5)
        self.assertEqual(result["cost"], 2_000)
        self.assertEqual(result["value"], 2_550)
        self.assertEqual(result["profit"], 550)
        self.assertAlmostEqual(result["return_pct"], 27.5)

    def test_zero_cost_investment(self):
        self.assertEqual(calculate_investment(0, 0, 25)["return_pct"], 0)

    def test_coach_returns_two_recommendations(self):
        finances = calculate_finances(1_000, {"Food": 900})
        advice = generate_financial_advice(finances, {"Food": 900})
        self.assertEqual(len(advice["recommendations"]), 2)


if __name__ == "__main__":
    unittest.main()
