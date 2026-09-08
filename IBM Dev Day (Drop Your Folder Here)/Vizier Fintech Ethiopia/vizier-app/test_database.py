import tempfile
import unittest
from pathlib import Path

import database


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_path = database.DB_PATH
        database.DB_PATH = Path(self.temp_dir.name) / "test.db"
        database.initialize_database()

    def tearDown(self):
        database.DB_PATH = self.original_path
        self.temp_dir.cleanup()

    def test_registration_authentication_and_default_account(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        self.assertEqual(database.authenticate_user("USER@example.com", "correct-horse-123")["id"], user_id)
        self.assertIsNone(database.authenticate_user("user@example.com", "wrong-password"))
        self.assertEqual(database.list_accounts(user_id)[0]["name"], "Main account")

    def test_multiple_accounts_and_monthly_history(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        second_id = database.add_account(user_id, "M-Pesa", "M-Pesa")
        database.save_month(user_id, second_id, "2026-08", 80_000, 20_000, {"Rent": 25_000})
        records = database.list_records(user_id)
        self.assertEqual(len(database.list_accounts(user_id)), 2)
        self.assertEqual(records[0]["account_name"], "M-Pesa")
        self.assertEqual(records[0]["expenses"]["Rent"], 25_000)

    def test_month_upsert_and_export(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        account_id = database.list_accounts(user_id)[0]["id"]
        database.save_month(user_id, account_id, "2026-08", 1_000, 100, {"Food": 400})
        database.save_month(user_id, account_id, "2026-08", 2_000, 200, {"Food": 500})
        self.assertEqual(len(database.list_records(user_id)), 1)
        exported = database.export_user_csv(user_id)
        self.assertIn("Main account,2026-08,2000.0", exported)

    def test_deleting_user_cascades_all_data(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        account_id = database.list_accounts(user_id)[0]["id"]
        database.save_month(user_id, account_id, "2026-08", 1_000, 100, {"Food": 400})
        database.delete_user(user_id)
        self.assertIsNone(database.get_user(user_id))
        self.assertEqual(database.list_accounts(user_id), [])
        self.assertEqual(database.list_records(user_id), [])

    def test_cannot_delete_only_financial_account(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        account_id = database.list_accounts(user_id)[0]["id"]
        with self.assertRaises(ValueError):
            database.delete_financial_account(user_id, account_id)

    def test_budget_goals_and_debts_persist(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        database.upsert_category_budget(user_id, "Healthcare", 5_000)
        database.add_savings_goal(user_id, "Emergency fund", 60_000, 10_000, "2027-01-01")
        database.add_debt(user_id, "Student loan", 100_000, 8.5, 4_000)
        categories = database.list_category_budgets(user_id)
        self.assertTrue(any(item["category"] == "Healthcare" for item in categories))
        self.assertEqual(database.list_savings_goals(user_id)[0]["saved_amount"], 10_000)
        self.assertEqual(database.list_debts(user_id)[0]["annual_rate"], 8.5)

    def test_holdings_and_watchlist_persist(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        holding_id = database.add_holding(user_id, "scom", 100, 20, 250, "2026-01-01")
        database.add_watchlist_item(user_id, "kcb")
        self.assertEqual(database.list_holdings(user_id)[0]["ticker"], "SCOM")
        self.assertEqual(database.list_holdings(user_id)[0]["dividends"], 250)
        self.assertEqual(database.list_watchlist(user_id)[0]["ticker"], "KCB")
        database.delete_holding(user_id, holding_id)
        self.assertEqual(database.list_holdings(user_id), [])

    def test_transaction_import_deduplicates_and_tracks_batches(self):
        user_id = database.create_user("user@example.com", "Test User", "correct-horse-123")
        account_id = database.list_accounts(user_id)[0]["id"]
        rows = [{"date": "2026-08-01", "description": "NAIVAS", "amount": -500,
                 "category": "Food", "fingerprint": "same-row"}]
        first = database.import_transactions(user_id, account_id, "statement.csv", rows)
        second = database.import_transactions(user_id, account_id, "statement.csv", rows)
        self.assertEqual(first["imported"], 1)
        self.assertEqual(second["imported"], 0)
        self.assertEqual(second["duplicates"], 1)
        self.assertEqual(len(database.list_transactions(user_id)), 1)
        self.assertEqual(len(database.list_import_batches(user_id)), 2)


if __name__ == "__main__":
    unittest.main()
