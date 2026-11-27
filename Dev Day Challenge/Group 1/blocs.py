"""Passerelle (EN: "Gateway") — Regional Bloc Normalisation & Intersection.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Canonicalise regional bloc memberships through ``data/aliases.json``, preserve
    membership qualifiers (such as ``observer``, ``dormant``, ``verify``) separately
    from canonical keys, intersect shared blocs between home and target dossiers,
    and attach plain-language startup meanings from ``data/blocs.json``.

Inputs:
    Parsed home and target dossier dictionaries produced by ``parser.py``, plus
    ``data/aliases.json`` and ``data/blocs.json``.

Outputs:
    Structured comparison dictionary containing ``shared``, ``only_in_home``,
    ``only_in_target``, and ``qualifiers_by_side``, with line-level provenance on
    every bloc item.

Failure behaviour:
    Never crashes on missing bloc lists or unknown bloc names; unknown blocs fall
    back to their raw canonical name with an explicit placeholder meaning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

from parser import Field

DATA_DIR = Path(__file__).resolve().parent / "data"


def load_json_data(filename: str, data_dir: Path | str | None = None) -> Any:
    """Load a JSON reference file from ``Group 1/data/``.

    Purpose:
        Centralise loading of data-driven tables (``aliases.json``, ``blocs.json``,
        etc.) without embedding country or bloc knowledge inside Python code.

    Inputs:
        filename: Name of the JSON file inside ``data/``.
        data_dir: Optional override directory for tests.

    Outputs:
        Decoded JSON object (dict or list).

    Failure behaviour:
        Raises ``FileNotFoundError`` if the requested data file does not exist.
    """
    base = Path(data_dir) if data_dir is not None else DATA_DIR
    return json.loads((base / filename).read_text(encoding="utf-8"))


def canonicalise_bloc_field(
    bloc_field: Field,
    aliases: dict[str, Any],
) -> dict[str, Any]:
    """Resolve a single parsed bloc ``Field`` into canonical key plus qualifier.

    Purpose:
        Map alternate bloc names (e.g. ``UEMOA`` -> ``WAEMU``, ``Arab Maghreb Union``
        -> ``AMU``) via ``data/aliases.json`` while keeping status qualifiers
        (``observer``, ``dormant``, ``verify``) in a separate ``qualifier`` key.

    Inputs:
        bloc_field: Provenance-tagged ``Field`` from Section 1 ``regional_blocs``.
        aliases: Loaded ``data/aliases.json`` dictionary.

    Outputs:
        Dictionary with ``canonical``, ``qualifier``, ``alternate_acronym``,
        ``raw_value``, and serialized ``field`` provenance.

    Failure behaviour:
        Never raises; falls back to ``bloc_field.canonical`` or ``bloc_field.value``
        when no alias mapping exists.
    """
    bloc_map = {k.lower(): v for k, v in aliases.get("blocs", {}).items()}
    qualifier_words = {w.lower() for w in aliases.get("qualifier_words", [])}

    base_name = (bloc_field.canonical or bloc_field.value).strip()
    canonical = bloc_map.get(base_name.lower(), base_name)

    raw_qual = bloc_field.qualifier.strip() if bloc_field.qualifier else None
    qualifier: Optional[str] = None
    alternate_acronym: Optional[str] = None

    if raw_qual:
        qual_lower = raw_qual.lower()
        # Distinguish genuine membership qualifiers ("observer", "dormant", "verify")
        # from alternate language acronyms like "(UEMOA)" that map to the same bloc.
        if qual_lower in qualifier_words:
            qualifier = raw_qual
        elif bloc_map.get(qual_lower) == canonical:
            alternate_acronym = raw_qual
        else:
            qualifier = raw_qual

    return {
        "canonical": canonical,
        "qualifier": qualifier,
        "alternate_acronym": alternate_acronym,
        "raw_value": bloc_field.value,
        "field": bloc_field.to_dict(),
        "citation": bloc_field.citation(),
    }


def extract_canonical_blocs(
    doc: dict[str, Any],
    aliases: Optional[dict[str, Any]] = None,
) -> list[dict[str, Any]]:
    """Canonicalise every regional bloc listed in a parsed dossier.

    Purpose:
        Provide a consistent list of canonicalised bloc entries with provenance for
        a single country dossier.

    Inputs:
        doc: Parsed dossier dictionary from ``parser.py``.
        aliases: Optional loaded ``aliases.json`` dict (loaded automatically if omitted).

    Outputs:
        List of canonicalised bloc dictionaries in dossier order.

    Failure behaviour:
        Returns an empty list if ``regional_blocs`` is missing or empty.
    """
    alias_data = aliases if aliases is not None else load_json_data("aliases.json")
    return [canonicalise_bloc_field(bf, alias_data) for bf in doc.get("regional_blocs", [])]


def compare_blocs(
    home_doc: dict[str, Any],
    target_doc: dict[str, Any],
    aliases: Optional[dict[str, Any]] = None,
    blocs_meta: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Intersect regional blocs between home and target dossiers and report qualifiers.

    Purpose:
        Determine shared blocs via set intersection of canonical bloc keys, attach
        plain-language startup meanings from ``data/blocs.json``, and highlight
        single-sided memberships and qualifiers (such as ``observer`` or ``dormant``).

    Inputs:
        home_doc: Parsed home country dossier dict.
        target_doc: Parsed target country dossier dict.
        aliases: Optional ``aliases.json`` dictionary.
        blocs_meta: Optional ``blocs.json`` dictionary.

    Outputs:
        Dictionary with ``shared``, ``only_in_home``, ``only_in_target``,
        ``home_all``, ``target_all``, and ``qualifiers_by_side``.

    Failure behaviour:
        Never raises; gracefully handles empty bloc lists or blocs absent from
        ``data/blocs.json``.
    """
    alias_data = aliases if aliases is not None else load_json_data("aliases.json")
    meta_data = blocs_meta if blocs_meta is not None else load_json_data("blocs.json")

    home_entries = extract_canonical_blocs(home_doc, alias_data)
    target_entries = extract_canonical_blocs(target_doc, alias_data)

    home_by_key = {e["canonical"]: e for e in home_entries}
    target_by_key = {e["canonical"]: e for e in target_entries}

    # Preserve home-dossier order for deterministic, readable presentation.
    shared_keys = [k for k in home_by_key if k in target_by_key]
    only_home_keys = [k for k in home_by_key if k not in target_by_key]
    only_target_keys = [k for k in target_by_key if k not in home_by_key]

    shared: list[dict[str, Any]] = []
    for key in shared_keys:
        info = meta_data.get(key, {})
        h_entry = home_by_key[key]
        t_entry = target_by_key[key]
        shared.append(
            {
                "canonical": key,
                "name_en": info.get("name_en", key),
                "name_fr": info.get("name_fr", key),
                "meaning_en": info.get(
                    "meaning_en",
                    "Regional grouping listed in both dossiers; confirm specific trade or licensing rules locally.",
                ),
                "meaning_fr": info.get(
                    "meaning_fr",
                    "Groupement régional cité dans les deux dossiers ; vérifiez les règles commerciales ou d'agrément applicables.",
                ),
                "monetary_union": bool(info.get("monetary_union", False)),
                "regional_supervisor": info.get("regional_supervisor"),
                "regional_supervisor_status": info.get("regional_supervisor_status", "unverified"),
                "home_entry": h_entry,
                "target_entry": t_entry,
                "home_qualifier": h_entry["qualifier"],
                "target_qualifier": t_entry["qualifier"],
            }
        )

    qualifiers_by_side = {
        "home": [e for e in home_entries if e["qualifier"]],
        "target": [e for e in target_entries if e["qualifier"]],
    }

    return {
        "shared": shared,
        "shared_keys": shared_keys,
        "only_in_home": [home_by_key[k] for k in only_home_keys],
        "only_in_target": [target_by_key[k] for k in only_target_keys],
        "home_all": home_entries,
        "target_all": target_entries,
        "qualifiers_by_side": qualifiers_by_side,
    }
