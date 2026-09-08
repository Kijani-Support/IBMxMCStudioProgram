import os
import unittest
from unittest.mock import patch

from ai_service import (answer_question, build_context, explain_transaction,
                        screen_scam, spending_summary)
from budgeting import (budget_status, emergency_fund_months,
                       monthly_comparison, trend_points)


class BudgetingTests(unittest.TestCase):
    def test_budget_alert_thresholds(self):
        rows = budget_status(
            {"Food": 900, "Rent": 1_000},
            [{"category": "Food", "monthly_limit": 1_000},
             {"category": "Rent", "monthly_limit": 800}],
        )
        self.assertEqual(rows[0]["status"], "near")
        self.assertEqual(rows[1]["status"], "over")

    def test_monthly_comparison_and_trend_order(self):
        records = [
            {"month": "2026-08", "income": 2_000, "expenses": {"Food": 500}},
            {"month": "2026-07", "income": 1_500, "expenses": {"Food": 700}},
        ]
        comparison = monthly_comparison(records)
        self.assertEqual(comparison["expense_change"], -200)
        self.assertEqual(comparison["savings_change"], 700)
        self.assertEqual(trend_points(records)[0]["month"], "2026-07")

    def test_emergency_fund_uses_essential_expenses(self):
        self.assertEqual(emergency_fund_months(6_000, {"Rent": 2_000, "Food": 1_000, "Entertainment": 1_000}), 2)


class AIServiceTests(unittest.TestCase):
    def setUp(self):
        self.records = [{"month": "2026-08", "income": 10_000,
                         "expenses": {"Rent": 4_000, "Food": 2_000}}]
        self.budgets = [{"category": "Food", "monthly_limit": 2_000}]
        self.goals = [{"name": "Emergency fund", "target_amount": 10_000, "saved_amount": 5_000}]
        self.debts = [{"name": "Loan", "balance": 3_000, "annual_rate": 12, "minimum_payment": 300}]

    def test_context_summary_and_offline_question(self):
        context = build_context(self.records, self.budgets, self.goals, self.debts)
        self.assertIn("savings are ETB 4,000", spending_summary(context))
        with patch.dict(os.environ, {}, clear=True):
            answer, source = answer_question("How is my savings goal?", context)
        self.assertEqual(source, "Offline coach")
        self.assertIn("50% funded", answer)

    def test_transaction_explanation(self):
        self.assertIn("Food", explain_transaction("Local supermarket", 2_500))

    def test_scam_screening(self):
        result = screen_scam("URGENT: account suspended. Send money and verify your PIN at http://bad.test")
        self.assertEqual(result["risk"], "HIGH")
        self.assertGreaterEqual(result["score"], 70)


if __name__ == "__main__":
    unittest.main()
