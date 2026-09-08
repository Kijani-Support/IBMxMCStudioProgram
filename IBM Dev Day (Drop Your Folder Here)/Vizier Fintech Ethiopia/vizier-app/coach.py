"""Offline, rule-based financial coaching."""

from __future__ import annotations


def generate_financial_advice(
    finances: dict[str, float | str], expenses: dict[str, float]
) -> dict[str, object]:
    rate = float(finances["savings_rate"])
    savings = float(finances["savings"])
    largest = str(finances["largest_expense_category"])

    if savings < 0:
        tone = "negative"
        assessment = "Your expenses currently exceed your income."
        rate_feedback = "Focus first on returning your monthly cash flow to positive."
    elif rate < 10:
        tone = "warning"
        assessment = "Your savings rate is low, leaving little room for surprises."
        rate_feedback = "Try working gradually toward a savings rate of at least 10%."
    elif rate < 20:
        tone = "moderate"
        assessment = "Your savings rate is moderate and moving in a useful direction."
        rate_feedback = "A small recurring transfer could move you closer to 20%."
    else:
        tone = "positive"
        assessment = "Your savings rate is healthy."
        rate_feedback = "Keep the habit consistent and review your goal each month."

    biggest = (
        f"{largest} is your largest spending category."
        if expenses and max(expenses.values(), default=0) > 0
        else "You have not recorded any expenses yet."
    )
    recommendations = [
        f"Review {largest.lower()} for one realistic reduction this month."
        if largest != "None"
        else "Add your monthly expenses to receive a targeted recommendation.",
        "Automate a savings transfer just after income arrives.",
    ]
    return {
        "tone": tone,
        "assessment": assessment,
        "biggest": biggest,
        "rate_feedback": rate_feedback,
        "recommendations": recommendations,
    }
