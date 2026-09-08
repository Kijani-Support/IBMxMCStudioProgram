"""Optional OpenAI-backed assistant with deterministic offline fallbacks."""

from __future__ import annotations

import json
import os
import re
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from budgeting import budget_status, emergency_fund_months, monthly_comparison
from finance import calculate_finances
from settings import COUNTRY, CURRENCY


def build_context(records: list[dict[str, Any]], budgets: list[dict[str, Any]],
                  goals: list[dict[str, Any]], debts: list[dict[str, Any]]) -> dict[str, Any]:
    latest = records[0] if records else {"income": 0, "expenses": {}, "month": "unsaved"}
    finances = calculate_finances(latest["income"], latest["expenses"])
    return {"month": latest["month"], "finances": finances, "expenses": latest["expenses"],
            "budget_status": budget_status(latest["expenses"], budgets),
            "comparison": monthly_comparison(records), "goals": goals, "debts": debts}


def spending_summary(context: dict[str, Any]) -> str:
    finances, expenses = context["finances"], context["expenses"]
    alerts = [row for row in context["budget_status"] if row["status"] in {"near", "over"}]
    summary = (f"For {context['month']}, spending is {CURRENCY} {finances['expenses']:,.0f} and "
               f"savings are {CURRENCY} {finances['savings']:,.0f} ({finances['savings_rate']:.1f}%).")
    if expenses:
        largest = max(expenses, key=expenses.get)
        summary += f" {largest} is the largest category at {CURRENCY} {expenses[largest]:,.0f}."
    if alerts:
        summary += " Budget attention: " + ", ".join(f"{row['category']} ({row['percentage']:.0f}%)" for row in alerts) + "."
    return summary


def offline_answer(question: str, context: dict[str, Any]) -> str:
    lowered, finances = question.lower(), context["finances"]
    if any(word in lowered for word in ("save", "saving", "goal")):
        goals = context["goals"]
        detail = " No savings goals are recorded yet." if not goals else " " + " ".join(
            f"{g['name']} is {min(g['saved_amount'] / g['target_amount'] * 100, 100):.0f}% funded." for g in goals)
        return f"Your current savings rate is {finances['savings_rate']:.1f}%." + detail
    if any(word in lowered for word in ("debt", "loan", "interest")):
        debts = context["debts"]
        if not debts: return "You have not recorded any debts."
        highest = max(debts, key=lambda debt: debt["annual_rate"])
        return f"Recorded debt totals {CURRENCY} {sum(d['balance'] for d in debts):,.0f}. {highest['name']} has the highest rate at {highest['annual_rate']:.1f}%; consider prioritizing it after minimum payments."
    if any(word in lowered for word in ("budget", "overspend", "category")):
        alerts = [row for row in context["budget_status"] if row["status"] != "ok"]
        return "All configured categories are within their alert thresholds." if not alerts else "Watch " + ", ".join(f"{row['category']} at {row['percentage']:.0f}% of budget" for row in alerts) + "."
    return spending_summary(context) + " Ask about savings goals, budgets, debts, or spending."


def _watsonx_answer(question: str, context: dict[str, Any]) -> str:
    api_key = os.environ["WATSONX_API_KEY"]
    token_request = Request(
        "https://iam.cloud.ibm.com/identity/token",
        data=urlencode({"grant_type": "urn:ibm:params:oauth:grant-type:apikey", "apikey": api_key}).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"},
    )
    with urlopen(token_request, timeout=20) as response:
        token = json.loads(response.read())["access_token"]
    base_url = os.environ.get("WATSONX_URL", "https://us-south.ml.cloud.ibm.com").rstrip("/")
    prompt = (
        f"You are Vizier, an educational personal-finance coach for {COUNTRY}. "
        "Use only the supplied deterministic figures. Never invent values or give buy/sell instructions. "
        f"Use {CURRENCY} for money. Keep the response concise and practical.\n\n"
        f"Financial context:\n{json.dumps(context, default=str)}\n\nUser question: {question}\nAnswer:"
    )
    payload = {
        "model_id": os.environ.get("WATSONX_MODEL_ID", "ibm/granite-3-8b-instruct"),
        "project_id": os.environ["WATSONX_PROJECT_ID"],
        "input": prompt,
        "parameters": {"decoding_method": "greedy", "max_new_tokens": 350, "repetition_penalty": 1.05},
    }
    request = Request(
        f"{base_url}/ml/v1/text/generation?version=2024-05-31",
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "Accept": "application/json"},
    )
    with urlopen(request, timeout=45) as response:
        result = json.loads(response.read())
    return str(result["results"][0]["generated_text"]).strip()


def answer_question(question: str, context: dict[str, Any]) -> tuple[str, str]:
    if os.environ.get("WATSONX_API_KEY") and os.environ.get("WATSONX_PROJECT_ID"):
        try:
            return _watsonx_answer(question, context), "IBM watsonx.ai / Granite"
        except Exception:
            pass
    if os.environ.get("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            response = client.responses.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-5.4-mini"), store=False,
                instructions=(f"You are Vizier, an educational personal-finance coach for {COUNTRY}. "
                              "Use only the supplied deterministic figures. Never invent values or give buy/sell instructions. "
                              "Be concise, practical, and clearly label uncertainty."),
                input=f"Financial context:\n{json.dumps(context, default=str)}\n\nUser question: {question}",
            )
            return response.output_text, "OpenAI"
        except Exception:
            pass
    return offline_answer(question, context), "Offline coach"


def explain_transaction(description: str, amount: float) -> str:
    text = description.lower()
    mappings = {"ride": "Transport", "taxi": "Transport", "bus": "Transport",
                "market": "Food", "supermarket": "Food", "restaurant": "Food",
                "telebirr": "Utilities", "ethio telecom": "Utilities",
                "rent": "Rent", "pharmacy": "Healthcare"}
    category = next((value for key, value in mappings.items() if key in text), "Other")
    return f"Likely category: {category}. The {CURRENCY} {amount:,.0f} transaction was classified from keywords in the description; review it before saving."


def screen_scam(message: str) -> dict[str, Any]:
    rules = {"urgent pressure": r"urgent|immediately|act now|suspended",
             "credential request": r"password|pin|otp|verification code",
             "payment request": r"send money|pay now|transfer",
             "suspicious link": r"https?://|www\.", "prize or windfall": r"won|prize|lottery|inheritance"}
    matches = [label for label, pattern in rules.items() if re.search(pattern, message, re.I)]
    score = min(20 + len(matches) * 20, 95) if matches else 10
    risk = "HIGH" if score >= 70 else "MEDIUM" if score >= 40 else "LOW"
    return {"risk": risk, "score": score, "reasons": matches or ["No common high-risk language detected"]}
