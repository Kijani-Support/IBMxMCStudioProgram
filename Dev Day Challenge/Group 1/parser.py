"""Passerelle (EN: "Gateway") — Template-Driven Dossier Parser & Corpus Profiler.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Load country regulatory dossiers from ``africa-regulatory/``, align them against
    ``_template.md`` and corpus-level boilerplate affixes, and extract every data point
    into provenance-carrying ``Field`` objects (value, file, section, line, raw). Also
    produces a full corpus profile saved to ``data/corpus_profile.json``.

Inputs:
    Path to the directory containing ``_template.md`` and the 54 country ``*.md``
    dossiers (defaults to the repository's ``africa-regulatory/`` folder).

Outputs:
    Structured dossier dictionaries containing ``Field`` objects, lists of ``Field``
    objects for multi-value cells, and ``parse_notes`` recording any missing fields or
    template deviations. When executed as a script, prints and writes
    ``data/corpus_profile.json``.

Failure behaviour:
    Missing sections, malformed tables, or unexpected cell formats never raise unhandled
    exceptions during parsing; they are recorded in ``parse_notes`` so downstream
    validators can surface them as Verify-first flags. Only ``discover_dossier_files``
    asserts the expected corpus count when explicitly requested.
"""

from __future__ import annotations

import difflib
import json
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

# Regional blocs whose official/working monetary union language is French.
# Used purely for corpus language-profile diagnostics (not country-specific logic).
FRANCOPHONE_BLOCS: frozenset[str] = frozenset({"CEMAC", "WAEMU"})

# Placeholder patterns to count across dossier sections.
PLACEHOLDER_RE = re.compile(r"\b(verify|tbd|n/a)\b", re.IGNORECASE)

# Numeric pattern supporting integers, decimals, and percentages.
NUMBER_RE = re.compile(r"\d+(?:\.\d+)?")

# ISO 4217 three-letter uppercase currency code inside parentheses, plus mixed-case fallback.
ISO_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
ALPHA3_CURRENCY_RE = re.compile(r"^[A-Za-z]{3}$")

# Parenthetical groups inside a cell, e.g. "(XAF)" or "(CEMAC / BEAC)".
PAREN_GROUP_RE = re.compile(r"\(([^()]+)\)")

# Acronym extraction patterns for data-protection authority names:
# matches "ACRONYM (Full Name)" or "Full Name (ACRONYM)" (allowing trailing qualifier).
LEADING_ACRONYM_RE = re.compile(r"^([A-Z][A-Z0-9-]{1,12})\s*\(([^)]+)\)\s*$")
TRAILING_ACRONYM_RE = re.compile(r"^(.+?)\s*\(([A-Z][A-Z0-9-]{1,12})(?:[;,][^)]*)?\)\s*$")

# Known monetary-zone descriptor strings that indicate a national (non-union) currency.
NATIONAL_CURRENCY_MARKERS = ("national currency", "national", "domestic")


@dataclass
class Field:
    """Single extracted dossier datum with immutable line-level provenance.

    Purpose:
        Carry both the parsed value and its exact dossier citation (file, section,
        1-based line number, and raw line) through the entire Passerelle pipeline.

    Inputs:
        value: Cleaned extracted text for this field.
        file: Dossier filename (basename only, e.g. ``dossier.md``).
        section: Section identifier (``"0"`` for header metadata, ``"1"``–``"6"`` for
            numbered sections).
        line: 1-based line number in the source dossier file.
        raw: Exact raw line from the dossier supporting this value.
        canonical: Optional normalized key (used for bloc canonical keys).
        qualifier: Optional parenthetical qualifier (e.g. ``"observer"`` or ``"UEMOA"``).
        is_boilerplate: True when the sentence/row is generic corpus boilerplate.
        meta: Optional structured metadata (e.g. extracted tax numbers list).

    Outputs:
        Dataclass instance serialisable via ``to_dict()`` and citable via ``citation()``.

    Failure behaviour:
        Pure data container; never raises on construction with valid argument types.
    """

    value: str
    file: str
    section: str
    line: int
    raw: str
    canonical: Optional[str] = None
    qualifier: Optional[str] = None
    is_boilerplate: bool = False
    meta: dict[str, Any] = field(default_factory=dict)

    def citation(self) -> str:
        """Format the standard inline provenance citation string.

        Purpose:
            Produce the exact ``(source: <file> §<section>, line <n>)`` tag required
            by hard rule R2.

        Inputs:
            None (uses instance provenance fields).

        Outputs:
            Formatted citation string.

        Failure behaviour:
            Never raises.
        """
        return f"(source: {self.file} §{self.section}, line {self.line})"

    def to_dict(self) -> dict[str, Any]:
        """Convert this Field into a JSON-serialisable dictionary.

        Purpose:
            Allow clean JSON persistence for ``facts.json`` and corpus profiles.

        Inputs:
            None.

        Outputs:
            Dictionary representation of all Field attributes.

        Failure behaviour:
            Never raises.
        """
        return asdict(self)


@dataclass
class TemplateSpec:
    """Structural specification parsed at runtime from ``_template.md``.

    Purpose:
        Anchor dossier parsing in ``_template.md`` rather than hard-coded regexes or
        punctuation splits, capturing expected sections, table fields, and slot labels.

    Inputs:
        template_path: Path to ``_template.md``.
        title_suffix: Fixed title suffix after ``{Country}`` in line 1.
        expected_sections: Mapping of section number strings to expected heading titles.
        overview_fields: Ordered list of Section 1 table field labels.
        slot_labels: Mapping of section numbers to expected slot prefixes from template.
        corpus_affixes: Optional mapping of slot keys to ``(prefix, suffix)`` tuples
            discovered across the corpus so prose boilerplate is stripped cleanly
            without splitting on periods or dashes.

    Outputs:
        TemplateSpec instance consumed by ``parse_dossier`` and ``parse_corpus``.

    Failure behaviour:
        Defaults to empty collections if ``_template.md`` is missing or truncated;
        callers record a parse note and fall back to heading/bold-label parsing.
    """

    template_path: str
    title_suffix: str = ""
    expected_sections: dict[str, str] = field(default_factory=dict)
    overview_fields: list[str] = field(default_factory=list)
    slot_labels: dict[str, list[str]] = field(default_factory=dict)
    corpus_affixes: dict[str, tuple[str, str]] = field(default_factory=dict)


def default_dossier_dir() -> Path:
    """Locate the repository's ``africa-regulatory/`` folder relative to Group 1.

    Purpose:
        Resolve the canonical dossier directory without hard-coding absolute machine
        paths.

    Inputs:
        None.

    Outputs:
        ``Path`` pointing to ``africa-regulatory/``.

    Failure behaviour:
        Returns the computed path even if it does not exist; callers check existence.
    """
    return Path(__file__).resolve().parents[2] / "africa-regulatory"


def discover_dossier_files(
    dossier_dir: Path | str | None = None,
    expect_count: Optional[int] = 54,
) -> list[Path]:
    """Discover all country dossier ``*.md`` files, excluding templates and README.

    Purpose:
        Load every ``*.md`` in ``africa-regulatory/`` except files whose name starts
        with ``"_"`` and ``README.md``, sorted deterministically.

    Inputs:
        dossier_dir: Optional directory path; defaults to ``africa-regulatory/``.
        expect_count: Expected number of dossiers (default 54). Pass ``None`` when
            loading custom test fixture directories.

    Outputs:
        Sorted list of ``Path`` objects for the country dossiers.

    Failure behaviour:
        Raises ``FileNotFoundError`` if ``dossier_dir`` does not exist, or
        ``AssertionError`` if ``expect_count`` is set and the discovered count differs.
    """
    target = Path(dossier_dir) if dossier_dir is not None else default_dossier_dir()
    if not target.is_dir():
        raise FileNotFoundError(f"Dossier directory not found: {target}")

    files = sorted(
        p
        for p in target.glob("*.md")
        if not p.name.startswith("_") and p.name.lower() != "readme.md"
    )
    if expect_count is not None:
        assert len(files) == expect_count, (
            f"Expected {expect_count} country dossiers in {target}, found {len(files)}"
        )
    return files


def load_template_spec(dossier_dir: Path | str | None = None) -> TemplateSpec:
    """Read ``_template.md`` and derive expected headings, table fields, and slots.

    Purpose:
        Build a ``TemplateSpec`` directly from ``_template.md`` at runtime so the
        parser checks dossiers against the authoritative template rather than static
        assumptions.

    Inputs:
        dossier_dir: Directory containing ``_template.md`` (defaults to
            ``africa-regulatory/``).

    Outputs:
        Populated ``TemplateSpec`` object.

    Failure behaviour:
        If ``_template.md`` does not exist or cannot be read, returns an empty
        ``TemplateSpec`` so the parser still succeeds via fallback heading/bold rules.
    """
    target_dir = Path(dossier_dir) if dossier_dir is not None else default_dossier_dir()
    template_path = target_dir / "_template.md"
    spec = TemplateSpec(template_path=str(template_path))
    if not template_path.is_file():
        return spec

    lines = template_path.read_text(encoding="utf-8", errors="replace").splitlines()
    current_section = "0"

    for raw in lines:
        line = raw.strip()
        if not line:
            continue

        # Capture title suffix from line 1 template pattern: "# {Country} <suffix>".
        if line.startswith("# ") and "{Country}" in line and not spec.title_suffix:
            spec.title_suffix = line.split("{Country}", 1)[1]
            continue

        # Capture canonical numbered section headings: "## N. Title".
        sec_match = re.match(r"^##\s+(\d+)\.\s+(.+)$", line)
        if sec_match:
            current_section = sec_match.group(1)
            spec.expected_sections[current_section] = sec_match.group(2).strip()
            continue

        # Capture Section 1 table field names from the template table.
        if current_section == "1" and line.startswith("|") and line.endswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) >= 2 and cells[0].lower() != "field" and not set(cells[0]) <= {"-", ":"}:
                spec.overview_fields.append(cells[0])
            continue

        # Capture slot label prefixes containing "{name}" in prose sections (e.g. §2, §3).
        if "{name}" in line and ":" in line:
            prefix = line.split("{name}", 1)[0].strip()
            spec.slot_labels.setdefault(current_section, []).append(prefix)

    return spec


def _longest_common_prefix(strings: list[str]) -> str:
    """Compute the longest common prefix across a non-empty list of strings.

    Purpose:
        Identify fixed boilerplate text preceding a variable slot across the corpus.

    Inputs:
        strings: List of lines sharing a template slot.

    Outputs:
        Longest shared prefix string, or empty string if input is empty.

    Failure behaviour:
        Never raises.
    """
    if not strings:
        return ""
    shortest = min(strings, key=len)
    for idx, ch in enumerate(shortest):
        if any(s[idx] != ch for s in strings):
            return shortest[:idx]
    return shortest


def _longest_common_suffix(strings: list[str]) -> str:
    """Compute the longest common suffix across a non-empty list of strings.

    Purpose:
        Identify fixed boilerplate text trailing a variable slot across the corpus so
        slot extraction strips the exact boilerplate instead of splitting on ``.`` or
        ``—``.

    Inputs:
        strings: List of lines sharing a template slot.

    Outputs:
        Longest shared suffix string, or empty string if input is empty.

    Failure behaviour:
        Never raises.
    """
    if not strings:
        return ""
    rev = [s[::-1] for s in strings]
    return _longest_common_prefix(rev)[::-1]


def _modal_common_affix(lines: list[str], fixed_prefix: str) -> Optional[tuple[str, str]]:
    """Derive the modal (prefix, suffix) boilerplate frame for a slot across dossiers.

    Purpose:
        Keep the prefix anchored strictly to the template/bold label so slot text
        (such as leading letters shared by many bank names) is never consumed, and
        find the longest trailing boilerplate suffix shared by >= 85% of lines so
        closing punctuation belonging to a subset of slot values is never consumed.

    Inputs:
        lines: Non-empty list of raw lines matching a slot anchor across dossiers.
        fixed_prefix: Exact label prefix (e.g. ``"**Central bank:** "``).

    Outputs:
        ``(prefix, suffix)`` tuple if a stable boilerplate suffix is shared by at
        least 85% of lines, else ``None``.

    Failure behaviour:
        Returns ``None`` if fewer than 2 lines are provided or no stable suffix exists.
    """
    matching = [ln for ln in lines if ln.startswith(fixed_prefix)]
    if len(matching) < 2:
        return None

    bodies = [ln[len(fixed_prefix) :] for ln in matching]
    # Pairwise longest common suffixes against a spread of anchor lines so a single
    # deviating file cannot collapse the shared suffix.
    suffix_counts: Counter[str] = Counter()
    step = max(1, len(bodies) // 6)
    anchors = bodies[::step][:6]

    for anchor in anchors:
        for other in bodies:
            if other == anchor:
                continue
            lcs = _longest_common_suffix([anchor, other])
            if lcs:
                suffix_counts[lcs] += 1

    if not suffix_counts:
        return None

    # Require >= 85% corpus support so only genuine template-wide boilerplate is
    # treated as the fixed suffix, never a trailing ')' or common phrase in ~50% of slots.
    threshold = max(2, int(len(bodies) * 0.85))
    best_suffix = ""
    for cand, _ in suffix_counts.most_common(30):
        support = sum(1 for b in bodies if b.endswith(cand))
        if support >= threshold and len(cand) > len(best_suffix):
            best_suffix = cand

    if not best_suffix:
        return None
    # Never let a closing parenthesis belonging to slot text (e.g. "(verify...)") be
    # absorbed into the boilerplate suffix; start the suffix at the delimiter itself.
    if best_suffix.startswith(")"):
        best_suffix = best_suffix.lstrip(")")
    return (fixed_prefix, best_suffix)


def enrich_template_with_corpus_affixes(
    spec: TemplateSpec,
    files: list[Path],
) -> TemplateSpec:
    """Learn fixed slot prefix/suffix boilerplate frames from the dossier corpus.

    Purpose:
        Complement ``_template.md`` with exact corpus-level fixed boilerplate around
        prose slots (central bank, data protection, energy regulator) so variable slot
        values are carved out by template/boilerplate diffing rather than punctuation
        splitting.

    Inputs:
        spec: ``TemplateSpec`` loaded from ``_template.md``.
        files: List of dossier ``Path`` objects in the corpus.

    Outputs:
        The updated ``TemplateSpec`` with ``corpus_affixes`` populated.

    Failure behaviour:
        Silently skips unreadable files and leaves ``corpus_affixes`` empty for any
        slot without a consistent frame.
    """
    slot_buckets: dict[str, list[str]] = defaultdict(list)
    slot_anchors = {
        "central_bank": "**Central bank:** ",
        "data_protection": "**Data protection:** ",
        "energy_regulator": "**Regulator / authority:** ",
    }

    for path in files:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for raw in text.splitlines():
            stripped = raw.strip()
            for key, anchor in slot_anchors.items():
                if stripped.startswith(anchor):
                    slot_buckets[key].append(stripped)

    for key, lines in slot_buckets.items():
        affix = _modal_common_affix(lines, fixed_prefix=slot_anchors[key])
        if affix is not None:
            spec.corpus_affixes[key] = affix

    return spec


def _extract_slot_by_affix(
    line: str,
    slot_key: str,
    bold_label: str,
    spec: TemplateSpec,
    file_name: str,
    section: str,
    line_num: int,
    parse_notes: list[dict[str, Any]],
) -> tuple[str, str]:
    """Extract a variable slot and trailing prose via template/boilerplate diffing.

    Purpose:
        Isolate a country-specific value by stripping the known fixed prefix and
        boilerplate suffix (or aligning via ``difflib.SequenceMatcher``) instead of
        naively splitting on ``.`` or ``—``. Falls back to bold-label extraction with
        a recorded parse note when a file deviates.

    Inputs:
        line: Stripped source line containing the slot.
        slot_key: Key in ``spec.corpus_affixes`` (e.g. ``"central_bank"``).
        bold_label: Expected bold label prefix (e.g. ``"**Central bank:**"``).
        spec: Loaded ``TemplateSpec``.
        file_name: Source filename for parse-note provenance.
        section: Section number string for parse-note provenance.
        line_num: 1-based line number for parse-note provenance.
        parse_notes: Mutable list receiving any deviation/fallback notes.

    Outputs:
        Tuple ``(slot_value, trailing_prose)``.

    Failure behaviour:
        Never raises; returns ``("", line)`` and records a parse note if extraction
        cannot isolate a value.
    """
    affix = spec.corpus_affixes.get(slot_key)
    if affix is not None:
        prefix, suffix = affix
        if line.startswith(prefix) and suffix and line.endswith(suffix):
            end_idx = len(line) - len(suffix)
            if end_idx >= len(prefix):
                slot_val = line[len(prefix) : end_idx].strip()
                # Preserve clean trailing prose without leading punctuation delimiter.
                prose = suffix.lstrip(".—- ").strip()
                return slot_val, prose

        # If the line starts with the prefix but the suffix deviates slightly, align
        # against the known boilerplate suffix using SequenceMatcher so we avoid
        # punctuation splitting and record the deviation as a parse note.
        if line.startswith(prefix) and suffix:
            rest = line[len(prefix) :]
            matcher = difflib.SequenceMatcher(None, rest, suffix)
            match = matcher.find_longest_match(0, len(rest), 0, len(suffix))
            if match.size >= max(15, int(len(suffix) * 0.4)):
                parse_notes.append(
                    {
                        "file": file_name,
                        "section": section,
                        "line": line_num,
                        "kind": "template_deviation",
                        "message": (
                            f"Line for '{slot_key}' deviated from standard boilerplate; "
                            "isolated slot via SequenceMatcher alignment."
                        ),
                        "raw": line,
                    }
                )
                slot_val = rest[: match.a].strip().rstrip(".—- ")
                prose = rest[match.a :].lstrip(".—- ").strip()
                return slot_val, prose

    # Fallback: strip the bold label (or plain label from _template.md) and record note.
    parse_notes.append(
        {
            "file": file_name,
            "section": section,
            "line": line_num,
            "kind": "fallback_label_parse",
            "message": (
                f"Used fallback label extraction for '{slot_key}' because corpus "
                "boilerplate frame did not match."
            ),
            "raw": line,
        }
    )

    body = line
    if body.lower().startswith(bold_label.lower()):
        body = body[len(bold_label) :].strip()
    else:
        plain_label = bold_label.replace("**", "")
        if body.lower().startswith(plain_label.lower()):
            body = body[len(plain_label) :].strip()

    # Fallback boundary only when template diffing was unavailable (standalone broken file).
    for sep in (" — ", ". "):
        if sep in body:
            head, tail = body.split(sep, 1)
            return head.strip(), tail.strip()
    return body.strip().rstrip("."), ""


def _extract_top_level_parens(text: str) -> list[tuple[int, int, str]]:
    """Extract balanced top-level ``(...)`` groups so nested parens stay intact.

    Purpose:
        Handle Currency cells like ``"Example Franc (XYZ) (national currency (pegged to EUR))"``
        without losing the outer ``national currency`` descriptor to a non-nested regex.

    Inputs:
        text: Source cell string.

    Outputs:
        List of ``(start_idx, end_idx, inner_text)`` tuples for each top-level group.

    Failure behaviour:
        Ignores unmatched closing parentheses; never raises.
    """
    groups: list[tuple[int, int, str]] = []
    depth = 0
    start = -1
    for idx, ch in enumerate(text):
        if ch == "(":
            if depth == 0:
                start = idx
            depth += 1
        elif ch == ")" and depth > 0:
            depth -= 1
            if depth == 0 and start != -1:
                groups.append((start, idx + 1, text[start + 1 : idx].strip()))
                start = -1
    return groups


def _parse_currency_cell(
    cell_value: str,
    file_name: str,
    line_num: int,
    raw_line: str,
    parse_notes: list[dict[str, Any]],
) -> dict[str, Optional[Field]]:
    """Parse a Section 1 Currency cell into name, code, bloc, and bank Fields.

    Purpose:
        Decompose cells like ``"Central African CFA franc (XAF) (CEMAC / BEAC)"`` or
        ``"Example Shilling (XYZ) (national currency)"`` into separate provenance-tagged
        ``Field`` objects where ``currency_bloc`` and ``currency_bank`` are optional.

    Inputs:
        cell_value: Trimmed value from the Currency table cell.
        file_name: Dossier filename.
        line_num: 1-based line number of the Currency row.
        raw_line: Original raw markdown table row.
        parse_notes: Mutable list receiving parse notes on unexpected shapes.

    Outputs:
        Dict with keys ``currency_name``, ``currency_code``, ``currency_bloc``,
        ``currency_bank``, and ``currency_zone_raw`` (each ``Field`` or ``None``).

    Failure behaviour:
        Never raises; records a parse note if no 3-letter ISO code or unexpected
        monetary-zone format is encountered.
    """
    result: dict[str, Optional[Field]] = {
        "currency_name": None,
        "currency_code": None,
        "currency_bloc": None,
        "currency_bank": None,
        "currency_zone_raw": None,
    }
    if not cell_value:
        parse_notes.append(
            {
                "file": file_name,
                "section": "1",
                "line": line_num,
                "kind": "missing_value",
                "message": "Currency cell is empty.",
                "raw": raw_line,
            }
        )
        return result

    groups = _extract_top_level_parens(cell_value)
    name_part = cell_value[: groups[0][0]].strip() if groups else cell_value.strip()
    if name_part:
        result["currency_name"] = Field(
            value=name_part,
            file=file_name,
            section="1",
            line=line_num,
            raw=raw_line,
        )

    zone_candidates: list[str] = []
    for _, _, content in groups:
        if result["currency_code"] is None and ISO_CURRENCY_RE.match(content):
            result["currency_code"] = Field(
                value=content,
                file=file_name,
                section="1",
                line=line_num,
                raw=raw_line,
            )
        elif result["currency_code"] is None and ALPHA3_CURRENCY_RE.match(content):
            # Capture non-standard mixed-case 3-letter ticker (still flagging it) so
            # downstream profiling and validators see the raw token rather than None.
            result["currency_code"] = Field(
                value=content,
                file=file_name,
                section="1",
                line=line_num,
                raw=raw_line,
            )
            parse_notes.append(
                {
                    "file": file_name,
                    "section": "1",
                    "line": line_num,
                    "kind": "non_iso_currency_code",
                    "message": (
                        f"Currency code '{content}' is mixed-case rather than a standard "
                        "uppercase ISO 4217 3-letter code."
                    ),
                    "raw": raw_line,
                }
            )
        else:
            zone_candidates.append(content)

    if result["currency_code"] is None:
        # Check for multi-code or non-standard ISO token inside parentheticals so we
        # preserve visibility without crashing.
        parse_notes.append(
            {
                "file": file_name,
                "section": "1",
                "line": line_num,
                "kind": "unusual_currency_code",
                "message": f"Could not isolate a 3-letter ISO currency code in '{cell_value}'.",
                "raw": raw_line,
            }
        )

    if zone_candidates:
        zone_raw = " ; ".join(zone_candidates)
        result["currency_zone_raw"] = Field(
            value=zone_raw,
            file=file_name,
            section="1",
            line=line_num,
            raw=raw_line,
        )
        # Parse "<bloc> / <bank>" when present; national currencies legitimately omit both.
        primary_zone = zone_candidates[-1]
        if "/" in primary_zone:
            parts = [p.strip() for p in primary_zone.split("/", 1)]
            if parts[0]:
                result["currency_bloc"] = Field(
                    value=parts[0],
                    file=file_name,
                    section="1",
                    line=line_num,
                    raw=raw_line,
                )
            if len(parts) > 1 and parts[1]:
                result["currency_bank"] = Field(
                    value=parts[1],
                    file=file_name,
                    section="1",
                    line=line_num,
                    raw=raw_line,
                )
        elif not any(marker in primary_zone.lower() for marker in NATIONAL_CURRENCY_MARKERS):
            # Non-national monetary zone descriptor without "/" separator (e.g. pegged
            # or common monetary area) — capture as bloc with note if bank is absent.
            result["currency_bloc"] = Field(
                value=primary_zone,
                file=file_name,
                section="1",
                line=line_num,
                raw=raw_line,
            )
            parse_notes.append(
                {
                    "file": file_name,
                    "section": "1",
                    "line": line_num,
                    "kind": "currency_zone_no_bank",
                    "message": (
                        f"Monetary zone '{primary_zone}' has no '/ bank' separator; "
                        "stored as currency_bloc with currency_bank=None."
                    ),
                    "raw": raw_line,
                }
            )

    return result


def _parse_bloc_token(
    raw_token: str,
    file_name: str,
    line_num: int,
    raw_line: str,
) -> Field:
    """Parse one regional-bloc list item into a Field with canonical key and qualifier.

    Purpose:
        Keep qualifiers such as ``observer`` or alternate acronyms such as ``(UEMOA)``
        in ``Field.qualifier`` while storing the clean canonical bloc name in
        ``Field.canonical`` so intersection and symmetry checks work reliably.

    Inputs:
        raw_token: Trimmed single bloc entry from the semicolon-separated list.
        file_name: Dossier filename.
        line_num: 1-based line number.
        raw_line: Original raw markdown row.

    Outputs:
        ``Field`` with ``value``, ``canonical``, and optional ``qualifier``.

    Failure behaviour:
        Never raises.
    """
    qualifier: Optional[str] = None
    canonical = raw_token.strip()
    paren = re.match(r"^(.+?)\s*\(([^()]+)\)\s*$", canonical)
    if paren:
        canonical = paren.group(1).strip()
        qualifier = paren.group(2).strip()

    return Field(
        value=raw_token.strip(),
        file=file_name,
        section="1",
        line=line_num,
        raw=raw_line,
        canonical=canonical,
        qualifier=qualifier,
    )


def _extract_tax_meta(value: str) -> dict[str, Any]:
    """Extract all numeric rates and compound-cell metadata from a tax cell.

    Purpose:
        Preserve every number in compound cells (e.g. ``"30% (33% for some sectors)"``)
        so downstream comparisons and validators never silently discard secondary rates.

    Inputs:
        value: Raw tax cell text.

    Outputs:
        Dictionary with ``numbers`` (list of floats), ``is_compound`` (bool), and
        ``has_numeric`` (bool).

    Failure behaviour:
        Never raises; returns empty ``numbers`` for non-numeric cells.
    """
    nums = [float(m.group(0)) for m in NUMBER_RE.finditer(value)]
    # A simple single percentage looks like "30%" or "19.25%"; anything with multiple
    # numbers or extra qualifying text (parentheticals, ranges, slashes) is compound.
    is_simple = bool(re.fullmatch(r"\s*\d+(?:\.\d+)?\s*%\s*", value))
    is_compound = len(nums) > 1 or (len(nums) == 1 and not is_simple)
    return {
        "numbers": nums,
        "has_numeric": len(nums) > 0,
        "is_compound": is_compound,
    }


def _split_top_level(text: str, delimiters: tuple[str, ...] = (",", ";")) -> list[str]:
    """Split a delimited cell ONLY at parenthesis depth 0.

    Purpose:
        Prevent language cells with parenthetical lists or semicolon clauses from
        being torn apart mid-parenthesis (C4).

    Inputs:
        text: Raw table cell text.
        delimiters: Characters that separate list items when outside parentheses.

    Outputs:
        List of non-empty trimmed items.

    Failure behaviour:
        Handles unbalanced parentheses gracefully without raising.
    """
    parts: list[str] = []
    buf: list[str] = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
            buf.append(ch)
        elif ch == ")":
            depth = max(0, depth - 1)
            buf.append(ch)
        elif depth == 0 and ch in delimiters:
            item = "".join(buf).strip()
            if item:
                parts.append(item)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _parse_markdown_table_row(raw_line: str) -> Optional[list[str]]:
    """Split a markdown pipe-delimited table row into stripped cell strings.

    Purpose:
        Centralise markdown table row parsing and skip separator rows (``|---|---|``).

    Inputs:
        raw_line: Raw line from the markdown file.

    Outputs:
        List of stripped cell strings, or ``None`` if not a data row.

    Failure behaviour:
        Never raises.
    """
    stripped = raw_line.strip()
    if not (stripped.startswith("|") and stripped.endswith("|")):
        return None
    cells = [c.strip() for c in stripped.strip("|").split("|")]
    # Skip markdown horizontal rule separator lines such as |---|---|.
    if all(set(c) <= {"-", ":", " "} and "-" in c for c in cells if c):
        return None
    return cells


def parse_dossier(
    path: Path | str,
    template_spec: Optional[TemplateSpec] = None,
) -> dict[str, Any]:
    """Parse a single regulatory dossier markdown file into provenance-tagged Fields.

    Purpose:
        Convert one country dossier into a structured dictionary where every extracted
        value is a ``Field`` (or list/dict of ``Field`` objects) carrying exact file,
        section, line, and raw-line provenance.

    Inputs:
        path: Path to the dossier markdown file.
        template_spec: Optional ``TemplateSpec`` (loaded from ``_template.md`` if
            omitted).

    Outputs:
        Dictionary representing the parsed dossier, including ``parse_notes`` for any
        missing sections, missing fields, or template deviations.

    Failure behaviour:
        Never crashes on missing sections, empty files, or malformed rows; records
        structured entries in ``parse_notes`` instead.
    """
    file_path = Path(path)
    file_name = file_path.name
    slug = file_path.stem
    spec = template_spec if template_spec is not None else load_template_spec(file_path.parent)
    parse_notes: list[dict[str, Any]] = []

    parsed: dict[str, Any] = {
        "slug": slug,
        "file": file_name,
        "country": None,
        "author": None,
        "status": None,
        "updated": None,
        "citation_key": None,
        "capital": None,
        "currency": None,
        "currency_name": None,
        "currency_code": None,
        "currency_bloc": None,
        "currency_bank": None,
        "currency_zone_raw": None,
        "regional_blocs": [],
        "official_languages": [],
        "dominant_languages": [],
        "central_bank": None,
        "section2_prose": None,
        "data_protection": None,
        "data_protection_prose": None,
        "energy_regulator": None,
        "energy_prose": None,
        "sectors": {},
        "sector_steps": {},
        "cit": None,
        "vat": None,
        "investment_agency": None,
        "incentives": None,
        "tax_prose": None,
        "expansion_notes": [],
        "sections_present": [],
        "sentences": [],
        "raw_lines": [],
        "parse_notes": parse_notes,
    }

    try:
        raw_text = file_path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        parse_notes.append(
            {
                "file": file_name,
                "section": "0",
                "line": 0,
                "kind": "read_error",
                "message": f"Failed to read file: {exc}",
                "raw": "",
            }
        )
        return parsed

    lines = raw_text.splitlines()
    parsed["raw_lines"] = lines
    current_section = "0"

    for line_num, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()
        if not stripped:
            continue

        # Detect numbered section headings (## 1. ..., ## 2. ..., etc.).
        sec_match = re.match(r"^##\s+(\d+)\.\s*(.*)$", stripped)
        if sec_match:
            current_section = sec_match.group(1)
            if current_section not in parsed["sections_present"]:
                parsed["sections_present"].append(current_section)
            expected_title = spec.expected_sections.get(current_section)
            actual_title = sec_match.group(2).strip()
            if expected_title and actual_title.lower() != expected_title.lower():
                parse_notes.append(
                    {
                        "file": file_name,
                        "section": current_section,
                        "line": line_num,
                        "kind": "heading_deviation",
                        "message": (
                            f"Section {current_section} heading '{actual_title}' differs "
                            f"from template '{expected_title}'."
                        ),
                        "raw": raw_line,
                    }
                )
            continue

        # --- Section 0: Header, metadata, citation key ---
        if current_section == "0":
            if stripped.startswith("# ") and parsed["country"] is None:
                title_body = stripped[2:].strip()
                if spec.title_suffix and title_body.endswith(spec.title_suffix):
                    country_name = title_body[: -len(spec.title_suffix)].strip()
                elif "—" in title_body:
                    country_name = title_body.split("—", 1)[0].strip()
                    parse_notes.append(
                        {
                            "file": file_name,
                            "section": "0",
                            "line": line_num,
                            "kind": "title_deviation",
                            "message": "Title suffix deviated from _template.md; parsed before em-dash.",
                            "raw": raw_line,
                        }
                    )
                else:
                    country_name = title_body
                    parse_notes.append(
                        {
                            "file": file_name,
                            "section": "0",
                            "line": line_num,
                            "kind": "title_deviation",
                            "message": "Title format deviated from _template.md; kept full heading.",
                            "raw": raw_line,
                        }
                    )
                parsed["country"] = Field(
                    value=country_name,
                    file=file_name,
                    section="0",
                    line=line_num,
                    raw=raw_line,
                )
                continue

            if "**Author:**" in stripped or "**Updated:**" in stripped or "**Status:**" in stripped:
                # Split metadata parts on the template's middle-dot separator "·".
                segments = [seg.strip() for seg in stripped.split("·")]
                for seg in segments:
                    for label, key in (
                        ("**Author:**", "author"),
                        ("**Status:**", "status"),
                        ("**Updated:**", "updated"),
                    ):
                        if seg.startswith(label):
                            val = seg[len(label) :].strip()
                            parsed[key] = Field(
                                value=val,
                                file=file_name,
                                section="0",
                                line=line_num,
                                raw=raw_line,
                            )
                continue

            if stripped.startswith(">") and "citation key" in stripped.lower():
                parsed["citation_key"] = Field(
                    value=stripped.lstrip("> ").strip(),
                    file=file_name,
                    section="0",
                    line=line_num,
                    raw=raw_line,
                )
                continue

        # --- Section 1: Overview table ---
        elif current_section == "1":
            cells = _parse_markdown_table_row(raw_line)
            if cells and len(cells) >= 2:
                key_label = cells[0].strip().lower()
                val_text = cells[1].strip()
                if key_label == "field":
                    continue
                if key_label == "capital":
                    parsed["capital"] = Field(
                        value=val_text,
                        file=file_name,
                        section="1",
                        line=line_num,
                        raw=raw_line,
                    )
                elif key_label == "currency":
                    parsed["currency"] = Field(
                        value=val_text,
                        file=file_name,
                        section="1",
                        line=line_num,
                        raw=raw_line,
                    )
                    parsed.update(
                        _parse_currency_cell(val_text, file_name, line_num, raw_line, parse_notes)
                    )
                elif key_label == "regional blocs":
                    tokens = [t.strip() for t in val_text.split(";") if t.strip()]
                    parsed["regional_blocs"] = [
                        _parse_bloc_token(tok, file_name, line_num, raw_line) for tok in tokens
                    ]
                elif key_label == "official languages":
                    langs = _split_top_level(val_text, delimiters=(",", ";"))
                    parsed["official_languages"] = [
                        Field(
                            value=lang,
                            file=file_name,
                            section="1",
                            line=line_num,
                            raw=raw_line,
                        )
                        for lang in langs
                    ]
                elif key_label == "dominant spoken languages":
                    langs = _split_top_level(val_text, delimiters=(",", ";"))
                    parsed["dominant_languages"] = [
                        Field(
                            value=lang,
                            file=file_name,
                            section="1",
                            line=line_num,
                            raw=raw_line,
                        )
                        for lang in langs
                    ]
            continue

        # --- Section 2: Central bank & data protection ---
        elif current_section == "2":
            if stripped.lower().startswith("**central bank:**") or stripped.lower().startswith("central bank:"):
                cb_val, cb_prose = _extract_slot_by_affix(
                    stripped,
                    slot_key="central_bank",
                    bold_label="**Central bank:**",
                    spec=spec,
                    file_name=file_name,
                    section="2",
                    line_num=line_num,
                    parse_notes=parse_notes,
                )
                parsed["central_bank"] = Field(
                    value=cb_val,
                    file=file_name,
                    section="2",
                    line=line_num,
                    raw=raw_line,
                )
                if cb_prose:
                    parsed["section2_prose"] = Field(
                        value=cb_prose,
                        file=file_name,
                        section="2",
                        line=line_num,
                        raw=raw_line,
                    )
                    _record_sentences(parsed["sentences"], cb_prose, file_name, "2", line_num, raw_line)
            elif stripped.lower().startswith("**data protection:**") or stripped.lower().startswith("data protection:"):
                dp_val, dp_prose = _extract_slot_by_affix(
                    stripped,
                    slot_key="data_protection",
                    bold_label="**Data protection:**",
                    spec=spec,
                    file_name=file_name,
                    section="2",
                    line_num=line_num,
                    parse_notes=parse_notes,
                )
                parsed["data_protection"] = Field(
                    value=dp_val,
                    file=file_name,
                    section="2",
                    line=line_num,
                    raw=raw_line,
                )
                if dp_prose:
                    parsed["data_protection_prose"] = Field(
                        value=dp_prose,
                        file=file_name,
                        section="2",
                        line=line_num,
                        raw=raw_line,
                    )
                    _record_sentences(parsed["sentences"], dp_prose, file_name, "2", line_num, raw_line)
            else:
                _record_sentences(parsed["sentences"], stripped, file_name, "2", line_num, raw_line)
            continue

        # --- Section 3: Energy sector ---
        elif current_section == "3":
            if stripped.lower().startswith("**regulator / authority:**") or stripped.lower().startswith("regulator / authority:"):
                en_val, en_prose = _extract_slot_by_affix(
                    stripped,
                    slot_key="energy_regulator",
                    bold_label="**Regulator / authority:**",
                    spec=spec,
                    file_name=file_name,
                    section="3",
                    line_num=line_num,
                    parse_notes=parse_notes,
                )
                parsed["energy_regulator"] = Field(
                    value=en_val,
                    file=file_name,
                    section="3",
                    line=line_num,
                    raw=raw_line,
                )
                if en_prose:
                    parsed["energy_prose"] = Field(
                        value=en_prose,
                        file=file_name,
                        section="3",
                        line=line_num,
                        raw=raw_line,
                    )
                    _record_sentences(parsed["sentences"], en_prose, file_name, "3", line_num, raw_line)
            else:
                _record_sentences(parsed["sentences"], stripped, file_name, "3", line_num, raw_line)
            continue

        # --- Section 4: Sector compliance steps table ---
        elif current_section == "4":
            cells = _parse_markdown_table_row(raw_line)
            if cells and len(cells) >= 2:
                sector_raw = cells[0].replace("**", "").strip()
                if sector_raw.lower() == "sector":
                    continue
                sector_key = sector_raw.lower()
                steps_text = cells[1].strip()
                parsed["sectors"][sector_key] = Field(
                    value=steps_text,
                    file=file_name,
                    section="4",
                    line=line_num,
                    raw=raw_line,
                    canonical=sector_raw,
                )
                step_parts = [s.strip().rstrip(".") for s in steps_text.split(";") if s.strip()]
                parsed["sector_steps"][sector_key] = [
                    Field(
                        value=part,
                        file=file_name,
                        section="4",
                        line=line_num,
                        raw=raw_line,
                        canonical=sector_raw,
                    )
                    for part in step_parts
                ]
            else:
                _record_sentences(parsed["sentences"], stripped, file_name, "4", line_num, raw_line)
            continue

        # --- Section 5: Tax planning ---
        elif current_section == "5":
            cells = _parse_markdown_table_row(raw_line)
            if cells and len(cells) >= 2:
                item_label = cells[0].strip().lower()
                val_text = cells[1].strip()
                if item_label == "item":
                    continue
                if "corporate income tax" in item_label:
                    parsed["cit"] = Field(
                        value=val_text,
                        file=file_name,
                        section="5",
                        line=line_num,
                        raw=raw_line,
                        meta=_extract_tax_meta(val_text),
                    )
                elif "vat" in item_label or "sales tax" in item_label:
                    parsed["vat"] = Field(
                        value=val_text,
                        file=file_name,
                        section="5",
                        line=line_num,
                        raw=raw_line,
                        meta=_extract_tax_meta(val_text),
                    )
                continue

            # Inline bold anchors on line 47: **Investment promotion agency:** ... **Incentives:** ...
            if "**investment promotion agency:**" in stripped.lower():
                ipa_label = "**Investment promotion agency:**"
                inc_label = "**Incentives:**"
                lower_s = stripped.lower()
                ipa_start = lower_s.find(ipa_label.lower()) + len(ipa_label)
                inc_idx = lower_s.find(inc_label.lower())
                if inc_idx != -1:
                    ipa_val = stripped[ipa_start:inc_idx].strip().rstrip(".")
                    inc_val = stripped[inc_idx + len(inc_label) :].strip().rstrip(".")
                    parsed["investment_agency"] = Field(
                        value=ipa_val,
                        file=file_name,
                        section="5",
                        line=line_num,
                        raw=raw_line,
                    )
                    parsed["incentives"] = Field(
                        value=inc_val,
                        file=file_name,
                        section="5",
                        line=line_num,
                        raw=raw_line,
                    )
                else:
                    ipa_val = stripped[ipa_start:].strip().rstrip(".")
                    parsed["investment_agency"] = Field(
                        value=ipa_val,
                        file=file_name,
                        section="5",
                        line=line_num,
                        raw=raw_line,
                    )
                    parse_notes.append(
                        {
                            "file": file_name,
                            "section": "5",
                            "line": line_num,
                            "kind": "missing_inline_label",
                            "message": "Found Investment promotion agency without inline Incentives label.",
                            "raw": raw_line,
                        }
                    )
                continue

            if stripped.lower().startswith("**incentives:**"):
                inc_val = stripped[len("**Incentives:**") :].strip().rstrip(".")
                parsed["incentives"] = Field(
                    value=inc_val,
                    file=file_name,
                    section="5",
                    line=line_num,
                    raw=raw_line,
                )
                continue

            # Capture Section 5 narrative paragraph(s).
            if parsed["tax_prose"] is None:
                parsed["tax_prose"] = Field(
                    value=stripped,
                    file=file_name,
                    section="5",
                    line=line_num,
                    raw=raw_line,
                )
            _record_sentences(parsed["sentences"], stripped, file_name, "5", line_num, raw_line)
            continue

        # --- Section 6: Expansion notes ---
        elif current_section == "6":
            if stripped.startswith("- ") or stripped.startswith("* "):
                bullet = stripped[2:].strip()
                parsed["expansion_notes"].append(
                    Field(
                        value=bullet,
                        file=file_name,
                        section="6",
                        line=line_num,
                        raw=raw_line,
                    )
                )
                _record_sentences(parsed["sentences"], bullet, file_name, "6", line_num, raw_line)
            else:
                _record_sentences(parsed["sentences"], stripped, file_name, "6", line_num, raw_line)

    # Record missing expected sections and required fields as parse notes (R4).
    for sec_num in spec.expected_sections:
        if sec_num not in parsed["sections_present"]:
            parse_notes.append(
                {
                    "file": file_name,
                    "section": sec_num,
                    "line": 0,
                    "kind": "missing_section",
                    "message": f"Expected section {sec_num} ({spec.expected_sections[sec_num]}) is missing.",
                    "raw": "",
                }
            )

    required_scalar_fields = [
        ("country", "0"),
        ("updated", "0"),
        ("capital", "1"),
        ("currency", "1"),
        ("currency_code", "1"),
        ("central_bank", "2"),
        ("data_protection", "2"),
        ("energy_regulator", "3"),
        ("cit", "5"),
        ("vat", "5"),
        ("investment_agency", "5"),
    ]
    for key, sec_num in required_scalar_fields:
        if parsed[key] is None or not str(parsed[key].value).strip():
            parse_notes.append(
                {
                    "file": file_name,
                    "section": sec_num,
                    "line": 0,
                    "kind": "missing_field",
                    "message": f"Required field '{key}' is missing or empty.",
                    "raw": "",
                }
            )

    required_list_fields = [
        ("regional_blocs", "1"),
        ("official_languages", "1"),
        ("dominant_languages", "1"),
        ("expansion_notes", "6"),
    ]
    for key, sec_num in required_list_fields:
        if not parsed[key]:
            parse_notes.append(
                {
                    "file": file_name,
                    "section": sec_num,
                    "line": 0,
                    "kind": "missing_field",
                    "message": f"Required list field '{key}' is empty.",
                    "raw": "",
                }
            )

    if len(parsed["sectors"]) < 6:
        parse_notes.append(
            {
                "file": file_name,
                "section": "4",
                "line": 0,
                "kind": "missing_sector_rows",
                "message": f"Expected 6 sector compliance rows, found {len(parsed['sectors'])}.",
                "raw": "",
            }
        )

    return parsed


def _record_sentences(
    bucket: list[Field],
    text: str,
    file_name: str,
    section: str,
    line_num: int,
    raw_line: str,
) -> None:
    """Split prose text into individual provenance-tagged sentence Fields.

    Purpose:
        Enable corpus-wide boilerplate detection (V17) by indexing each prose
        sentence with its exact dossier location.

    Inputs:
        bucket: Mutable list of ``Field`` objects on the dossier.
        text: Prose string to segment into sentences.
        file_name: Source filename.
        section: Section number string.
        line_num: 1-based line number.
        raw_line: Original line text.

    Outputs:
        Appends sentence ``Field`` objects in place.

    Failure behaviour:
        Never raises.
    """
    for sent in re.split(r"(?<=[.!?])\s+", text.strip()):
        cleaned = sent.strip()
        if cleaned:
            bucket.append(
                Field(
                    value=cleaned,
                    file=file_name,
                    section=section,
                    line=line_num,
                    raw=raw_line,
                )
            )


def mark_corpus_boilerplate(
    dossiers: dict[str, dict[str, Any]],
    threshold: int = 30,
) -> dict[str, int]:
    """Flag sentences and sector rows repeated verbatim across more than ``threshold`` files.

    Purpose:
        Keep templated boilerplate out of country comparisons (V17) by marking
        ``Field.is_boilerplate = True`` whenever identical text appears in more than
        30 distinct dossiers.

    Inputs:
        dossiers: Mapping of country slug to parsed dossier dict.
        threshold: Minimum exclusive dossier count to consider text generic (default 30).

    Outputs:
        Dictionary mapping boilerplate strings to the number of dossiers containing them.

    Failure behaviour:
        Never raises.
    """
    sentence_doc_counts: Counter[str] = Counter()
    sector_row_doc_counts: Counter[str] = Counter()

    for doc in dossiers.values():
        unique_sents = {f.value for f in doc.get("sentences", [])}
        for s in unique_sents:
            sentence_doc_counts[s] += 1
        for sec_field in doc.get("sectors", {}).values():
            sector_row_doc_counts[sec_field.value] += 1

    generic_sents = {s: c for s, c in sentence_doc_counts.items() if c > threshold}
    generic_rows = {r: c for r, c in sector_row_doc_counts.items() if c > threshold}

    for doc in dossiers.values():
        for f in doc.get("sentences", []):
            if f.value in generic_sents:
                f.is_boilerplate = True
        for sec_key, sec_field in doc.get("sectors", {}).items():
            if sec_field.value in generic_rows:
                sec_field.is_boilerplate = True
                for step_field in doc.get("sector_steps", {}).get(sec_key, []):
                    step_field.is_boilerplate = True

    combined = dict(generic_sents)
    combined.update(generic_rows)
    return combined


def parse_corpus(
    dossier_dir: Path | str | None = None,
    expect_count: Optional[int] = 54,
) -> tuple[dict[str, dict[str, Any]], TemplateSpec, dict[str, int]]:
    """Load and parse all country dossiers in ``dossier_dir`` against ``_template.md``.

    Purpose:
        Run the two-pass template-driven parser across the entire corpus: first learn
        shared boilerplate frames from ``_template.md`` and the corpus, then parse
        every file with full provenance and tag generic boilerplate sentences.

    Inputs:
        dossier_dir: Optional path to the dossier folder (defaults to
            ``africa-regulatory/``).
        expect_count: Expected dossier count assertion (default 54; ``None`` to skip).

    Outputs:
        Tuple ``(dossiers_by_slug, template_spec, boilerplate_counts)``.

    Failure behaviour:
        Raises ``FileNotFoundError`` or ``AssertionError`` only if the directory is
        missing or count assertion fails; individual file defects become parse notes.
    """
    files = discover_dossier_files(dossier_dir, expect_count=expect_count)
    spec = load_template_spec(dossier_dir)
    enrich_template_with_corpus_affixes(spec, files)

    dossiers: dict[str, dict[str, Any]] = {}
    for file_path in files:
        doc = parse_dossier(file_path, template_spec=spec)
        dossiers[doc["slug"]] = doc

    boilerplate_counts = mark_corpus_boilerplate(dossiers, threshold=30)
    return dossiers, spec, boilerplate_counts


def extract_acronym_and_expansion(text: str) -> Optional[tuple[str, str]]:
    """Extract an ``(acronym, expansion)`` pair from a regulator name string.

    Purpose:
        Identify acronym-expansion pairs written either as ``"ACRONYM (Expansion)"``
        or ``"Expansion (ACRONYM)"`` for corpus profiling and cross-dossier checks.

    Inputs:
        text: Authority name string.

    Outputs:
        Tuple ``(acronym, expansion)`` if matched, otherwise ``None``.

    Failure behaviour:
        Never raises.
    """
    cleaned = text.strip()
    m1 = LEADING_ACRONYM_RE.match(cleaned)
    if m1:
        return (m1.group(1).strip(), m1.group(2).strip())
    m2 = TRAILING_ACRONYM_RE.match(cleaned)
    if m2:
        return (m2.group(2).strip(), m2.group(1).strip())
    return None


def _mask_dossier_slots(text: str, doc: dict[str, Any], sector_key: str = "") -> str:
    """Replace country-specific slot values inside a Section 4 row with placeholders.

    Purpose:
        Test whether a Section 4 compliance row differs from the corpus pattern beyond
        simple slot substitution (corpus profile check ``l``). Orders VAT vs CIT
        according to sector context so countries where CIT == VAT (e.g. both 15% or
        both 20%) do not trigger false skeleton mismatches.

    Inputs:
        text: Raw Section 4 row text.
        doc: Parsed dossier dictionary providing slot values to mask.
        sector_key: Normalized sector row name for disambiguating equal CIT/VAT rates.

    Outputs:
        Skeleton string with known slot values replaced by symbolic tokens.

    Failure behaviour:
        Never raises.
    """
    masked = text
    # Disambiguate equal numeric CIT/VAT strings by placing the sector's leaked tax first.
    if sector_key == "fintech":
        slot_order = (
            ("data_protection", "<DPA>"),
            ("vat", "<VAT>"),
            ("cit", "<CIT>"),
            ("central_bank", "<CB>"),
            ("energy_regulator", "<ENERGY_REG>"),
            ("country", "<COUNTRY>"),
        )
    else:
        slot_order = (
            ("data_protection", "<DPA>"),
            ("cit", "<CIT>"),
            ("vat", "<VAT>"),
            ("central_bank", "<CB>"),
            ("energy_regulator", "<ENERGY_REG>"),
            ("country", "<COUNTRY>"),
        )

    replacements: list[tuple[str, str]] = []
    for key, token in slot_order:
        fld = doc.get(key)
        if fld is not None and fld.value:
            replacements.append((fld.value, token))

    # Stable sort by descending length preserves sector-specific CIT/VAT priority on ties.
    for val, token in sorted(replacements, key=lambda pair: len(pair[0]), reverse=True):
        if val in masked:
            masked = masked.replace(val, token)
    return masked


def build_corpus_profile(dossiers: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Compute the full Phase 1 corpus profile (sections ``a`` through ``l``).

    Purpose:
        Aggregate structural health, currencies, blocs, central banks, data-protection
        acronyms, tax anomalies, language mismatches, update dates, placeholders,
        systemic defects, and Section 4 deviations across all parsed dossiers.

    Inputs:
        dossiers: Mapping of country slug to parsed dossier dict.

    Outputs:
        JSON-serialisable dictionary containing items ``a`` through ``l``.

    Failure behaviour:
        Never raises on missing or partial fields; treats missing fields defensively.
    """
    sorted_slugs = sorted(dossiers.keys())

    # (a) Files with any missing or unparseable field / parse note.
    a_missing: list[dict[str, Any]] = []
    for slug in sorted_slugs:
        doc = dossiers[slug]
        if doc["parse_notes"]:
            a_missing.append(
                {
                    "file": doc["file"],
                    "country": doc["country"].value if doc["country"] else slug,
                    "note_count": len(doc["parse_notes"]),
                    "notes": doc["parse_notes"],
                }
            )

    # (b) Distinct currency codes -> countries.
    b_currencies: dict[str, list[str]] = defaultdict(list)
    # (c) Distinct (currency_code, bloc, bank) combinations -> countries.
    c_combos_map: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    # (d) Distinct bloc tokens (raw and canonical).
    d_raw_blocs: dict[str, list[str]] = defaultdict(list)
    d_canonical_blocs: dict[str, list[str]] = defaultdict(list)

    # (e) Distinct central bank strings.
    e_central_banks: dict[str, list[str]] = defaultdict(list)

    # (f) Distinct data-protection acronyms with expansions and countries.
    f_acronyms: dict[str, dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    f_no_acronym: list[dict[str, Any]] = []

    # (g) CIT and VAT per country + anomalies.
    g_per_country: dict[str, dict[str, Any]] = {}
    g_anomalies: dict[str, list[dict[str, Any]]] = {
        "non_numeric": [],
        "compound": [],
        "zero": [],
        "above_40": [],
    }

    # (h) Official vs dominant languages + francophone bloc anomalies.
    h_per_country: dict[str, dict[str, Any]] = {}
    h_no_french_in_francophone_bloc: list[dict[str, Any]] = []
    h_english_in_francophone_bloc: list[dict[str, Any]] = []

    # (i) Updated dates.
    i_dates: dict[str, list[str]] = defaultdict(list)

    # (j) Placeholders by section.
    j_placeholders: dict[str, list[dict[str, Any]]] = defaultdict(list)

    # (k) Systemic defect counts across the corpus.
    k_defects: dict[str, list[dict[str, Any]]] = {
        "dpa_as_payments_licensor": [],
        "vat_in_fee_slot": [],
        "cit_in_energy_regulator_slot": [],
        "waemu_ecowas_eac_text_in_non_waemu": [],
        "waemu_ecowas_eac_text_in_none_of_the_three": [],
    }

    # (l) Section 4 skeleton tracker per sector.
    sector_skeletons: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )

    for slug in sorted_slugs:
        doc = dossiers[slug]
        cname = doc["country"].value if doc["country"] else slug
        fname = doc["file"]

        # b & c
        ccode = doc["currency_code"].value if doc["currency_code"] else "<MISSING>"
        cbloc = doc["currency_bloc"].value if doc["currency_bloc"] else "<NONE>"
        cbank = doc["currency_bank"].value if doc["currency_bank"] else "<NONE>"
        b_currencies[ccode].append(cname)
        c_combos_map[(ccode, cbloc, cbank)].append(cname)

        # d
        canonical_bloc_set: set[str] = set()
        for bf in doc["regional_blocs"]:
            d_raw_blocs[bf.value].append(cname)
            canon = bf.canonical or bf.value
            d_canonical_blocs[canon].append(cname)
            canonical_bloc_set.add(canon.upper())

        # e
        cb_str = doc["central_bank"].value if doc["central_bank"] else "<MISSING>"
        e_central_banks[cb_str].append(cname)

        # f
        dp_field = doc["data_protection"]
        if dp_field and dp_field.value:
            pair = extract_acronym_and_expansion(dp_field.value)
            if pair is not None:
                acr, exp = pair
                f_acronyms[acr][exp].append(cname)
            else:
                f_no_acronym.append(
                    {"file": fname, "country": cname, "line": dp_field.line, "value": dp_field.value}
                )

        # g
        cit_f = doc["cit"]
        vat_f = doc["vat"]
        g_per_country[cname] = {
            "file": fname,
            "cit": cit_f.value if cit_f else None,
            "cit_numbers": cit_f.meta.get("numbers", []) if cit_f else [],
            "vat": vat_f.value if vat_f else None,
            "vat_numbers": vat_f.meta.get("numbers", []) if vat_f else [],
        }
        for tax_kind, tf in (("CIT", cit_f), ("VAT", vat_f)):
            if tf is None:
                g_anomalies["non_numeric"].append(
                    {"file": fname, "country": cname, "tax": tax_kind, "line": 0, "value": None}
                )
                continue
            nums = tf.meta.get("numbers", [])
            entry = {
                "file": fname,
                "country": cname,
                "tax": tax_kind,
                "line": tf.line,
                "value": tf.value,
                "numbers": nums,
            }
            if not nums:
                g_anomalies["non_numeric"].append(entry)
            if tf.meta.get("is_compound"):
                g_anomalies["compound"].append(entry)
            if any(n == 0 for n in nums):
                g_anomalies["zero"].append(entry)
            if any(n > 40 for n in nums):
                g_anomalies["above_40"].append(entry)

        # h
        off_langs = [f.value for f in doc["official_languages"]]
        dom_langs = [f.value for f in doc["dominant_languages"]]
        h_per_country[cname] = {
            "file": fname,
            "official": off_langs,
            "dominant": dom_langs,
            "blocs": sorted(canonical_bloc_set),
        }
        in_franco_bloc = bool(canonical_bloc_set & FRANCOPHONE_BLOCS)
        if in_franco_bloc:
            off_lower = {l.lower() for l in off_langs}
            if not any("french" in l for l in off_lower):
                h_no_french_in_francophone_bloc.append(
                    {
                        "file": fname,
                        "country": cname,
                        "blocs": sorted(canonical_bloc_set & FRANCOPHONE_BLOCS),
                        "official": off_langs,
                        "dominant": dom_langs,
                    }
                )
            if any("english" in l for l in off_lower):
                h_english_in_francophone_bloc.append(
                    {
                        "file": fname,
                        "country": cname,
                        "blocs": sorted(canonical_bloc_set & FRANCOPHONE_BLOCS),
                        "official": off_langs,
                        "dominant": dom_langs,
                    }
                )

        # i
        upd = doc["updated"].value if doc["updated"] else "<MISSING>"
        i_dates[upd].append(fname)

        # j — inspect all extracted value fields for placeholder tokens by section.
        fields_to_scan: list[tuple[str, Field]] = []
        for scalar_key in (
            "capital",
            "currency",
            "central_bank",
            "data_protection",
            "energy_regulator",
            "cit",
            "vat",
            "investment_agency",
            "incentives",
        ):
            sf = doc.get(scalar_key)
            if sf is not None:
                fields_to_scan.append((scalar_key, sf))
        for sec_key, sec_f in doc.get("sectors", {}).items():
            fields_to_scan.append((f"sector:{sec_key}", sec_f))

        for field_name, fld in fields_to_scan:
            matches = PLACEHOLDER_RE.findall(fld.value)
            if matches:
                j_placeholders[fld.section].append(
                    {
                        "file": fname,
                        "country": cname,
                        "field": field_name,
                        "line": fld.line,
                        "tokens": sorted({m.lower() for m in matches}),
                        "value": fld.value,
                    }
                )

        # k — systemic defects
        fintech_f = doc["sectors"].get("fintech")
        if fintech_f is not None:
            if dp_field and dp_field.value and dp_field.value in fintech_f.value:
                if "licensing for payments and lending" in fintech_f.value.lower():
                    k_defects["dpa_as_payments_licensor"].append(
                        {"file": fname, "country": cname, "line": fintech_f.line}
                    )
            if vat_f and vat_f.value:
                if f"data protection registration ({vat_f.value})" in fintech_f.value.lower() or (
                    f"({vat_f.value})" in fintech_f.value
                    and "data protection registration" in fintech_f.value.lower()
                ):
                    k_defects["vat_in_fee_slot"].append(
                        {"file": fname, "country": cname, "line": fintech_f.line, "vat": vat_f.value}
                    )

        energy_f = doc["sectors"].get("energy & manufacturing")
        if energy_f is not None and cit_f and cit_f.value:
            if f"energy regulator: {cit_f.value.lower()}" in energy_f.value.lower():
                k_defects["cit_in_energy_regulator_slot"].append(
                    {"file": fname, "country": cname, "line": energy_f.line, "cit": cit_f.value}
                )

        s2_prose = doc.get("section2_prose")
        if s2_prose and "waemu/ecowas/eac" in s2_prose.value.lower():
            if "WAEMU" not in canonical_bloc_set:
                k_defects["waemu_ecowas_eac_text_in_non_waemu"].append(
                    {
                        "file": fname,
                        "country": cname,
                        "line": s2_prose.line,
                        "blocs": sorted(canonical_bloc_set),
                    }
                )
            if not (canonical_bloc_set & {"WAEMU", "ECOWAS", "EAC"}):
                k_defects["waemu_ecowas_eac_text_in_none_of_the_three"].append(
                    {
                        "file": fname,
                        "country": cname,
                        "line": s2_prose.line,
                        "blocs": sorted(canonical_bloc_set),
                    }
                )

        # l — Section 4 skeleton comparison across all 6 sectors.
        for sec_key, sec_f in doc["sectors"].items():
            skeleton = _mask_dossier_slots(sec_f.value, doc, sector_key=sec_key)
            sector_skeletons[sec_key][skeleton].append(
                {
                    "file": fname,
                    "country": cname,
                    "line": sec_f.line,
                    "value": sec_f.value,
                }
            )

    # Finalize (c) combo table with singleton flag.
    c_combos = []
    for (ccode, cbloc, cbank), countries in sorted(c_combos_map.items()):
        c_combos.append(
            {
                "currency_code": ccode,
                "bloc": None if cbloc == "<NONE>" else cbloc,
                "bank": None if cbank == "<NONE>" else cbank,
                "count": len(countries),
                "singleton": len(countries) == 1,
                "countries": sorted(countries),
            }
        )

    # Finalize (f) acronym table + shared acronyms (2+ countries).
    f_formatted: dict[str, Any] = {}
    f_shared: dict[str, Any] = {}
    for acr, exp_map in sorted(f_acronyms.items()):
        total = sum(len(c) for c in exp_map.values())
        entry = {
            "total_countries": total,
            "expansions": {exp: sorted(ctries) for exp, ctries in sorted(exp_map.items())},
        }
        f_formatted[acr] = entry
        if total >= 2:
            f_shared[acr] = entry

    # Finalize (i) modal Updated date and differing files.
    modal_date = max(i_dates.items(), key=lambda kv: len(kv[1]))[0] if i_dates else None
    i_diff = {d: sorted(fs) for d, fs in i_dates.items() if d != modal_date}

    # Finalize (l) Section 4 non-modal deviations.
    l_deviations: list[dict[str, Any]] = []
    l_modal_patterns: dict[str, dict[str, Any]] = {}
    for sec_key, skel_map in sorted(sector_skeletons.items()):
        modal_skel, modal_items = max(skel_map.items(), key=lambda kv: len(kv[1]))
        l_modal_patterns[sec_key] = {
            "modal_skeleton": modal_skel,
            "count": len(modal_items),
        }
        for skel, items in skel_map.items():
            if skel != modal_skel:
                for item in items:
                    l_deviations.append(
                        {
                            "sector": sec_key,
                            "file": item["file"],
                            "country": item["country"],
                            "line": item["line"],
                            "skeleton": skel,
                            "modal_skeleton": modal_skel,
                            "value": item["value"],
                        }
                    )

    return {
        "dossier_count": len(dossiers),
        "a_missing_or_unparseable": a_missing,
        "b_currency_codes": {k: sorted(v) for k, v in sorted(b_currencies.items())},
        "c_currency_bloc_bank_combos": c_combos,
        "d_bloc_tokens": {
            "raw": {
                k: {"count": len(v), "countries": sorted(v)}
                for k, v in sorted(d_raw_blocs.items(), key=lambda kv: (-len(kv[1]), kv[0]))
            },
            "canonical": {
                k: {"count": len(v), "countries": sorted(v)}
                for k, v in sorted(d_canonical_blocs.items(), key=lambda kv: (-len(kv[1]), kv[0]))
            },
        },
        "e_central_banks": {
            k: {"count": len(v), "countries": sorted(v)}
            for k, v in sorted(e_central_banks.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        },
        "f_data_protection_acronyms": {
            "all": f_formatted,
            "shared_by_2_plus": f_shared,
            "without_acronym": f_no_acronym,
        },
        "g_taxes": {
            "per_country": g_per_country,
            "anomalies": g_anomalies,
        },
        "h_languages": {
            "per_country": h_per_country,
            "no_french_in_francophone_bloc": h_no_french_in_francophone_bloc,
            "english_in_francophone_bloc": h_english_in_francophone_bloc,
        },
        "i_updated_dates": {
            "distinct_counts": {k: len(v) for k, v in sorted(i_dates.items())},
            "modal_date": modal_date,
            "differing_files": i_diff,
        },
        "j_placeholders_by_section": {
            sec: {"count": len(items), "items": items}
            for sec, items in sorted(j_placeholders.items())
        },
        "k_systemic_defects": {
            key: {"count": len(items), "out_of": len(dossiers), "items": items}
            for key, items in k_defects.items()
        },
        "l_section4_deviations": {
            "modal_patterns": l_modal_patterns,
            "deviations": l_deviations,
        },
    }


def save_corpus_profile(profile: dict[str, Any], out_path: Path | str | None = None) -> Path:
    """Write the corpus profile dictionary to ``data/corpus_profile.json``.

    Purpose:
        Persist the Phase 1 corpus profile inside ``Group 1/data/`` for inspection and
        downstream rule design.

    Inputs:
        profile: Profile dictionary returned by ``build_corpus_profile``.
        out_path: Optional output path (defaults to ``<Group 1>/data/corpus_profile.json``).

    Outputs:
        ``Path`` to the written JSON file.

    Failure behaviour:
        Creates parent directories automatically; raises ``OSError`` only if the
        filesystem rejects the write.
    """
    target = (
        Path(out_path)
        if out_path is not None
        else Path(__file__).resolve().parent / "data" / "corpus_profile.json"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
    return target


def print_corpus_profile(profile: dict[str, Any]) -> None:
    """Print a readable stdout report covering corpus profile items ``a`` through ``l``.

    Purpose:
        Give engineers an immediate, auditable console summary of all 54 dossiers after
        running ``python parser.py``.

    Inputs:
        profile: Profile dictionary produced by ``build_corpus_profile``.

    Outputs:
        None (writes formatted summary tables to stdout).

    Failure behaviour:
        Never raises on valid profile dicts.
    """
    print(f"=== PASSERELLE CORPUS PROFILE ({profile['dossier_count']} dossiers loaded) ===\n")

    # a
    missing = profile["a_missing_or_unparseable"]
    print(f"[a] Files with missing/unparseable fields or parse notes: {len(missing)}")
    for row in missing:
        kinds = ", ".join(sorted({n["kind"] for n in row["notes"]}))
        print(f"  - {row['file']} ({row['note_count']} notes: {kinds})")
        for n in row["notes"]:
            print(f"      §{n['section']} L{n['line']}: [{n['kind']}] {n['message']}")

    # b
    print(f"\n[b] Distinct currency codes ({len(profile['b_currency_codes'])}):")
    for code, countries in profile["b_currency_codes"].items():
        print(f"  - {code} ({len(countries)}): {', '.join(countries)}")

    # c
    print(f"\n[c] Distinct (currency, bloc, bank) combinations ({len(profile['c_currency_bloc_bank_combos'])}):")
    for combo in profile["c_currency_bloc_bank_combos"]:
        flag = " [SINGLETON]" if combo["singleton"] else ""
        print(
            f"  - ({combo['currency_code']}, {combo['bloc']}, {combo['bank']}) "
            f"[{combo['count']}]{flag}: {', '.join(combo['countries'])}"
        )

    # d
    print("\n[d] Distinct bloc tokens:")
    print("  Raw:")
    for tok, info in profile["d_bloc_tokens"]["raw"].items():
        print(f"    - {tok}: {info['count']}")
    print("  Canonical:")
    for tok, info in profile["d_bloc_tokens"]["canonical"].items():
        print(f"    - {tok}: {info['count']}")

    # e
    print(f"\n[e] Distinct central bank strings ({len(profile['e_central_banks'])}):")
    for cb, info in profile["e_central_banks"].items():
        print(f"  - {cb} ({info['count']}): {', '.join(info['countries'])}")

    # f
    f_info = profile["f_data_protection_acronyms"]
    print(f"\n[f] Data-protection acronyms ({len(f_info['all'])} total; {len(f_info['shared_by_2_plus'])} shared by 2+):")
    print("  Shared by 2+ countries:")
    for acr, info in f_info["shared_by_2_plus"].items():
        print(f"    - {acr} ({info['total_countries']} countries):")
        for exp, ctries in info["expansions"].items():
            print(f"        * {exp}: {', '.join(ctries)}")
    print(f"  Without acronym ({len(f_info['without_acronym'])}):")
    for item in f_info["without_acronym"]:
        print(f"    - {item['file']} L{item['line']}: {item['value']}")

    # g
    g_anom = profile["g_taxes"]["anomalies"]
    print("\n[g] Tax anomalies (CIT & VAT):")
    for bucket in ("non_numeric", "compound", "zero", "above_40"):
        items = g_anom[bucket]
        print(f"  {bucket} ({len(items)}):")
        for item in items:
            print(f"    - {item['file']} §5 L{item['line']} {item['tax']}: {item['value']}")

    # h
    h_info = profile["h_languages"]
    print("\n[h] Language checks in francophone blocs:")
    print(f"  No French in francophone bloc ({len(h_info['no_french_in_francophone_bloc'])}):")
    for item in h_info["no_french_in_francophone_bloc"]:
        print(f"    - {item['file']} ({', '.join(item['blocs'])}): official={item['official']}")
    print(f"  English in francophone bloc ({len(h_info['english_in_francophone_bloc'])}):")
    for item in h_info["english_in_francophone_bloc"]:
        print(f"    - {item['file']} ({', '.join(item['blocs'])}): official={item['official']}")

    # i
    i_info = profile["i_updated_dates"]
    print(f"\n[i] Updated dates: {i_info['distinct_counts']} (differing: {i_info['differing_files']})")

    # j
    print("\n[j] Placeholders ('verify', 'TBD', 'N/A') by section:")
    for sec, info in profile["j_placeholders_by_section"].items():
        print(f"  - §{sec}: {info['count']} occurrences")

    # k
    print("\n[k] Systemic defects across corpus:")
    for key, info in profile["k_systemic_defects"].items():
        print(f"  - {key}: {info['count']}/{info['out_of']}")

    # l
    l_devs = profile["l_section4_deviations"]["deviations"]
    print(f"\n[l] Section 4 non-slot deviations: {len(l_devs)}")
    for item in l_devs:
        print(f"  - {item['file']} §4 L{item['line']} [{item['sector']}]: {item['value']}")


def main() -> None:
    """Parse all 54 dossiers, save ``data/corpus_profile.json``, and print summary.

    Purpose:
        CLI entry point for Phase 1 verification and corpus profiling.

    Inputs:
        None (uses default ``africa-regulatory/`` path).

    Outputs:
        Writes ``data/corpus_profile.json`` and prints the profile report.

    Failure behaviour:
        Exits non-zero if the dossier directory is missing or count != 54.
    """
    dossiers, spec, boilerplate = parse_corpus(expect_count=54)
    profile = build_corpus_profile(dossiers)
    saved = save_corpus_profile(profile)
    print(f"Template loaded: {spec.template_path}")
    print(f"Learned corpus boilerplate frames: {sorted(spec.corpus_affixes.keys())}")
    print(f"Generic boilerplate texts (>30 dossiers): {len(boilerplate)}")
    print(f"Saved corpus profile to: {saved}\n")
    print_corpus_profile(profile)


if __name__ == "__main__":
    main()
