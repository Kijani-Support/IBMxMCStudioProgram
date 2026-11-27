"""Passerelle (EN: "Gateway") — Golden Route & Edge-Case Tests.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Validate the Cameroon -> Gabon fintech golden table, EN/FR structural & figure
    parity, non-numeric tax safety (Somalia), depth-0 prose language parsing (South
    Africa), and directional asymmetry when home and target are swapped.

Inputs:
    Live 54-dossier corpus in ``africa-regulatory/``.

Outputs:
    Pytest pass/fail assertions covering Phase 2 requirements.

Failure behaviour:
    Fails individual test cases with diagnostic assertions if any golden fact,
    provenance citation, or parity rule regresses.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Ensure Group 1 modules are importable regardless of pytest working directory.
GROUP1_DIR = Path(__file__).resolve().parents[1]
if str(GROUP1_DIR) not in sys.path:
    sys.path.insert(0, str(GROUP1_DIR))

from facts import build_facts
from parser import parse_corpus
from render import render_brief


def _shared_corpus() -> dict:
    """Parse all 54 dossiers once for reuse across tests.

    Purpose:
        Avoid repeating disk reads in every test case while asserting count == 54.

    Inputs:
        None.

    Outputs:
        Mapping of country slug to parsed dossier dict.

    Failure behaviour:
        Raises ``AssertionError`` if corpus count != 54.
    """
    dossiers, _, _ = parse_corpus(expect_count=54)
    return dossiers


def test_golden_cameroon_to_gabon_fintech() -> None:
    """Verify every row of the Phase 2 golden table for Cameroon -> Gabon fintech.

    Purpose:
        Assert currency, normalised BEAC central bank, CNPD acronym with differing
        expansions, compound uncomparable CIT (headline 30 both), VAT 19.25 vs 18
        (-1.25 pp delta), official languages (English drops out), shared AU+CEMAC,
        and Cameroon-only ``ECOWAS (observer)``.

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Raises ``AssertionError`` on any mismatch with the golden specification.
    """
    dossiers = _shared_corpus()
    facts = build_facts("cameroon", "gabon", "fintech", dossiers=dossiers)
    regs = facts["comparisons"]["regulators"]
    taxes = facts["comparisons"]["taxes"]
    langs = facts["comparisons"]["languages"]
    blocs = facts["blocs"]

    # Currency: XAF both
    assert regs["currency"]["home_code"] == "XAF"
    assert regs["currency"]["target_code"] == "XAF"
    assert regs["currency"]["same"] is True

    # Central bank: BEAC both after normalisation via data/aliases.json
    assert regs["central_bank"]["home_canonical"] == "BEAC"
    assert regs["central_bank"]["target_canonical"] == "BEAC"
    assert regs["central_bank"]["same"] is True

    # DPA: acronym CNPD both with different expansions
    assert regs["data_protection"]["home_acronym"] == "CNPD"
    assert regs["data_protection"]["target_acronym"] == "CNPD"
    assert regs["data_protection"]["same_acronym_different_expansion"] is True
    assert regs["data_protection"]["home_expansion"] != regs["data_protection"]["target_expansion"]

    # Sector regulator: C5 maps fintech -> central_bank (BEAC), flagging §4 DPA conflict
    assert regs["sector_regulator"]["home"]["expected_canonical"] == "BEAC"
    assert regs["sector_regulator"]["target"]["expected_canonical"] == "BEAC"
    assert regs["sector_regulator"]["any_section4_conflict"] is True

    # CIT: headline 30 both, Cameroon compound -> uncomparable-as-is, no delta subtracted
    cit = taxes["cit"]
    assert cit["home_headline"] == 30.0
    assert cit["target_headline"] == 30.0
    assert cit["home_compound"] is True
    assert cit["target_compound"] is False
    assert cit["home_all_numbers"] == [30.0, 33.0]
    assert cit["comparable"] is False
    assert cit["status"] == "uncomparable-as-is"
    assert cit["delta_pp"] is None

    # VAT: 19.25 vs 18, delta -1.25 percentage points
    vat = taxes["vat"]
    assert vat["home_headline"] == 19.25
    assert vat["target_headline"] == 18.0
    assert vat["comparable"] is True
    assert vat["delta_pp"] == -1.25

    # Official languages: English + French vs French; English drops out
    assert [f["value"] for f in langs["home_official"]] == ["English", "French"]
    assert [f["value"] for f in langs["target_official"]] == ["French"]
    assert langs["dropped_official"] == ["English"]
    assert langs["official_differs"] is True

    # Shared blocs: African Union + CEMAC; Cameroon-only qualifier "ECOWAS (observer)"
    assert blocs["shared_keys"] == ["African Union", "CEMAC"]
    only_home_raw = [e["raw_value"] for e in blocs["only_in_home"]]
    assert "ECOWAS (observer)" in only_home_raw
    ecowas_entry = next(e for e in blocs["only_in_home"] if e["canonical"] == "ECOWAS")
    assert ecowas_entry["qualifier"] == "observer"

    # C2: Data Confidence computed only from country & bloc flags, template banner separate
    assert len(facts["template_banner"]) >= 2
    assert facts["scores"]["template_flag_count"] == len(facts["template_banner"])
    assert facts["scores"]["label"] in ("High", "Medium", "Low")

    # C3 & F5: regional banking supervisor check lives strictly in our_checks, unverified
    assert any(
        "regional banking supervisor" in c["claim"].lower() and c["status"] == "unverified"
        for c in facts["our_checks"]
    )


def test_en_fr_parity_and_swap_asymmetry() -> None:
    """Verify EN/FR briefs share identical section count and figures, and swap changes brief.

    Purpose:
        Enforce rules A5 (home/target swap changes output) and A8 (EN/FR parity).

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Raises ``AssertionError`` if EN and FR diverge structurally or swap is symmetric.
    """
    dossiers = _shared_corpus()
    facts_fwd = build_facts("cameroon", "gabon", "fintech", dossiers=dossiers)
    facts_rev = build_facts("gabon", "cameroon", "fintech", dossiers=dossiers)

    brief_en = render_brief(facts_fwd, lang="en")
    brief_fr = render_brief(facts_fwd, lang="fr")
    brief_rev = render_brief(facts_rev, lang="en")

    en_h2 = [ln for ln in brief_en.splitlines() if ln.startswith("## ")]
    fr_h2 = [ln for ln in brief_fr.splitlines() if ln.startswith("## ")]
    assert len(en_h2) == len(fr_h2) == 8

    # Key numeric figures must match in both EN and FR briefs.
    for token in ("19.25%", "18%", "-1.25", "30%", "33%", "54"):
        assert token in brief_en
        assert token in brief_fr

    # Swapping home and target must change VAT delta sign (+1.25 vs -1.25) and brief text.
    assert facts_rev["comparisons"]["taxes"]["vat"]["delta_pp"] == 1.25
    assert brief_en != brief_rev


def test_non_numeric_tax_and_prose_language_cells() -> None:
    """Verify Somalia non-numeric tax safety and South Africa depth-0 language parsing (C4).

    Purpose:
        Confirm the parser and comparator never crash or invent numbers on non-numeric
        taxes or parenthetical prose language lists.

    Inputs:
        None.

    Outputs:
        None (pytest assertions).

    Failure behaviour:
        Raises ``AssertionError`` if non-numeric taxes subtract or parens split wrongly.
    """
    dossiers = _shared_corpus()

    # Non-numeric tax pair: Kenya -> Somalia
    f_som = build_facts("kenya", "somalia", "fintech", dossiers=dossiers)
    assert f_som["comparisons"]["taxes"]["cit"]["comparable"] is False
    assert f_som["comparisons"]["taxes"]["cit"]["delta_pp"] is None
    assert f_som["comparisons"]["taxes"]["vat"]["comparable"] is False
    assert f_som["comparisons"]["taxes"]["vat"]["delta_pp"] is None
    brief_som = render_brief(f_som, lang="en")
    assert "Uncomparable as-is" in brief_som

    # Prose language cell (C4): South Africa must stay intact at depth 0
    f_za = build_facts("south-africa", "namibia", "fintech", dossiers=dossiers)
    za_official = [f["value"] for f in f_za["comparisons"]["languages"]["home_official"]]
    assert za_official == [
        "11 official languages (English, Afrikaans, isiZulu, isiXhosa and others)"
    ]
    assert f_za["comparisons"]["languages"]["has_prose_cell"] is True
