"""Passerelle (EN: "Gateway") — Command-Line Interface.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Provide the main CLI entry point for generating sourced cross-border launch briefs
    (Markdown EN/FR), writing ``facts.json``, and optionally invoking the dashboard or
    summary extensions added in later phases.

Inputs:
    Command-line arguments: ``--sector``, ``--home``, ``--target``, ``--lang``
    (``en`` | ``fr``), ``--out``, ``--facts-out``, ``--dossier-dir``, ``--dashboard``,
    and ``--summary``.

Outputs:
    Prints the rendered Markdown launch brief to stdout (and writes it to ``--out``
    if given) and persists ``facts.json`` when ``--facts-out`` is specified.

Failure behaviour:
    Prints actionable error messages to stderr and exits with code 2 on invalid
    arguments or unresolved country/sector names; never crashes on dossier defects.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

from facts import build_facts, save_facts
from render import render_brief
from validate import print_demo_shortlist


def build_arg_parser() -> argparse.ArgumentParser:
    """Create and configure the Passerelle CLI argument parser.

    Purpose:
        Define the stable command-line interface across all development phases.

    Inputs:
        None.

    Outputs:
        Configured ``argparse.ArgumentParser`` instance.

    Failure behaviour:
        Never raises.
    """
    ap = argparse.ArgumentParser(
        prog="passerelle",
        description=(
            "Passerelle — Cross-Border Launch Navigator. "
            "Turn country regulatory dossiers into sourced, plain-language launch briefs."
        ),
    )
    ap.add_argument("--sector", required=True, help="Target sector (e.g. fintech, healthtech, energy).")
    ap.add_argument("--home", required=True, help="Home country slug or name.")
    ap.add_argument("--target", required=True, help="Target country slug or name.")
    ap.add_argument("--lang", default="en", choices=("en", "fr"), help="Output language (en or fr).")
    ap.add_argument("--out", default=None, help="Optional file path to write the Markdown brief.")
    ap.add_argument("--facts-out", default=None, help="Optional file path to write facts.json.")
    ap.add_argument("--dossier-dir", default=None, help="Optional override directory for country dossiers.")
    ap.add_argument("--dashboard", action="store_true", help="Generate interactive dashboard.html (optional).")
    ap.add_argument("--summary", default=None, help="Optional grounded summary mode, e.g. granite.")
    ap.add_argument("--shortlist", action="store_true", help="Print the 6-flag DEMO SHORTLIST for the route.")
    return ap


def run_cli(argv: Optional[list[str]] = None) -> int:
    """Execute the Passerelle CLI workflow from argument list ``argv``.

    Purpose:
        Wire argument parsing, ``facts.build_facts``, ``render.render_brief``, and
        file output cleanly so both terminal users and pytest suites can invoke it.

    Inputs:
        argv: Optional list of CLI argument strings (defaults to ``sys.argv[1:]``).

    Outputs:
        Process exit code (``0`` on success, non-zero on invalid inputs).

    Failure behaviour:
        Catches ``ValueError`` and ``FileNotFoundError``, writing a clear message to
        stderr and returning exit code ``2``.
    """
    ap = build_arg_parser()
    args = ap.parse_args(argv)

    # Ensure UTF-8 stdout on Windows consoles so French accents and em-dashes render cleanly.
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except OSError:
            pass

    expect_count = 54 if args.dossier_dir is None else None
    try:
        facts = build_facts(
            home=args.home,
            target=args.target,
            sector=args.sector,
            dossier_dir=args.dossier_dir,
            expect_count=expect_count,
        )
        brief = render_brief(facts, lang=args.lang)
    except (ValueError, FileNotFoundError, AssertionError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.facts_out:
        save_facts(facts, args.facts_out)
    elif args.out:
        # Also save facts.json beside --out for reproducibility and audit verification.
        out_path = Path(args.out)
        save_facts(facts, out_path.with_name("facts.json"))

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(brief, encoding="utf-8")
    else:
        print(brief)

    if args.shortlist:
        print_demo_shortlist(facts.get("demo_shortlist", []))

    if args.dashboard:
        print(
            "Note: --dashboard will be enabled in Phase 4 (dashboard.py).",
            file=sys.stderr,
        )
    if args.summary:
        print(
            f"Note: --summary {args.summary} will be enabled in Phase 5 (summary.py).",
            file=sys.stderr,
        )

    return 0


def main() -> None:
    """Standard script entry point invoking ``run_cli``.

    Purpose:
        Exit with the integer status code returned by ``run_cli``.

    Inputs:
        None.

    Outputs:
        Exits process via ``sys.exit``.

    Failure behaviour:
        Propagates exit code from ``run_cli``.
    """
    sys.exit(run_cli())


if __name__ == "__main__":
    main()
