import unittest

from health_score import calculate_health_score
from statement_import import categorize, detect_columns, normalize_rows, read_csv_raw


class StatementImportTests(unittest.TestCase):
    def test_signed_amount_statement(self):
        text = "Date,Description,Amount\n2026-08-01,NAIVAS,-2500\n2026-08-02,Salary,80000\n"
        headers, rows = read_csv_raw(text)
        mapping = detect_columns(headers)
        transactions, errors = normalize_rows(rows, mapping)
        self.assertEqual(errors, [])
        self.assertEqual(transactions[0]["category"], "Food")
        self.assertEqual(transactions[0]["amount"], -2500)
        self.assertEqual(transactions[1]["category"], "Income")

    def test_debit_credit_statement_and_semicolon_detection(self):
        text = "Value Date;Narration;Withdrawal;Deposit\n01/08/2026;KPLC;1500;\n02/08/2026;Salary;;90000\n"
        headers, rows = read_csv_raw(text)
        mapping = detect_columns(headers)
        transactions, errors = normalize_rows(rows, mapping)
        self.assertEqual(errors, [])
        self.assertEqual(transactions[0]["amount"], -1500)
        self.assertEqual(transactions[0]["category"], "Utilities")
        self.assertEqual(transactions[1]["amount"], 90000)

    def test_invalid_rows_are_reported_not_imported(self):
        rows = [{"Date": "not-a-date", "Description": "Shop", "Amount": "100"},
                {"Date": "2026-08-01", "Description": "", "Amount": "100"}]
        transactions, errors = normalize_rows(rows, {"date": "Date", "description": "Description",
                                                      "amount": "Amount", "debit": None, "credit": None})
        self.assertEqual(transactions, [])
        self.assertEqual(len(errors), 2)

    def test_fingerprint_is_stable(self):
        rows = [{"Date": "2026-08-01", "Description": "Shop", "Amount": "-100"}]
        mapping = {"date": "Date", "description": "Description", "amount": "Amount",
                   "debit": None, "credit": None}
        first, _ = normalize_rows(rows, mapping)
        second, _ = normalize_rows(rows, mapping)
        self.assertEqual(first[0]["fingerprint"], second[0]["fingerprint"])


class HealthScoreTests(unittest.TestCase):
    def test_strong_profile_scores_high(self):
        score = calculate_health_score(
            100_000, {"Rent": 25_000, "Food": 10_000, "Utilities": 5_000},
            [{"category": "Rent", "monthly_limit": 30_000}],
            [{"name": "Emergency fund", "saved_amount": 120_000, "target_amount": 200_000}],
            [],
        )
        self.assertGreaterEqual(score["score"], 80)
        self.assertEqual(score["rating"], "Strong")

    def test_at_risk_profile_has_recommendations(self):
        score = calculate_health_score(
            50_000, {"Rent": 40_000, "Food": 20_000},
            [{"category": "Food", "monthly_limit": 10_000}], [],
            [{"minimum_payment": 15_000}],
        )
        self.assertLess(score["score"], 45)
        self.assertTrue(score["recommendations"])


if __name__ == "__main__":
    unittest.main()
