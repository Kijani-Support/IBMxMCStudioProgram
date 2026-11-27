"""Passerelle (EN: "Gateway") — Validation Registry & Broken-File Tests.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Verify the lean validation registry (V01–V03 collapsed with affected_count 54,
    V05 passing across all six CEMAC members, V12 catching a broken temp dossier
    without crashing, and RULE_ERROR isolation when a rule raises).

Inputs:
    Live 54-dossier corpus plus a temporary broken dossier copy created via pytest
    ``tmp_path``.

Outputs:
    Pytest pass/fail assertions.

Failure behaviour:
    Fails individual tests if any validation invariant breaks.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

GROUP1_DIR = Path(__file__).resolve().parents[1]
if str(GROUP1_DIR) not in sys.path:
    sys.path.insert(0, str(GROUP1_DIR))

from facts import build_facts
from parser import default_dossier_dir, parse_corpus
from render import render_brief
from validate import (
    build_bloc_consistency_matrix,
    run_validation_registry,
)


def test_v01_to_v03_collapse_to_one_flag_with_count_54() -> None:
    """Confirm V01, V02, and V03 each emit ONE collapsed flag with affected_count == 54.

    Purpose:
        Prevent template-wide defects from spamming 54 duplicate flags.

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Raises ``AssertionError`` if any of V01–V03 does not collapse to 1 flag of 54.
    """
    dossiers, _, _ = parse_corpus(expect_count=54)
    flags = run_validation_registry(dossiers, context={})

    for v_code in ("V01", "V02", "V03"):
        hits = [f for f in flags if f["v_number"] == v_code]
        assert len(hits) == 1, f"Expected 1 collapsed flag for {v_code}, got {len(hits)}"
        assert hits[0]["scope"] == "template"
        assert hits[0]["affected_count"] == 54
        assert len(hits[0]["countries"]) == 54


def test_v05_passes_for_all_six_cemac_members() -> None:
    """Confirm V05 raises zero currency-mismatch flags across all six CEMAC dossiers.

    Purpose:
        Verify CEMAC currency consistency and matrix generation across all 6 members.

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Raises ``AssertionError`` if CEMAC member count != 6 or any member fails V05.
    """
    dossiers, _, _ = parse_corpus(expect_count=54)
    matrix = build_bloc_consistency_matrix("CEMAC", dossiers)
    assert matrix["member_count"] == 6
    for row in matrix["rows"]:
        assert row["currency"]["status"] == "ok"
        assert row["currency"]["label"] == "XAF"


def test_broken_dossier_triggers_v12_without_crashing(tmp_path: Path) -> None:
    """Confirm deleting a section from a temp dossier triggers V12 and never crashes.

    Purpose:
        Validate hard rule R4 and validation rule V12 on a deliberately broken file.

    Inputs:
        tmp_path: Pytest temporary directory fixture.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Fails if parsing, validation, facts building, or rendering raises or omits V12.
    """
    src_dir = default_dossier_dir()
    shutil.copy(src_dir / "_template.md", tmp_path / "_template.md")
    shutil.copy(src_dir / "cameroon.md", tmp_path / "cameroon.md")

    # Delete Section 5 (Tax planning) from a temporary copy of gabon.md.
    raw = (src_dir / "gabon.md").read_text(encoding="utf-8")
    before_s5, _, after_s5 = raw.partition("## 5. Tax planning")
    _, _, s6_part = after_s5.partition("## 6. Expansion notes")
    broken_text = before_s5 + "## 6. Expansion notes" + s6_part
    (tmp_path / "gabon.md").write_text(broken_text, encoding="utf-8")

    facts = build_facts(
        "cameroon",
        "gabon",
        "fintech",
        dossier_dir=tmp_path,
        expect_count=None,
    )
    v12_flags = [f for f in facts["flags"] if f["v_number"] == "V12"]
    assert len(v12_flags) == 1
    assert v12_flags[0]["severity"] == "high"
    assert "gabon" in v12_flags[0]["countries"]

    # Both EN and FR briefs must still render cleanly without crashing.
    brief_en = render_brief(facts, lang="en")
    brief_fr = render_brief(facts, lang="fr")
    assert "V12" in brief_en
    assert "V12" in brief_fr


def test_rule_exception_is_isolated_as_rule_error() -> None:
    """Confirm a raising validation rule becomes RULE_ERROR and does not crash the run.

    Purpose:
        Verify Step 1 exception-isolation requirement in ``run_validation_registry``.

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Fails if the exception propagates or no ``RULE_ERROR`` flag is returned.
    """
    def _exploding_rule(dossiers: dict, context: dict) -> list:
        """Deliberately raise RuntimeError to verify registry isolation."""
        raise RuntimeError("synthetic failure")

    dossiers, _, _ = parse_corpus(expect_count=54)
    flags = run_validation_registry(dossiers, context={}, registry=[("V99", _exploding_rule)])
    assert len(flags) == 1
    assert flags[0]["v_number"] == "RULE_ERROR"
    assert flags[0]["rule_id"] == "RULE_ERROR"
