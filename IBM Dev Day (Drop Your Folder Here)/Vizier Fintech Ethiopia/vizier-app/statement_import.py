"""CSV statement parsing, validation, mapping, categorization, and deduplication."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import datetime
from typing import Any


COLUMN_ALIASES = {
    "date": ("date", "transaction date", "posted date", "value date", "time"),
    "description": ("description", "details", "narration", "merchant", "transaction", "memo"),
    "amount": ("amount", "transaction amount", "value"),
    "debit": ("debit", "withdrawal", "money out", "paid out"),
    "credit": ("credit", "deposit", "money in", "paid in"),
}

CATEGORY_RULES = [
    ("Rent", r"\brent\b|landlord|property"),
    ("Food", r"market|supermarket|restaurant|cafe|food|coffee|injera|naivas|carrefour|quickmart"),
    ("Transport", r"ride|taxi|fuel|petrol|bus|transport|minibus|bajaj|uber|bolt|matatu"),
    ("Utilities", r"electric|water|ethio telecom|internet|airtime|telebirr|kplc|safaricom"),
    ("Healthcare", r"hospital|clinic|pharmacy|chemist|medical"),
    ("Entertainment", r"netflix|spotify|cinema|showmax|entertainment"),
    ("Income", r"salary|payroll|wages|interest received"),
    ("Transfers", r"transfer|telebirr|cbe birr|mobile money"),
    ("Fees", r"fee|charge|levy|commission"),
]


def read_csv_raw(text: str, max_rows: int = 5_000) -> tuple[list[str], list[dict[str, str]]]:
    text = text.lstrip("\ufeff")
    sample = text[:8_192]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel
    reader = csv.DictReader(io.StringIO(text), dialect=dialect)
    headers = [header.strip() for header in (reader.fieldnames or []) if header]
    if not headers:
        raise ValueError("The CSV file has no header row.")
    rows = []
    for index, row in enumerate(reader):
        if index >= max_rows:
            raise ValueError(f"CSV files are limited to {max_rows:,} transactions per import.")
        rows.append({str(key).strip(): str(value or "").strip() for key, value in row.items() if key})
    if not rows:
        raise ValueError("The CSV file contains no transaction rows.")
    return headers, rows


def detect_columns(headers: list[str]) -> dict[str, str | None]:
    normalized = {header.lower().strip(): header for header in headers}
    return {field: next((normalized[alias] for alias in aliases if alias in normalized), None)
            for field, aliases in COLUMN_ALIASES.items()}


def _number(value: str) -> float:
    cleaned = re.sub(r"[^0-9.()\-]", "", value.replace(",", ""))
    if not cleaned: return 0.0
    negative = cleaned.startswith("(") and cleaned.endswith(")")
    cleaned = cleaned.strip("()")
    number = float(cleaned)
    return -abs(number) if negative else number


def _date(value: str) -> str:
    value = value.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%Y/%m/%d",
                "%d %b %Y", "%d %B %Y", "%Y-%m-%d %H:%M:%S"):
        try: return datetime.strptime(value, fmt).date().isoformat()
        except ValueError: pass
    raise ValueError(f"Unsupported date: {value}")


def categorize(description: str, amount: float) -> str:
    for category, pattern in CATEGORY_RULES:
        if re.search(pattern, description, re.I): return category
    return "Income" if amount > 0 else "Other"


def normalize_rows(rows: list[dict[str, str]], mapping: dict[str, str | None]) -> tuple[list[dict[str, Any]], list[str]]:
    if not mapping.get("date") or not mapping.get("description"):
        raise ValueError("Map both the date and description columns.")
    if not mapping.get("amount") and not (mapping.get("debit") or mapping.get("credit")):
        raise ValueError("Map an amount column or debit/credit columns.")
    transactions, errors = [], []
    for index, row in enumerate(rows, start=2):
        try:
            date = _date(row.get(mapping["date"], ""))
            description = row.get(mapping["description"], "").strip()
            if not description: raise ValueError("description is empty")
            if mapping.get("amount"):
                amount = _number(row.get(mapping["amount"], ""))
            else:
                credit = _number(row.get(mapping.get("credit") or "", ""))
                debit = _number(row.get(mapping.get("debit") or "", ""))
                amount = credit - abs(debit)
            if amount == 0: raise ValueError("amount is zero or missing")
            category = categorize(description, amount)
            fingerprint = hashlib.sha256(f"{date}|{description.lower()}|{amount:.2f}".encode()).hexdigest()
            transactions.append({"date": date, "description": description, "amount": amount,
                                 "category": category, "fingerprint": fingerprint})
        except (ValueError, TypeError) as error:
            errors.append(f"Row {index}: {error}")
    return transactions, errors
