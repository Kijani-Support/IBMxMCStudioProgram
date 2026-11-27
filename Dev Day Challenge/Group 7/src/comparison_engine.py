from difflib import SequenceMatcher
from .sector_extractor import extract_sectors
from .extractors.fields import numeric_rate

MATCH_THRESHOLD = 0.72


def compare(home, target, sector):
    h = extract_sectors(home).get(sector)
    t = extract_sectors(target).get(sector)
    if not h or not t:
        return {"home": h, "target": t, "similarity": None, "status": "Missing or unclear"}
    score = SequenceMatcher(None, h.value.casefold(), t.value.casefold()).ratio()
    return {"home": h, "target": t, "similarity": score, "status": "Likely equivalent" if score >= MATCH_THRESHOLD else "Different / review"}


def tax_delta(home_finding, target_finding):
    if not home_finding or not target_finding:
        return None
    a, b = numeric_rate(home_finding.value), numeric_rate(target_finding.value)
    if a is None or b is None:
        return None
    return {"percentage_points": b - a, "home_input": a, "target_input": b,
            "sources": [home_finding.source, target_finding.source]}
