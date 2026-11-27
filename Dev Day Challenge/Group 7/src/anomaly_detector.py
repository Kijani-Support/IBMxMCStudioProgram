"""Registered cautious rules. Rules return evidence-backed findings only."""
from dataclasses import dataclass
import re
from .dossier_loader import Source, section
from .extractors.fields import authorities, tax, overview
from .sector_extractor import extract_sectors


@dataclass
class Rule:
    id: str
    category: str
    description: str
    severity_logic: str
    check: object


def _missing(d):
    fields = {**authorities(d), **tax(d), **overview(d)}
    # Digital service tax is not a universally required dossier field; don't infer absence as a defect.
    fields.pop("digital_taxes", None)
    rows = []
    for field, values in fields.items():
        if not values:
            section_number = 2 if field in {"central_bank", "data_protection"} else 3 if field == "energy_regulator" else 5 if field in {"corporate_income_tax", "vat"} else 1 if field in {"official_languages", "dominant_languages", "regional_blocs"} else 4
            candidates = section(d, section_number)
            source = candidates[0].source if candidates else Source(d.source_file, [d.country], 1, d.lines[0] if d.lines else "")
            rows.append({"country": d.country, "category": "compliance" if field == "regional_blocs" else "tax" if field in {"vat", "corporate_income_tax"} else "regulator" if field in {"central_bank", "data_protection", "energy_regulator"} else "language",
                         "severity": "Medium", "label": "Missing information", "entry": "", "reason": f"{field.replace('_', ' ').title()} not specified in dossier.",
                         "recommendation": "Verify with the relevant authority before launch.", "source": source})
    if not extract_sectors(d):
        candidates = section(d, 4)
        source = candidates[0].source if candidates else Source(d.source_file, [d.country], 1, d.lines[0] if d.lines else "")
        rows.append({"country": d.country, "category": "compliance", "severity": "Medium", "label": "Missing information", "entry": "", "reason": "Section 4 sector content not found.", "recommendation": "Review source dossier and confirm sector obligations.", "source": source})
    return rows


def _rates(d):
    rows = []
    for kind, findings in tax(d).items():
        rates = {}
        for f in findings:
            if "%" in f.value:
                rates.setdefault(f.value, []).append(f)
        if len(rates) > 1 and kind != "digital_taxes":
            for f in findings:
                rows.append({"country": d.country, "category": "tax", "severity": "High", "label": "Internal inconsistency", "entry": f.raw_text,
                             "reason": f"Multiple {kind.replace('_', ' ')} rate claims appear in the dossier.", "recommendation": "Confirm which claim, scope, and effective period apply; this tool selects no winner.", "source": f.source})
    return rows


def _weak_date(d):
    rows = []
    for findings in tax(d).values():
        for f in findings:
            has_explicit_year = re.search(r"\b(?:19|20)\d{2}\b", f.raw_text)
            if "%" in f.value and not has_explicit_year:
                rows.append({"country": d.country, "category": "tax", "severity": "Low", "label": "Potentially outdated", "entry": f.raw_text,
                             "reason": "Rate is stated without an explicit effective date in this entry.", "recommendation": "Check the current finance act and revenue authority guidance.", "source": f.source})
    return rows


RULES = [
    Rule("missing_fields", "compliance", "Explicitly absent key fields", "Medium when a field is absent", _missing),
    Rule("conflicting_tax_rates", "tax", "More than one tax rate claim", "High when distinct rates appear", _rates),
    Rule("rate_without_date", "tax", "A stated rate has no explicit date", "Low; verify currency", _weak_date),
]


def scan(dossiers):
    flags = []
    counts = {rule.id: 0 for rule in RULES}
    for d in dossiers:
        for rule in RULES:
            found = rule.check(d)
            counts[rule.id] += len(found)
            for row in found:
                row["rule_id"] = rule.id
                flags.append(row)
    order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    return sorted(flags, key=lambda x: (order.get(x["severity"], 4), x["country"], x["rule_id"])), counts
