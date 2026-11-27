"""Conservative, source-preserving field extraction."""
from ..dossier_loader import Dossier, Finding, Source, section
import re


def _field(d: Dossier, section_number: int, label: str) -> list[Finding]:
    result = []
    for f in section(d, section_number):
        m = re.search(rf"(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*[:|]\s*(.+?)(?:\s*\|\s*)?$", f.raw_text, re.I)
        if m:
            value = m.group(1).strip().strip("*")
            result.append(Finding(value, f.raw_text, f.source, "high", False))
    return result


def authorities(d: Dossier) -> dict[str, list[Finding]]:
    # Labels occur in prose; take the text through the next sentence boundary conservatively.
    out = {}
    for key, label in [("central_bank", "Central bank"), ("data_protection", "Data protection"), ("energy_regulator", "Regulator / authority")]:
        vals = []
        for f in section(d, 2 if key != "energy_regulator" else 3):
            m = re.search(rf"(?:\*\*)?{re.escape(label)}(?:\*\*)?\s*:\s*(.+?)(?=\s+[—–]\s|\.)", f.raw_text, re.I)
            if m:
                vals.append(Finding(m.group(1).strip().strip("* "), f.raw_text, f.source, "medium", "verify" in m.group(1).lower()))
        out[key] = vals
    return out


def tax(d: Dossier) -> dict[str, list[Finding]]:
    out = {"corporate_income_tax": [], "vat": [], "digital_taxes": []}
    for f in section(d, 5):
        text = f.raw_text
        m = re.match(r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|?$", text)
        if m:
            label, value = m.group(1).strip().lower(), m.group(2).strip()
            key = "corporate_income_tax" if "corporate income tax" in label else "vat" if "vat" in label or "sales tax" in label else None
            if key:
                out[key].append(Finding(value, text, f.source, "high", "verify" in value.lower()))
        elif re.search(r"digital service|digital tax|digital economy tax", text, re.I):
            out["digital_taxes"].append(Finding(text, text, f.source, "low", True))
    return out


def overview(d: Dossier) -> dict[str, list[Finding]]:
    out = {"official_languages": [], "dominant_languages": [], "regional_blocs": []}
    for f in section(d, 1):
        m = re.match(r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|?$", f.raw_text)
        if not m:
            continue
        key = m.group(1).strip().lower()
        target = "official_languages" if key == "official languages" else "dominant_languages" if "dominant spoken languages" in key else "regional_blocs" if key == "regional blocs" else None
        if target:
            value = m.group(2).strip()
            if target in {"official_languages", "dominant_languages"}:
                parts, depth, start = [], 0, 0
                for i, char in enumerate(value):
                    depth += (char == "(") - (char == ")")
                    if char == "," and depth == 0:
                        parts.append(value[start:i].strip())
                        start = i + 1
                parts.append(value[start:].strip())
            else:
                parts = re.split(r";\s*", value)
            out[target] = [Finding(part.strip(), f.raw_text, f.source, "high", False) for part in parts if part.strip()]
    return out


def numeric_rate(text: str) -> float | None:
    if re.search(r"\d\s*[–—-]\s*\d|\bnone\b", text, re.I):
        return None
    vals = re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)\s*%", text)
    return float(vals[0]) if len(vals) == 1 else None
