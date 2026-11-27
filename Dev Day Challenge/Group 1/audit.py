"""Passerelle (EN: "Gateway") — Rules Self-Check Audit Suite.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Enforce every hard engineering rule (A1–A10) before committing or demoing:
    zero country literals in code, inline provenance on brief figures, crash-free
    execution across 5 pairs and all 6 sectors, 100% AST docstrings, swap asymmetry,
    required brief sections and non-lawyer takeaways, Group 1 import boundary,
    zero secrets, passing pytest suite, and single-file offline dashboard integrity.

Inputs:
    Group 1 Python source files, live 54-dossier corpus, generated ``facts.json``,
    and ``dashboard.html``.

Outputs:
    Prints a formatted PASS/FAIL audit table to stdout and exits with code ``0``
    if every check passes or ``1`` if any check fails.

Failure behaviour:
    Captures unexpected exceptions inside individual checks as ``FAIL`` rows so
    the full PASS/FAIL table is always displayed before returning non-zero.
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable

GROUP1_DIR = Path(__file__).resolve().parent
if str(GROUP1_DIR) not in sys.path:
    sys.path.insert(0, str(GROUP1_DIR))

from dashboard import write_dashboard
from facts import build_facts
from parser import parse_corpus
from render import render_brief

CORE_MODULES = (
    "parser.py",
    "blocs.py",
    "compare.py",
    "validate.py",
    "facts.py",
    "render.py",
    "dashboard.py",
    "cli.py",
)

SECRET_PATTERNS = (
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY"),
    re.compile(r"(?:WATSONX|IBM|OPENAI|API)[_-]?(?:KEY|TOKEN|SECRET)\s*=\s*['\"][^'\"]{8,}['\"]", re.I),
)


def _check_a1_no_country_literals(dossiers: dict) -> tuple[bool, str]:
    """A1: Verify zero country-name literals appear in core Python modules.

    Purpose:
        Guarantee Passerelle contains no hard-coded country logic (R1).

    Inputs:
        dossiers: Parsed 54-dossier corpus providing the full country-name list.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` listing any offending file and country hit.
    """
    names = sorted(
        {doc["country"].value for doc in dossiers.values() if doc.get("country") and doc["country"].value}
    )
    offenders: list[str] = []
    for mod in CORE_MODULES:
        src = (GROUP1_DIR / mod).read_text(encoding="utf-8")
        for cname in names:
            if re.search(r"\b" + re.escape(cname) + r"\b", src, re.IGNORECASE):
                offenders.append(f"{mod}:{cname}")
    if offenders:
        return False, f"Found country literals: {', '.join(offenders[:8])}"
    return True, f"0 country literals across {len(CORE_MODULES)} core modules"


def _check_a2_figure_provenance(brief_en: str) -> tuple[bool, str]:
    """A2: Verify every dossier figure line in the brief carries '(source:' inline.

    Purpose:
        Enforce line-level provenance on every percentage or delta figure (R2).

    Inputs:
        brief_en: Rendered English Markdown brief string.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` citing any line with a dossier percentage/delta
        missing ``(source:``.
    """
    missing: list[str] = []
    for idx, line in enumerate(brief_en.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # Check lines containing tax/fee percentages or percentage-point deltas.
        if re.search(r"\d+(?:\.\d+)?%|percentage points", stripped):
            if "(source:" not in stripped:
                missing.append(f"L{idx}: {stripped[:70]}")
    if missing:
        return False, f"Uncited figure lines: {'; '.join(missing[:5])}"
    return True, "Every percentage and delta line carries '(source:' inline"


def _check_a3_multi_route_and_all_sectors(dossiers: dict) -> tuple[bool, str]:
    """A3: Run cleanly on 5 diverse pairs and all 6 Sita sectors without crashing.

    Purpose:
        Confirm the pipeline generalises across the full 54-country corpus and all
        6 sectors (R1, R4).

    Inputs:
        dossiers: Pre-parsed 54-dossier corpus.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` on any raised exception.
    """
    slugs = sorted(dossiers.keys())
    # Select 5 deterministic spread pairs from the sorted corpus (no country literals!).
    indices = [(0, 1), (10, 20), (24, 45), (30, 46), (37, 42)]
    sectors = (
        "fintech",
        "healthtech",
        "edtech",
        "agritech",
        "retail & ecommerce",
        "energy & manufacturing",
    )
    runs = 0
    for i, j in indices:
        h, t = slugs[i], slugs[j]
        f = build_facts(h, t, "fintech", dossiers=dossiers)
        render_brief(f, lang="en")
        render_brief(f, lang="fr")
        runs += 1
    for sec in sectors:
        f = build_facts(slugs[7], slugs[19], sec, dossiers=dossiers)
        render_brief(f, lang="en")
        runs += 1
    return True, f"{runs} route/sector combinations rendered cleanly (5 pairs + 6 sectors)"


def _check_a4_docstrings() -> tuple[bool, str]:
    """A4: Verify every module, class, and function in Group 1 has a docstring.

    Purpose:
        Enforce documentation discipline (R5) using Python's ``ast`` module.

    Inputs:
        None.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` listing any module/class/function lacking a docstring.
    """
    py_files = sorted(GROUP1_DIR.glob("*.py")) + sorted((GROUP1_DIR / "tests").glob("*.py"))
    missing: list[str] = []
    for path in py_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        if not ast.get_docstring(tree):
            missing.append(f"{path.name}:<module>")
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing.append(f"{path.name}:{node.name}")
    if missing:
        return False, f"Missing docstrings: {', '.join(missing[:8])}"
    return True, f"100% docstring coverage across {len(py_files)} Python files"


def _check_a5_swap_asymmetry(dossiers: dict) -> tuple[bool, str]:
    """A5: Verify swapping --home and --target produces a different brief.

    Purpose:
        Confirm directional comparisons (such as VAT delta sign and dropped vs added
        languages) are genuinely asymmetric.

    Inputs:
        dossiers: Pre-parsed 54-dossier corpus.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` if forward and reversed briefs match.
    """
    slugs = sorted(dossiers.keys())
    h, t = slugs[7], slugs[19]
    b_fwd = render_brief(build_facts(h, t, "fintech", dossiers=dossiers), lang="en")
    b_rev = render_brief(build_facts(t, h, "fintech", dossiers=dossiers), lang="en")
    if b_fwd == b_rev:
        return False, "Swapping home and target produced identical briefs"
    return True, f"Swapping {h} <-> {t} changes brief content and deltas"


def _check_a6_brief_structure(brief_en: str, brief_fr: str) -> tuple[bool, str]:
    """A6: Verify required sections, 6 takeaways, template banner, disclaimer, and EN/FR parity.

    Purpose:
        Confirm the brief contains At-a-glance, Sections 1–6, one 'What this means
        for you' per section, template banner, Our checks, disclaimer, and matching
        EN/FR heading counts.

    Inputs:
        brief_en: Rendered English brief.
        brief_fr: Rendered French brief.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` naming the missing structural element.
    """
    en_h2 = [ln for ln in brief_en.splitlines() if ln.startswith("## ")]
    fr_h2 = [ln for ln in brief_fr.splitlines() if ln.startswith("## ")]
    takeaways_en = brief_en.count("**What this means for you:**")
    takeaways_fr = brief_fr.count("**Ce que cela signifie pour vous:**")
    checks = [
        (len(en_h2) == 8, f"EN h2 count={len(en_h2)}"),
        (len(fr_h2) == 8, f"FR h2 count={len(fr_h2)}"),
        (takeaways_en == 6, f"EN takeaways={takeaways_en}"),
        (takeaways_fr == 6, f"FR takeaways={takeaways_fr}"),
        ("Disclaimer" in brief_en, "missing disclaimer"),
        ("share this defect" in brief_en, "missing template banner"),
        ("## Our checks (unverified)" in brief_en, "missing Our checks section"),
    ]
    failed = [msg for ok, msg in checks if not ok]
    if failed:
        return False, "; ".join(failed)
    return True, "At-a-glance + 6 sections + 6 takeaways + banner + disclaimer + EN/FR parity"


def _check_a7_import_boundary() -> tuple[bool, str]:
    """A7: Verify no Group 1 Python file imports code from outside Group 1/.

    Purpose:
        Guarantee complete isolation from other challenge folders (Group 2–7, etc.).

    Inputs:
        None.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` listing any disallowed import.
    """
    local_mods = {p.stem for p in GROUP1_DIR.glob("*.py")}
    allowed = set(sys.stdlib_module_names) | local_mods | {"pytest"}
    py_files = sorted(GROUP1_DIR.glob("*.py")) + sorted((GROUP1_DIR / "tests").glob("*.py"))
    bad: list[str] = []
    for path in py_files:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    if top not in allowed:
                        bad.append(f"{path.name}:{top}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                if top not in allowed:
                    bad.append(f"{path.name}:{top}")
    if bad:
        return False, f"External/disallowed imports: {', '.join(bad)}"
    return True, "Only stdlib, pytest, and Group 1 local modules imported"


def _check_a8_no_secrets() -> tuple[bool, str]:
    """A8: Scan all Group 1 files for leaked secrets or API keys.

    Purpose:
        Enforce Hard Rule R6 (no credentials committed; fully offline execution).

    Inputs:
        None.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` naming any file matching a secret pattern.
    """
    hits: list[str] = []
    for path in sorted(GROUP1_DIR.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or ".pytest_cache" in path.parts:
            continue
        if path.suffix.lower() not in (".py", ".json", ".md", ".txt", ".html", ".env"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pat in SECRET_PATTERNS:
            if pat.search(text):
                hits.append(str(path.relative_to(GROUP1_DIR)))
                break
    if hits:
        return False, f"Possible secret pattern in: {', '.join(hits)}"
    return True, "No secrets or API keys detected; runs 100% offline"


def _check_a9_pytest() -> tuple[bool, str]:
    """A9: Execute the full Group 1 pytest suite and verify exit code 0.

    Purpose:
        Confirm every unit, golden, and broken-file regression test passes.

    Inputs:
        None.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` with pytest summary if any test fails.
    """
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", str(GROUP1_DIR / "tests"), "-q"],
        capture_output=True,
        text=True,
        check=False,
    )
    summary = (proc.stdout.strip().splitlines() or ["no output"])[-1]
    if proc.returncode != 0:
        return False, f"pytest failed (rc={proc.returncode}): {summary}"
    return True, summary


def _check_a10_offline_dashboard(facts: dict) -> tuple[bool, str]:
    """A10: Verify dashboard.html is a single offline file with zero external requests.

    Purpose:
        Ensure ``dashboard.html`` contains no ``http://``/``https://`` script/link/fetch
        calls and embeds ``facts.json`` directly.

    Inputs:
        facts: Current route ``facts`` dictionary.

    Outputs:
        Tuple ``(passed, detail_message)``.

    Failure behaviour:
        Returns ``(False, ...)`` if external asset URLs or missing embedded facts are found.
    """
    dash_path = write_dashboard(facts, GROUP1_DIR / "dashboard.html")
    html = dash_path.read_text(encoding="utf-8")
    ext_patterns = (
        r"<script[^>]+src=",
        r"<link[^>]+href=",
        r"fetch\s*\(",
        r"https?://",
    )
    for pat in ext_patterns:
        if re.search(pat, html, re.IGNORECASE):
            return False, f"dashboard.html matched disallowed external pattern: {pat}"
    if "const FACTS = " not in html or facts["meta"]["home_file"] not in html:
        return False, "dashboard.html does not embed route facts payload"
    return True, f"Single-file offline dashboard ({len(html):,} bytes, 0 external requests)"


def run_audit() -> int:
    """Execute all audit checks, print a PASS/FAIL table, and return exit code.

    Purpose:
        Provide the pre-commit quality gate required by Step 2.

    Inputs:
        None.

    Outputs:
        Integer exit code: ``0`` if every check passes, ``1`` otherwise.

    Failure behaviour:
        Catches unexpected errors per check and marks that check ``FAIL``.
    """
    dossiers, _, _ = parse_corpus(expect_count=54)
    slugs = sorted(dossiers.keys())
    # Default route check uses two corpus dossiers dynamically (no country literals).
    facts = build_facts(slugs[7], slugs[19], "fintech", dossiers=dossiers)
    brief_en = render_brief(facts, lang="en")
    brief_fr = render_brief(facts, lang="fr")

    checks: list[tuple[str, str, Callable[[], tuple[bool, str]]]] = [
        ("A1", "No country literals in core code", lambda: _check_a1_no_country_literals(dossiers)),
        ("A2", "Every brief figure cites (source:)", lambda: _check_a2_figure_provenance(brief_en)),
        ("A3", "Runs on 5 pairs + all 6 sectors", lambda: _check_a3_multi_route_and_all_sectors(dossiers)),
        ("A4", "100% AST docstring coverage", _check_a4_docstrings),
        ("A5", "Swapping home/target changes brief", lambda: _check_a5_swap_asymmetry(dossiers)),
        ("A6", "Brief sections, takeaways & EN/FR", lambda: _check_a6_brief_structure(brief_en, brief_fr)),
        ("A7", "No imports outside Group 1/", _check_a7_import_boundary),
        ("A8", "No secrets / API keys (offline)", _check_a8_no_secrets),
        ("A9", "Pytest regression suite passes", _check_a9_pytest),
        ("A10", "Offline single-file dashboard.html", lambda: _check_a10_offline_dashboard(facts)),
    ]

    print(f"{'Rule':<6} | {'Status':<6} | {'Check':<34} | Details")
    print("-" * 96)
    all_ok = True
    for code, title, fn in checks:
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 — keep audit table complete
            ok, detail = False, f"Exception: {type(exc).__name__}: {exc}"
        status = "PASS" if ok else "FAIL"
        if not ok:
            all_ok = False
        print(f"{code:<6} | {status:<6} | {title:<34} | {detail}")
    print("-" * 96)
    print("AUDIT RESULT:", "ALL CHECKS PASSED" if all_ok else "FAILED — DO NOT COMMIT")
    return 0 if all_ok else 1


def main() -> None:
    """CLI entry point exiting with ``run_audit()`` status code.

    Purpose:
        Allow CI or local pre-commit checks to gate on ``python audit.py``.

    Inputs:
        None.

    Outputs:
        Exits via ``sys.exit``.

    Failure behaviour:
        Exits with code ``1`` when any check fails.
    """
    sys.exit(run_audit())


if __name__ == "__main__":
    main()
