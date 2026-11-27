from .dossier_loader import Dossier, Finding, Source, section
from .markdown_parser import is_separator
import re


def extract_sectors(d: Dossier) -> dict[str, Finding]:
    rows: dict[str, Finding] = {}
    fs = section(d, 4)
    if not fs:
        return rows
    lines = d.lines
    begin = min(f.source.line for f in fs) - 1
    end = max(f.source.line for f in fs)
    for i in range(begin, end):
        if "|" not in lines[i] or i + 1 >= end or not is_separator(lines[i + 1]):
            continue
        for j in range(i + 2, end):
            if "|" not in lines[j]:
                break
            cells = [c.strip().strip("*") for c in lines[j].strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0].strip().lower() == "sector":
                continue
            name, raw = cells[0], cells[1]
            if name:
                rows[name] = Finding(raw, lines[j].strip(), Source(d.source_file, ["4. Sector compliance steps"], j + 1, lines[j].strip()), "high", False)
    return rows


def all_sector_names(dossiers: list[Dossier]) -> list[str]:
    names = {}
    for d in dossiers:
        for name in extract_sectors(d):
            names.setdefault(re.sub(r"\s+", " ", name).strip().casefold(), name)
    return sorted(names.values(), key=str.casefold)
