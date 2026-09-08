"""SQLite persistence and local account management for Vizier."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import secrets
import sqlite3
from pathlib import Path
from typing import Any

DB_PATH = Path(os.environ.get("VIZIER_DB_PATH", Path(__file__).with_name("vizier.db")))


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    with _connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                full_name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS financial_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                account_type TEXT NOT NULL DEFAULT 'Personal',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, name)
            );
            CREATE TABLE IF NOT EXISTS monthly_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                account_id INTEGER NOT NULL REFERENCES financial_accounts(id) ON DELETE CASCADE,
                month TEXT NOT NULL,
                income REAL NOT NULL,
                savings_goal REAL NOT NULL,
                expenses_json TEXT NOT NULL,
                updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(account_id, month)
            );
            CREATE TABLE IF NOT EXISTS category_budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                category TEXT NOT NULL,
                monthly_limit REAL NOT NULL DEFAULT 0,
                UNIQUE(user_id, category)
            );
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                saved_amount REAL NOT NULL DEFAULT 0,
                target_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS debts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                balance REAL NOT NULL,
                annual_rate REAL NOT NULL DEFAULT 0,
                minimum_payment REAL NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                ticker TEXT NOT NULL,
                shares REAL NOT NULL,
                purchase_price REAL NOT NULL,
                dividends REAL NOT NULL DEFAULT 0,
                acquired_date TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                ticker TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, ticker)
            );
            CREATE TABLE IF NOT EXISTS import_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                account_id INTEGER NOT NULL REFERENCES financial_accounts(id) ON DELETE CASCADE,
                filename TEXT NOT NULL,
                imported_count INTEGER NOT NULL,
                duplicate_count INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                account_id INTEGER NOT NULL REFERENCES financial_accounts(id) ON DELETE CASCADE,
                batch_id INTEGER REFERENCES import_batches(id) ON DELETE SET NULL,
                transaction_date TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, fingerprint)
            );
            CREATE INDEX IF NOT EXISTS idx_accounts_user ON financial_accounts(user_id);
            CREATE INDEX IF NOT EXISTS idx_records_user_month ON monthly_records(user_id, month DESC);
            CREATE INDEX IF NOT EXISTS idx_transactions_user_date ON transactions(user_id, transaction_date DESC);
            CREATE INDEX IF NOT EXISTS idx_holdings_user ON holdings(user_id);
            CREATE INDEX IF NOT EXISTS idx_import_batches_user ON import_batches(user_id);
        """)


def _hash_password(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"{salt.hex()}:{digest.hex()}"


def _password_matches(password: str, encoded: str) -> bool:
    try:
        salt_hex, expected = encoded.split(":", 1)
        actual = _hash_password(password, bytes.fromhex(salt_hex)).split(":", 1)[1]
        return secrets.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def create_user(email: str, full_name: str, password: str) -> int:
    email, full_name = email.strip().lower(), full_name.strip()
    if not email or "@" not in email:
        raise ValueError("Enter a valid email address.")
    if not full_name:
        raise ValueError("Enter your name.")
    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")
    try:
        with _connect() as db:
            cursor = db.execute(
                "INSERT INTO users (email, full_name, password_hash) VALUES (?, ?, ?)",
                (email, full_name, _hash_password(password)),
            )
            user_id = int(cursor.lastrowid)
            db.execute(
                "INSERT INTO financial_accounts (user_id, name, account_type) VALUES (?, ?, ?)",
                (user_id, "Main account", "Personal"),
            )
            db.executemany(
                "INSERT INTO category_budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)",
                [(user_id, name, 0) for name in
                 ("Rent", "Food", "Transport", "Utilities", "Entertainment", "Other")],
            )
            return user_id
    except sqlite3.IntegrityError as error:
        raise ValueError("An account with that email already exists.") from error


def authenticate_user(email: str, password: str) -> dict[str, Any] | None:
    with _connect() as db:
        row = db.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip(),)
        ).fetchone()
    return dict(row) if row and _password_matches(password, row["password_hash"]) else None


def get_user(user_id: int) -> dict[str, Any] | None:
    with _connect() as db:
        row = db.execute(
            "SELECT id, email, full_name, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    return dict(row) if row else None


def update_profile(user_id: int, full_name: str) -> None:
    if not full_name.strip():
        raise ValueError("Name cannot be empty.")
    with _connect() as db:
        db.execute("UPDATE users SET full_name = ? WHERE id = ?", (full_name.strip(), user_id))


def list_accounts(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute(
            "SELECT id, name, account_type, created_at FROM financial_accounts WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def add_account(user_id: int, name: str, account_type: str) -> int:
    if not name.strip():
        raise ValueError("Account name cannot be empty.")
    try:
        with _connect() as db:
            cursor = db.execute(
                "INSERT INTO financial_accounts (user_id, name, account_type) VALUES (?, ?, ?)",
                (user_id, name.strip(), account_type),
            )
            return int(cursor.lastrowid)
    except sqlite3.IntegrityError as error:
        raise ValueError("You already have an account with that name.") from error


def delete_financial_account(user_id: int, account_id: int) -> None:
    if len(list_accounts(user_id)) <= 1:
        raise ValueError("Keep at least one financial account.")
    with _connect() as db:
        db.execute("DELETE FROM financial_accounts WHERE id = ? AND user_id = ?", (account_id, user_id))


def save_month(user_id: int, account_id: int, month: str, income: float,
               savings_goal: float, expenses: dict[str, float]) -> None:
    if len(month) != 7 or month[4] != "-":
        raise ValueError("Use a month in YYYY-MM format.")
    try:
        year, number = (int(part) for part in month.split("-"))
        if year < 1900 or not 1 <= number <= 12:
            raise ValueError
    except ValueError as error:
        raise ValueError("Use a valid month in YYYY-MM format.") from error
    with _connect() as db:
        owned = db.execute(
            "SELECT 1 FROM financial_accounts WHERE id = ? AND user_id = ?", (account_id, user_id)
        ).fetchone()
        if not owned:
            raise ValueError("That financial account is not available.")
        db.execute("""
            INSERT INTO monthly_records
                (user_id, account_id, month, income, savings_goal, expenses_json)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(account_id, month) DO UPDATE SET
                income=excluded.income, savings_goal=excluded.savings_goal,
                expenses_json=excluded.expenses_json, updated_at=CURRENT_TIMESTAMP
        """, (user_id, account_id, month, income, savings_goal, json.dumps(expenses)))


def list_records(user_id: int, account_id: int | None = None) -> list[dict[str, Any]]:
    query = """
        SELECT r.id, r.month, r.income, r.savings_goal, r.expenses_json, r.updated_at,
               a.id AS account_id, a.name AS account_name
        FROM monthly_records r JOIN financial_accounts a ON a.id = r.account_id
        WHERE r.user_id = ?
    """
    parameters: list[Any] = [user_id]
    if account_id is not None:
        query += " AND r.account_id = ?"
        parameters.append(account_id)
    query += " ORDER BY r.month DESC, a.name"
    with _connect() as db:
        rows = db.execute(query, parameters).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        item["expenses"] = json.loads(item.pop("expenses_json"))
        results.append(item)
    return results


def export_user_csv(user_id: int) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["account", "month", "income", "savings_goal", "total_expenses",
                     "savings", "savings_rate", "expenses"])
    for record in list_records(user_id):
        total = sum(record["expenses"].values())
        savings = record["income"] - total
        rate = savings / record["income"] * 100 if record["income"] else 0
        writer.writerow([record["account_name"], record["month"], record["income"],
                         record["savings_goal"], total, savings, f"{rate:.2f}",
                         json.dumps(record["expenses"], sort_keys=True)])
    return output.getvalue()


def delete_user(user_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM users WHERE id = ?", (user_id,))


def list_category_budgets(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute(
            "SELECT id, category, monthly_limit FROM category_budgets WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        if not rows:
            db.executemany(
                "INSERT OR IGNORE INTO category_budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)",
                [(user_id, name, 0) for name in
                 ("Rent", "Food", "Transport", "Utilities", "Entertainment", "Other")],
            )
            rows = db.execute(
                "SELECT id, category, monthly_limit FROM category_budgets WHERE user_id = ? ORDER BY id",
                (user_id,),
            ).fetchall()
    return [dict(row) for row in rows]


def upsert_category_budget(user_id: int, category: str, monthly_limit: float) -> None:
    category = category.strip().title()
    if not category:
        raise ValueError("Category name cannot be empty.")
    if monthly_limit < 0:
        raise ValueError("Budget limit cannot be negative.")
    with _connect() as db:
        db.execute("""
            INSERT INTO category_budgets (user_id, category, monthly_limit) VALUES (?, ?, ?)
            ON CONFLICT(user_id, category) DO UPDATE SET monthly_limit = excluded.monthly_limit
        """, (user_id, category, monthly_limit))


def delete_category_budget(user_id: int, category_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM category_budgets WHERE id = ? AND user_id = ?", (category_id, user_id))


def add_savings_goal(user_id: int, name: str, target_amount: float,
                     saved_amount: float, target_date: str | None) -> int:
    if not name.strip() or target_amount <= 0 or saved_amount < 0:
        raise ValueError("Enter a goal name, positive target, and non-negative saved amount.")
    with _connect() as db:
        cursor = db.execute("""
            INSERT INTO savings_goals (user_id, name, target_amount, saved_amount, target_date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name.strip(), target_amount, saved_amount, target_date or None))
        return int(cursor.lastrowid)


def list_savings_goals(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute(
            "SELECT * FROM savings_goals WHERE user_id = ? ORDER BY created_at", (user_id,)
        ).fetchall()
    return [dict(row) for row in rows]


def delete_savings_goal(user_id: int, goal_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM savings_goals WHERE id = ? AND user_id = ?", (goal_id, user_id))


def add_debt(user_id: int, name: str, balance: float, annual_rate: float,
             minimum_payment: float) -> int:
    if not name.strip() or balance < 0 or annual_rate < 0 or minimum_payment < 0:
        raise ValueError("Enter a name and non-negative debt figures.")
    with _connect() as db:
        cursor = db.execute("""
            INSERT INTO debts (user_id, name, balance, annual_rate, minimum_payment)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, name.strip(), balance, annual_rate, minimum_payment))
        return int(cursor.lastrowid)


def list_debts(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute("SELECT * FROM debts WHERE user_id = ? ORDER BY annual_rate DESC", (user_id,)).fetchall()
    return [dict(row) for row in rows]


def delete_debt(user_id: int, debt_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM debts WHERE id = ? AND user_id = ?", (debt_id, user_id))


def add_holding(user_id: int, ticker: str, shares: float, purchase_price: float,
                dividends: float = 0, acquired_date: str | None = None) -> int:
    ticker = ticker.strip().upper()
    if not ticker or shares <= 0 or purchase_price < 0 or dividends < 0:
        raise ValueError("Enter a ticker, positive share count, and non-negative prices and dividends.")
    with _connect() as db:
        cursor = db.execute("""
            INSERT INTO holdings (user_id, ticker, shares, purchase_price, dividends, acquired_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, ticker, shares, purchase_price, dividends, acquired_date or None))
        return int(cursor.lastrowid)


def list_holdings(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute("SELECT * FROM holdings WHERE user_id = ? ORDER BY ticker, id", (user_id,)).fetchall()
    return [dict(row) for row in rows]


def delete_holding(user_id: int, holding_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM holdings WHERE id = ? AND user_id = ?", (holding_id, user_id))


def add_watchlist_item(user_id: int, ticker: str) -> None:
    ticker = ticker.strip().upper()
    if not ticker:
        raise ValueError("Ticker cannot be empty.")
    try:
        with _connect() as db:
            db.execute("INSERT INTO watchlist (user_id, ticker) VALUES (?, ?)", (user_id, ticker))
    except sqlite3.IntegrityError as error:
        raise ValueError("That ticker is already on your watchlist.") from error


def list_watchlist(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute("SELECT * FROM watchlist WHERE user_id = ? ORDER BY ticker", (user_id,)).fetchall()
    return [dict(row) for row in rows]


def delete_watchlist_item(user_id: int, item_id: int) -> None:
    with _connect() as db:
        db.execute("DELETE FROM watchlist WHERE id = ? AND user_id = ?", (item_id, user_id))


def import_transactions(user_id: int, account_id: int, filename: str,
                        transactions: list[dict[str, Any]]) -> dict[str, int]:
    with _connect() as db:
        owned = db.execute(
            "SELECT 1 FROM financial_accounts WHERE id = ? AND user_id = ?", (account_id, user_id)
        ).fetchone()
        if not owned:
            raise ValueError("That financial account is not available.")
        unique_rows = []
        seen = set()
        for transaction in transactions:
            fingerprint = transaction["fingerprint"]
            if fingerprint not in seen:
                seen.add(fingerprint); unique_rows.append(transaction)
        existing = {row[0] for row in db.execute(
            f"SELECT fingerprint FROM transactions WHERE user_id = ? AND fingerprint IN ({','.join('?' for _ in seen)})",
            [user_id, *seen],
        ).fetchall()} if seen else set()
        new_rows = [row for row in unique_rows if row["fingerprint"] not in existing]
        duplicate_count = len(transactions) - len(new_rows)
        cursor = db.execute("""
            INSERT INTO import_batches (user_id, account_id, filename, imported_count, duplicate_count)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, account_id, filename, len(new_rows), duplicate_count))
        batch_id = int(cursor.lastrowid)
        db.executemany("""
            INSERT INTO transactions
                (user_id, account_id, batch_id, transaction_date, description, amount, category, fingerprint)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [(user_id, account_id, batch_id, row["date"], row["description"], row["amount"],
                row["category"], row["fingerprint"]) for row in new_rows])
    return {"batch_id": batch_id, "imported": len(new_rows), "duplicates": duplicate_count}


def list_import_batches(user_id: int) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute("""
            SELECT b.id, b.filename, b.imported_count, b.duplicate_count, b.created_at,
                   a.name AS account_name
            FROM import_batches b JOIN financial_accounts a ON a.id = b.account_id
            WHERE b.user_id = ? ORDER BY b.id DESC
        """, (user_id,)).fetchall()
    return [dict(row) for row in rows]


def list_transactions(user_id: int, limit: int = 500) -> list[dict[str, Any]]:
    with _connect() as db:
        rows = db.execute("""
            SELECT t.id, t.transaction_date, t.description, t.amount, t.category,
                   a.name AS account_name
            FROM transactions t JOIN financial_accounts a ON a.id = t.account_id
            WHERE t.user_id = ? ORDER BY t.transaction_date DESC, t.id DESC LIMIT ?
        """, (user_id, limit)).fetchall()
    return [dict(row) for row in rows]
