"""Deterministic personal-finance calculations for the dashboard."""

from __future__ import annotations


def calculate_finances(income: float, expenses: dict[str, float]) -> dict[str, float | str]:
    """Return the core monthly finance metrics using safe numeric inputs."""
    safe_income = max(float(income or 0), 0.0)
    safe_expenses = {
        category: max(float(amount or 0), 0.0)
        for category, amount in expenses.items()
    }
    total_expenses = sum(safe_expenses.values())
    savings = safe_income - total_expenses
    savings_rate = savings / safe_income * 100 if safe_income > 0 else 0.0
    largest_category = (
        max(safe_expenses, key=safe_expenses.get) if safe_expenses else "None"
    )

    return {
        "income": safe_income,
        "expenses": total_expenses,
        "savings": savings,
        "savings_rate": savings_rate,
        "largest_expense_category": largest_category,
    }
