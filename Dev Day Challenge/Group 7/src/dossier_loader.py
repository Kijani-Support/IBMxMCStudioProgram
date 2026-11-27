"""Runtime discovery and line-aware loading of country dossier Markdown."""
from dataclasses import dataclass
from pathlib import Path
import os
import re

DEFAULT_DOSSIER_DIR = Path(__file__).resolve().parents[3] / "africa-regulatory"


@dataclass
class Source:
    file: str
    heading_path: list[str]
    line: int
    excerpt: str


@dataclass
class Finding:
    value: object
    raw_text: str
    source: Source
    confidence: str = "high"
    needs_review: bool = False


@dataclass
class Dossier:
    country: str
    source_file: str
    raw_markdown_path: str
    lines: list[str]
    headings: list[tuple[int, int, str]]
    sections: dict[str, list[Finding]]
    errors: list[str]


def dossier_dir() -> Path:
    return Path(os.environ.get("AFRICA_REGULATORY_DIR", str(DEFAULT_DOSSIER_DIR))).expanduser().resolve()


def discover_files(directory: Path | None = None) -> list[Path]:
    root = directory or dossier_dir()
    if not root.is_dir():
        raise FileNotFoundError(f"Dossier directory not found: {root}")
    return sorted(p for p in root.glob("*.md") if p.name.lower() not in {"readme.md", "_template.md"})


def _parse(path: Path) -> Dossier:
    raw = path.read_text(encoding="utf-8")
    lines = raw.splitlines()
    headings: list[tuple[int, int, str]] = []
    for i, line in enumerate(lines, 1):
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            headings.append((len(m.group(1)), i, m.group(2).strip()))
    title = next((h for level, _, h in headings if level == 1), path.stem.replace("-", " ").title())
    country = re.split(r"\s+[—–-]\s+", title, maxsplit=1)[0].strip()
    sections: dict[str, list[Finding]] = {}
    stack: list[tuple[int, str]] = []
    heading_by_line = {line: (level, text) for level, line, text in headings}
    for i, line in enumerate(lines, 1):
        if i in heading_by_line:
            level, text = heading_by_line[i]
            while stack and stack[-1][0] >= level:
                stack.pop()
            stack.append((level, text))
        path_text = [h for _, h in stack]
        section = next((h for lvl, h in reversed(stack) if lvl == 2), "")
        if line.strip():
            sections.setdefault(section, []).append(Finding(line.strip(), line.strip(), Source(path.name, path_text, i, line.strip())))
    errors = []
    if not headings:
        errors.append("No Markdown headings found")
    if not country:
        errors.append("Country title could not be derived")
    return Dossier(country, path.name, str(path.resolve()), lines, headings, sections, errors)


def load_all(directory: Path | None = None) -> list[Dossier]:
    return [_parse(path) for path in discover_files(directory)]


def section(dossier: Dossier, number: int) -> list[Finding]:
    prefix = f"{number}."
    for title, findings in dossier.sections.items():
        if title.startswith(prefix):
            return findings
    return []
