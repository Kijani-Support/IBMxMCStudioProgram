"""Explainable deterministic financial-health score."""

from __future__ import annotations

from typing import Any

from budgeting import budget_status, emergency_fund_months
from finance import calculate_finances


def calculate_health_score(income: float, expenses: dict[str, float], budgets: list[dict[str, Any]],
                           goals: list[dict[str, Any]], debts: list[dict[str, Any]]) -> dict[str, Any]:
    finances = calculate_finances(income, expenses)
    savings_rate = float(finances["savings_rate"])
    savings_points = max(0, min(savings_rate / 20 * 35, 35))
    expense_ratio = float(finances["expenses"]) / income if income > 0 else 1
    cashflow_points = max(0, min((1 - expense_ratio) / .20 * 20, 20))
    configured = [row for row in budget_status(expenses, budgets) if row["limit"] > 0]
    within = sum(1 for row in configured if row["status"] != "over")
    budget_points = within / len(configured) * 15 if configured else 7.5
    emergency_saved = sum(goal["saved_amount"] for goal in goals if "emergency" in goal["name"].lower())
    cover = emergency_fund_months(emergency_saved, expenses)
    emergency_points = min(cover / 3 * 15, 15)
    minimum_payments = sum(debt["minimum_payment"] for debt in debts)
    debt_ratio = minimum_payments / income if income > 0 else (1 if minimum_payments else 0)
    debt_points = max(0, min((.20 - debt_ratio) / .20 * 15, 15))
    score = round(savings_points + cashflow_points + budget_points + emergency_points + debt_points)
    rating = "Strong" if score >= 80 else "Stable" if score >= 65 else "Developing" if score >= 45 else "At risk"
    recommendations = []
    if savings_rate < 20: recommendations.append("Work toward saving 20% of monthly income.")
    if cover < 3: recommendations.append("Build an emergency fund covering three months of essential expenses.")
    if debt_ratio > .20: recommendations.append("Minimum debt payments exceed 20% of income; review repayment options.")
    if any(row["status"] == "over" for row in configured): recommendations.append("Bring over-budget categories back within their limits.")
    if not recommendations: recommendations.append("Maintain your current habits and review the score monthly.")
    return {"score": score, "rating": rating, "components": {
        "Savings rate": round(savings_points, 1), "Positive cash flow": round(cashflow_points, 1),
        "Budget adherence": round(budget_points, 1), "Emergency fund": round(emergency_points, 1),
        "Debt load": round(debt_points, 1)}, "recommendations": recommendations,
        "emergency_months": cover, "debt_payment_ratio": debt_ratio * 100}
