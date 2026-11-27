import hashlib
import sys
import tempfile
import unittest
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.dossier_loader import load_all, discover_files, section
from src.sector_extractor import extract_sectors, all_sector_names
from src.extractors.fields import authorities, tax, overview, numeric_rate
from src.comparison_engine import compare, tax_delta
from src.anomaly_detector import scan
from src.report_generator import brief_data, to_markdown, source_label

FIX = ROOT / "tests" / "fixtures"


def digest_tree(folder):
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file()}


def digest_outside_group(folder):
    group = ROOT.resolve()
    return {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in folder.rglob("*") if p.is_file() and not p.resolve().is_relative_to(group)
            and ".git" not in p.parts}


class ComparatorTests(unittest.TestCase):
    def test_discovery_and_load_and_malformed(self):
        ds = load_all(FIX)
        self.assertEqual({d.country for d in ds}, {"Alpha Republic", "Beta Republic", "Malformed"})
        self.assertIn("malformed.md", {p.name for p in discover_files(FIX)})
        malformed = next(d for d in ds if d.country == "Malformed")
        self.assertFalse(section(malformed, 4))

    def test_sector_and_extractors(self):
        a, b = load_all(FIX)[:2]
        self.assertIn("Retail & ecommerce", all_sector_names([a, b]))
        self.assertIn("Retail & ecommerce", extract_sectors(a))
        self.assertEqual(authorities(a)["central_bank"][0].value, "Reserve Authority")
        self.assertEqual(authorities(a)["data_protection"][0].value, "Privacy Office")
        self.assertEqual(tax(a)["corporate_income_tax"][0].value, "20%")
        self.assertEqual(overview(a)["official_languages"][0].value, "Examplean")
        self.assertEqual(overview(a)["official_languages"][1].value, "Examplean Two (Formal, Local)")

    def test_comparison_and_pp_calculation(self):
        a, b = load_all(FIX)[:2]
        comp = compare(a, b, "Retail & ecommerce")
        self.assertIsNotNone(comp["similarity"])
        self.assertEqual(numeric_rate("20–25%"), None)
        delta = tax_delta(tax(a)["corporate_income_tax"][0], tax(b)["corporate_income_tax"][0])
        self.assertEqual(delta["percentage_points"], 5)
        self.assertEqual(len(delta["sources"]), 2)

    def test_missing_and_conflict_rules_positive_negative(self):
        a, b = load_all(FIX)[:2]
        flags, counts = scan([a, b])
        self.assertGreater(counts["missing_fields"], 0)  # missing beta spoken languages and fixture omissions
        self.assertEqual(counts["conflicting_tax_rates"], 0)
        self.assertTrue(any(f["rule_id"] == "missing_fields" for f in flags))
        self.assertTrue(all(f["source"] is not None for f in flags if f["rule_id"] == "missing_fields"))
        # Synthetic duplicate claim creates positive contradiction; original has none.
        a.lines.extend(["| Standard corporate income tax | 22% |"])
        a.sections["5. Tax planning"].append(a.sections["5. Tax planning"][-1])
        a.sections["5. Tax planning"][-1].raw_text = "| Standard corporate income tax | 22% |"
        a.sections["5. Tax planning"][-1].value = "| Standard corporate income tax | 22% |"
        found, _ = scan([a])
        self.assertTrue(any(f["rule_id"] == "conflicting_tax_rates" for f in found))

    def test_report_sources_and_numeric_provenance(self):
        a, b = load_all(FIX)[:2]
        c = compare(a, b, "Retail & ecommerce")
        rows = {"corporate_income_tax": [(a.country, tax(a)["corporate_income_tax"][0]), (b.country, tax(b)["corporate_income_tax"][0])], "vat": []}
        data = brief_data(a, b, "Retail & ecommerce", c, rows, [])
        md = to_markdown(data)
        self.assertIn("20%", md)
        self.assertIn("alpha.md", md)
        self.assertIn("beta.md", md)
        self.assertIn("not legal or tax advice", md.lower())
        delta = tax_delta(rows["corporate_income_tax"][0][1], rows["corporate_income_tax"][1][1])
        self.assertEqual(len(delta["sources"]), 2)
        self.assertIn(source_label(delta["sources"][0]), md)
        self.assertIn(source_label(delta["sources"][1]), md)
        lines = md.splitlines()
        for index, line in enumerate(lines):
            if re.search(r"\b\d+(?:\.\d+)?%", line):
                nearby = " ".join(lines[max(0, index - 1):index + 1])
                self.assertTrue("alpha.md" in nearby or "beta.md" in nearby, f"Uncited numeric figure: {line}")
            if "percentage points" in line:
                self.assertIn("alpha.md", line)
                self.assertIn("beta.md", line)

    def test_writes_stay_in_group_and_dossier_tree_unchanged(self):
        workspace = ROOT.parents[1]
        dossier_root = workspace / "africa-regulatory"
        before = digest_tree(dossier_root)
        outside_before = digest_outside_group(workspace)
        real_dossiers = load_all()
        scan(real_dossiers)
        from src.report_generator import brief_data, to_markdown
        home, target = next(d for d in real_dossiers if d.country == "Kenya"), next(d for d in real_dossiers if d.country == "Tanzania")
        result = compare(home, target, "Retail & ecommerce")
        to_markdown(brief_data(home, target, "Retail & ecommerce", result, {}, []))
        with tempfile.NamedTemporaryFile(dir=ROOT, prefix="scope-check-", delete=True) as f:
            self.assertTrue(Path(f.name).resolve().is_relative_to(ROOT.resolve()))
        self.assertEqual(before, digest_tree(dossier_root))
        self.assertEqual(outside_before, digest_outside_group(workspace))

    def test_source_has_no_country_facts(self):
        source = "\n".join(p.read_text(encoding="utf-8") for p in [ROOT / "app.py", * (ROOT / "src").rglob("*.py")])
        # Generic source-code grep guard for examples of forbidden dossier facts.
        country_rate_pattern = r"(?<!\d)(?:1\d|2\d|3\d)(?:\.\d+)?\s*%"
        self.assertIsNone(re.search(country_rate_pattern, source), "Country tax rate embedded in source")
        self.assertIsNone(re.search(r"Central\s+Bank\s+of\s+[A-Z]", source), "Country regulator name embedded in source")


if __name__ == "__main__":
    unittest.main()
