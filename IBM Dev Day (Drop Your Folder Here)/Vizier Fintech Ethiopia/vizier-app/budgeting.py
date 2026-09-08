"""Deterministic advanced-budgeting analytics."""

from __future__ import annotations

from typing import Any

from finance import calculate_finances


def budget_status(expenses: dict[str, float], budgets: list[dict[str, Any]]) -> list[dict[str, Any]]:
    results = []
    for budget in budgets:
        category = str(budget["category"])
        limit = float(budget["monthly_limit"])
        spent = float(expenses.get(category, 0))
        percentage = spent / limit * 100 if limit > 0 else 0
        status = "over" if limit > 0 and spent > limit else "near" if limit > 0 and percentage >= 80 else "ok"
        results.append({"id": budget.get("id"), "category": category, "limit": limit, "spent": spent,
                        "remaining": limit - spent, "percentage": percentage, "status": status})
    return results


def monthly_comparison(records: list[dict[str, Any]]) -> dict[str, Any] | None:
    if len(records) < 2:
        return None
    current, previous = records[0], records[1]
    current_finances = calculate_finances(current["income"], current["expenses"])
    previous_finances = calculate_finances(previous["income"], previous["expenses"])
    return {
        "current_month": current["month"], "previous_month": previous["month"],
        "expense_change": float(current_finances["expenses"]) - float(previous_finances["expenses"]),
        "savings_change": float(current_finances["savings"]) - float(previous_finances["savings"]),
        "rate_change": float(current_finances["savings_rate"]) - float(previous_finances["savings_rate"]),
    }


def emergency_fund_months(saved_amount: float, expenses: dict[str, float]) -> float:
    essential_names = {"Rent", "Food", "Transport", "Utilities", "Healthcare", "Debt"}
    essentials = sum(value for name, value in expenses.items() if name in essential_names)
    return saved_amount / essentials if essentials > 0 else 0


def trend_points(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    points = []
    for record in reversed(records):
        finances = calculate_finances(record["income"], record["expenses"])
        points.append({"month": record["month"], "expenses": finances["expenses"], "savings": finances["savings"]})
    return points
