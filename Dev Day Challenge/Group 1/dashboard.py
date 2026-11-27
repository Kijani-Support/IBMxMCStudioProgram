"""Passerelle (EN: "Gateway") — Offline Single-File HTML Dashboard Generator.

Tagline: "Franchir la frontière, vérifier d'abord" / "Cross the border, verify first."
Team: Christopher Damian Munene, Mark Lekayia. Group 1, IBM x MC Studio Dev Day.

Purpose:
    Generate ONE self-contained, 100% offline ``dashboard.html`` directly from
    ``facts.json`` with embedded vanilla JavaScript, accessible styling, print-ready
    PDF layout, click-any-figure Evidence Drawer, Verify-first severity/rule filters,
    tickable Section 4 checklist, shared-bloc consistency matrix, and offline Markdown
    export.

Inputs:
    ``facts`` dictionary produced by ``facts.py`` (or loaded from ``facts.json``),
    plus pre-rendered EN and FR Markdown briefs for offline export.

Outputs:
    Writes a single standalone ``dashboard.html`` file with zero external network
    requests and zero figures outside ``facts.json``.

Failure behaviour:
    Never crashes on missing optional fields (such as empty bloc matrices or
    non-numeric taxes); gracefully displays ``Not reported`` placeholders.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from render import render_brief

_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__PAGE_TITLE__</title>
<style>
  :root {
    --bg: #f6f7f9;
    --surface: #ffffff;
    --surface-alt: #f0f3f7;
    --ink: #13202e;
    --muted: #4b5b6b;
    --border: #d5dce4;
    --accent: #0f4c81;
    --accent-soft: #e6f0fa;
    --ok-bg: #e6f4ea;
    --ok-ink: #135e29;
    --note-bg: #fef7e0;
    --note-ink: #7a4f01;
    --flag-bg: #fce8e6;
    --flag-ink: #9c1b13;
    --radius: 10px;
    --shadow: 0 2px 8px rgba(19, 32, 46, 0.06);
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    background: var(--bg);
    color: var(--ink);
    line-height: 1.5;
  }
  a, button { font-family: inherit; }
  button:focus-visible, input:focus-visible, select:focus-visible, [tabindex="0"]:focus-visible {
    outline: 3px solid var(--accent);
    outline-offset: 2px;
  }
  .wrap { max-width: 1180px; margin: 0 auto; padding: 20px 18px 80px; }
  header.hero {
    background: var(--ink);
    color: #fff;
    padding: 22px 24px;
    border-radius: var(--radius);
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 16px;
    box-shadow: var(--shadow);
  }
  .brand h1 { margin: 0; font-size: 1.45rem; letter-spacing: 0.01em; }
  .brand .tagline { color: #c7d6e6; font-size: 0.92rem; margin-top: 4px; }
  .brand .team { color: #9db4ca; font-size: 0.8rem; margin-top: 2px; }
  .toolbar { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
  .btn {
    border: 1px solid #4c647c;
    background: #1d3247;
    color: #fff;
    padding: 8px 13px;
    border-radius: 7px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 600;
  }
  .btn:hover { background: #274461; }
  .btn.primary { background: #2d7dd2; border-color: #2d7dd2; }
  .btn.primary:hover { background: #2266b0; }
  .btn.light { background: var(--surface); color: var(--ink); border-color: var(--border); }
  .btn.light:hover { background: var(--surface-alt); }
  .btn.active { background: var(--accent); color: #fff; border-color: var(--accent); }

  .disclaimer {
    margin-top: 14px;
    background: var(--accent-soft);
    border-left: 4px solid var(--accent);
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 0.88rem;
  }
  .banner {
    margin-top: 14px;
    background: var(--flag-bg);
    border: 1px solid #f5c2be;
    border-left: 5px solid var(--flag-ink);
    padding: 12px 16px;
    border-radius: 8px;
  }
  .banner h2 { margin: 0 0 6px; font-size: 0.96rem; color: var(--flag-ink); }
  .banner ul { margin: 6px 0 0; padding-left: 18px; font-size: 0.88rem; }
  .banner li { margin: 4px 0; }

  .grid-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 14px;
    margin-top: 16px;
  }
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 15px 16px;
    box-shadow: var(--shadow);
  }
  .card-label { font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--muted); font-weight: 700; }
  .card-value { font-size: 1.2rem; font-weight: 700; margin-top: 6px; }
  .card-sub { font-size: 0.82rem; color: var(--muted); margin-top: 4px; }

  section.panel {
    margin-top: 20px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 18px 20px;
    box-shadow: var(--shadow);
  }
  section.panel h2 {
    margin: 0 0 12px;
    font-size: 1.1rem;
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
  }

  .chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 700;
    vertical-align: middle;
  }
  .chip.ok { background: var(--ok-bg); color: var(--ok-ink); }
  .chip.note { background: var(--note-bg); color: var(--note-ink); }
  .chip.flag { background: var(--flag-bg); color: var(--flag-ink); }
  .chip.info { background: var(--accent-soft); color: var(--accent); }

  table.cmp { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
  table.cmp th, table.cmp td {
    text-align: left;
    padding: 9px 10px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
  }
  table.cmp th { background: var(--surface-alt); font-weight: 700; font-size: 0.82rem; text-transform: uppercase; color: var(--muted); }
  .table-scroll { overflow-x: auto; }

  .cite-btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    background: var(--surface-alt);
    border: 1px solid var(--border);
    color: var(--accent);
    border-radius: 5px;
    padding: 2px 7px;
    font-size: 0.76rem;
    font-weight: 600;
    cursor: pointer;
    margin-top: 4px;
  }
  .cite-btn:hover { background: var(--accent-soft); border-color: var(--accent); }

  .tax-bar-wrap { margin-top: 6px; background: var(--surface-alt); height: 10px; border-radius: 5px; overflow: hidden; max-width: 240px; }
  .tax-bar { height: 100%; background: var(--accent); }
  .tax-bar.target { background: #1e8e3e; }

  .checklist { list-style: none; padding: 0; margin: 0; }
  .checklist li {
    display: flex;
    gap: 10px;
    align-items: flex-start;
    padding: 10px 12px;
    border: 1px solid var(--border);
    border-radius: 8px;
    margin-bottom: 8px;
    background: #fcfdff;
  }
  .checklist li.flagged { background: #fff8f7; border-color: #f2c0bc; }
  .checklist input[type="checkbox"] { margin-top: 4px; width: 17px; height: 17px; cursor: pointer; }
  .checklist li.done label { text-decoration: line-through; color: var(--muted); }

  .filter-bar { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 12px; align-items: center; }
  .flag-card {
    border: 1px solid var(--border);
    border-left: 5px solid var(--accent);
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
    background: #fff;
  }
  .flag-card.high { border-left-color: var(--flag-ink); }
  .flag-card.med { border-left-color: var(--note-ink); }
  .flag-card.low { border-left-color: var(--accent); }
  .flag-head { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin-bottom: 6px; }
  .flag-meta { font-size: 0.84rem; color: var(--muted); margin-top: 6px; }

  .external-card {
    border: 1px dashed var(--muted);
    background: var(--surface-alt);
    border-radius: 8px;
    padding: 12px 14px;
    margin-bottom: 10px;
  }
  .meaning-box {
    margin-top: 12px;
    padding: 10px 14px;
    border-radius: 7px;
    background: var(--surface-alt);
    font-size: 0.9rem;
  }

  /* Evidence Drawer */
  .drawer-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(19, 32, 46, 0.45);
    display: none;
    z-index: 90;
  }
  .drawer-backdrop.open { display: block; }
  aside.drawer {
    position: fixed;
    top: 0;
    right: 0;
    width: min(460px, 94vw);
    height: 100vh;
    background: var(--surface);
    box-shadow: -4px 0 24px rgba(0, 0, 0, 0.2);
    z-index: 100;
    padding: 20px;
    overflow-y: auto;
    transform: translateX(100%);
    transition: transform 0.2s ease;
  }
  aside.drawer.open { transform: translateX(0); }
  .drawer pre {
    background: #13202e;
    color: #eef4fa;
    padding: 12px;
    border-radius: 7px;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 0.85rem;
  }
  .drawer-entry { border-bottom: 1px solid var(--border); padding-bottom: 12px; margin-bottom: 12px; }

  @media print {
    body { background: #fff; }
    .toolbar, .filter-bar, .cite-btn, .drawer-backdrop, aside.drawer { display: none !important; }
    .wrap { max-width: 100%; padding: 0; }
    section.panel, .card, header.hero { box-shadow: none; break-inside: avoid; }
    header.hero { background: #fff; color: #000; border: 2px solid #000; }
    .brand .tagline, .brand .team { color: #333; }
  }
</style>
</head>
<body>
<div class="wrap">
  <header class="hero" role="banner">
    <div class="brand">
      <h1 id="hero-title"></h1>
      <div class="tagline" id="hero-tagline"></div>
      <div class="team" id="hero-team"></div>
    </div>
    <div class="toolbar" role="group" aria-label="Dashboard controls">
      <button type="button" class="btn active" id="btn-lang-en" aria-pressed="true">EN</button>
      <button type="button" class="btn" id="btn-lang-fr" aria-pressed="false">FR</button>
      <button type="button" class="btn primary" id="btn-export-md">Export Brief (.md)</button>
      <button type="button" class="btn" id="btn-print">Print / PDF</button>
    </div>
  </header>

  <div class="disclaimer" role="note" id="disclaimer-box"></div>
  <div class="banner" role="region" aria-label="Systemic template defects" id="template-banner" style="display:none;"></div>

  <div class="grid-cards" id="at-a-glance" aria-label="At a glance summary"></div>

  <section class="panel" aria-labelledby="h-reg">
    <h2 id="h-reg"><span>1. Regulators to Engage</span><span class="chip info" id="chip-reg-hint">Click any source button to inspect raw dossier line</span></h2>
    <div class="table-scroll"><table class="cmp" id="tbl-regulators"></table></div>
    <div class="meaning-box" id="meaning-reg"></div>
  </section>

  <section class="panel" aria-labelledby="h-steps">
    <h2 id="h-steps"><span>2. Sector Compliance First Steps (Tickable Checklist)</span></h2>
    <div id="steps-warning"></div>
    <ul class="checklist" id="steps-list"></ul>
    <div class="meaning-box" id="meaning-steps"></div>
  </section>

  <section class="panel" aria-labelledby="h-tax">
    <h2 id="h-tax"><span>3. Tax Differences (CIT &amp; VAT)</span></h2>
    <div class="table-scroll"><table class="cmp" id="tbl-tax"></table></div>
    <div class="meaning-box" id="meaning-tax"></div>
  </section>

  <section class="panel" aria-labelledby="h-lang">
    <h2 id="h-lang"><span>4. Official &amp; Spoken Languages</span></h2>
    <div class="table-scroll"><table class="cmp" id="tbl-lang"></table></div>
    <div class="meaning-box" id="meaning-lang"></div>
  </section>

  <section class="panel" aria-labelledby="h-blocs">
    <h2 id="h-blocs"><span>5. Shared Regional Blocs &amp; Bloc Consistency Matrix</span></h2>
    <div id="blocs-summary"></div>
    <div id="bloc-matrix-wrap" class="table-scroll" style="margin-top:14px;"></div>
    <div class="meaning-box" id="meaning-blocs"></div>
  </section>

  <section class="panel" aria-labelledby="h-flags">
    <h2 id="h-flags"><span>6. Verify First (Country &amp; Bloc Flags)</span></h2>
    <div class="filter-bar" role="group" aria-label="Flag filters">
      <button type="button" class="btn light active" data-sev="all">All</button>
      <button type="button" class="btn light" data-sev="high">High</button>
      <button type="button" class="btn light" data-sev="med">Medium</button>
      <button type="button" class="btn light" data-sev="low">Low</button>
      <label for="rule-filter" style="font-size:0.84rem;color:var(--muted);margin-left:8px;">Rule:</label>
      <select id="rule-filter" class="btn light" aria-label="Filter by validation rule"></select>
    </div>
    <div id="flags-list"></div>
    <div class="meaning-box" id="meaning-flags"></div>
  </section>

  <section class="panel" aria-labelledby="h-ext">
    <h2 id="h-ext"><span>Our Checks (Unverified — Outside Dossiers)</span><span class="chip note">our-check · unverified</span></h2>
    <p id="ext-intro" style="font-size:0.88rem;color:var(--muted);margin-top:0;"></p>
    <div id="ext-list"></div>
  </section>
</div>

<div class="drawer-backdrop" id="drawer-backdrop"></div>
<aside class="drawer" id="evidence-drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title">
  <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
    <h2 id="drawer-title" style="margin:0;font-size:1.05rem;">Dossier Evidence</h2>
    <button type="button" class="btn light" id="btn-close-drawer" aria-label="Close evidence drawer">Close</button>
  </div>
  <p style="font-size:0.82rem;color:var(--muted);margin-top:6px;">Exact raw line, file, section, and line number extracted by Passerelle.</p>
  <div id="drawer-body"></div>
</aside>

<script>
const FACTS = __FACTS_JSON__;
const BRIEFS = __BRIEFS_JSON__;
let currentLang = "en";
let activeSev = "all";
let activeRule = "all";
const evidenceStore = [];

function esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function registerEvidence(fields, title) {
  const clean = (fields || []).filter(Boolean);
  const idx = evidenceStore.length;
  evidenceStore.push({ title: title || "Dossier Evidence", fields: clean });
  return idx;
}

function citeBtn(fields, title) {
  const clean = (fields || []).filter(Boolean);
  if (!clean.length) return "";
  const idx = registerEvidence(clean, title);
  const first = clean[0];
  const label = clean.length === 1
    ? `${first.file} §${first.section} L${first.line}`
    : `${clean.length} sources`;
  return `<button type="button" class="cite-btn" data-ev="${idx}" title="Inspect raw dossier evidence">source: ${esc(label)}</button>`;
}

function openDrawer(idx) {
  const item = evidenceStore[idx];
  if (!item) return;
  document.getElementById("drawer-title").textContent = item.title;
  const body = document.getElementById("drawer-body");
  body.innerHTML = item.fields.map(f => `
    <div class="drawer-entry">
      <div><strong>File:</strong> <code>${esc(f.file)}</code> &middot; <strong>Section:</strong> §${esc(f.section)} &middot; <strong>Line:</strong> ${esc(f.line)}</div>
      <div style="margin-top:6px;"><strong>Parsed value:</strong> ${esc(f.value)}</div>
      <div style="margin-top:6px;"><strong>Raw dossier line:</strong></div>
      <pre>${esc(f.raw || f.value)}</pre>
    </div>
  `).join("");
  document.getElementById("drawer-backdrop").classList.add("open");
  document.getElementById("evidence-drawer").classList.add("open");
  document.getElementById("btn-close-drawer").focus();
}

function closeDrawer() {
  document.getElementById("drawer-backdrop").classList.remove("open");
  document.getElementById("evidence-drawer").classList.remove("open");
}

function fmtNum(v) {
  if (v === null || v === undefined) return "N/A";
  return Number.isInteger(v) ? String(v) : String(v);
}

function renderAll() {
  evidenceStore.length = 0;
  const m = FACTS.meta;
  const fr = currentLang === "fr";
  const regs = FACTS.comparisons.regulators;
  const steps = FACTS.comparisons.sector_steps;
  const taxes = FACTS.comparisons.taxes;
  const langs = FACTS.comparisons.languages;
  const blocs = FACTS.blocs;
  const scores = FACTS.scores;

  document.getElementById("hero-title").textContent =
    (fr ? "Passerelle — Note transfrontalière : " : "Passerelle — Cross-Border Navigator: ") +
    `${m.home_country} → ${m.target_country}`;
  document.getElementById("hero-tagline").textContent = fr ? m.tagline_fr : m.tagline_en;
  document.getElementById("hero-team").textContent = m.team;
  document.getElementById("disclaimer-box").innerHTML =
    `<strong>${fr ? "Avertissement :" : "Disclaimer:"}</strong> ${esc(fr ? m.disclaimer_fr : m.disclaimer_en)}`;

  // Template banner
  const tb = FACTS.template_banner || [];
  const bannerEl = document.getElementById("template-banner");
  if (tb.length) {
    bannerEl.style.display = "block";
    bannerEl.innerHTML = `
      <h2>${fr ? "Défauts systémiques du modèle (hors score pays)" : "Systemic Dossier Template Defects (Excluded from Route Score)"}</h2>
      <ul>${tb.map(item => {
        const flg = (FACTS.flags || []).find(f => f.v_number === item.v_number);
        const btn = flg ? citeBtn(flg.evidence, `${item.v_number} Template Defect`) : "";
        return `<li><strong>[${esc(item.v_number)}]</strong> ${esc(item.affected_count)} / ${esc(item.corpus_total)}: ${esc(item.message)} ${btn}</li>`;
      }).join("")}</ul>`;
  } else {
    bannerEl.style.display = "none";
  }

  // At-a-glance cards
  const sharedText = (blocs.shared || []).map(b => b.canonical).join(", ") || (fr ? "Aucun" : "None");
  const confChip = scores.label === "High" ? "ok" : (scores.label === "Medium" ? "note" : "flag");
  document.getElementById("at-a-glance").innerHTML = `
    <div class="card">
      <div class="card-label">${fr ? "Itinéraire & Secteur" : "Route & Sector"}</div>
      <div class="card-value">${esc(m.home_country)} → ${esc(m.target_country)}</div>
      <div class="card-sub">${esc(fr ? m.sector_display_fr : m.sector_display_en)}</div>
    </div>
    <div class="card">
      <div class="card-label">${fr ? "Blocs partagés" : "Shared Blocs"}</div>
      <div class="card-value">${esc(sharedText)}</div>
      <div class="card-sub">${fr ? "Intersection canonique des dossiers" : "Canonical intersection from dossiers"}</div>
    </div>
    <div class="card">
      <div class="card-label">${fr ? "Alertes (pays & bloc)" : "Verify-First Flags (Country & Bloc)"}</div>
      <div class="card-value">${scores.counts.high}H · ${scores.counts.med}M · ${scores.counts.low}L</div>
      <div class="card-sub">${scores.counts.total} total (${scores.template_flag_count} ${fr ? "bannière modèle" : "template banner"})</div>
    </div>
    <div class="card">
      <div class="card-label">${fr ? "Fiabilité des données" : "Data Confidence"}</div>
      <div class="card-value"><span class="chip ${confChip}">${esc(scores.label)}</span></div>
      <div class="card-sub">${esc(fr ? scores.note_fr : scores.note_en)}</div>
    </div>`;

  // 1. Regulators table
  const cb = regs.central_bank, cur = regs.currency, dp = regs.data_protection, sr = regs.sector_regulator;
  const sameChip = ok => `<span class="chip ${ok ? "ok" : "note"}">${ok ? (fr ? "Identique" : "Same") : (fr ? "Diffère" : "Differs")}</span>`;
  document.getElementById("tbl-regulators").innerHTML = `
    <thead><tr>
      <th>${fr ? "Domaine" : "Area"}</th>
      <th>${esc(m.home_country)} (${fr ? "Origine" : "Home"})</th>
      <th>${esc(m.target_country)} (${fr ? "Cible" : "Target"})</th>
      <th>${fr ? "Statut" : "Status"}</th>
    </tr></thead>
    <tbody>
      <tr>
        <td><strong>${fr ? "Banque centrale" : "Central bank"}</strong></td>
        <td>${esc(cb.home_field ? cb.home_field.value : "N/A")}<br><span class="chip info">${esc(cb.home_canonical)}</span> ${citeBtn([cb.home_field], "Home Central Bank")}</td>
        <td>${esc(cb.target_field ? cb.target_field.value : "N/A")}<br><span class="chip info">${esc(cb.target_canonical)}</span> ${citeBtn([cb.target_field], "Target Central Bank")}</td>
        <td>${sameChip(cb.same)}</td>
      </tr>
      <tr>
        <td><strong>${fr ? "Devise" : "Currency"}</strong></td>
        <td><code>${esc(cur.home_code)}</code> ${citeBtn([cur.home_field], "Home Currency")}</td>
        <td><code>${esc(cur.target_code)}</code> ${citeBtn([cur.target_field], "Target Currency")}</td>
        <td>${sameChip(cur.same)}</td>
      </tr>
      <tr>
        <td><strong>${fr ? "Protection des données" : "Data protection"}</strong></td>
        <td>${esc(dp.home_field ? dp.home_field.value : "N/A")}<br>${citeBtn([dp.home_field], "Home DPA")}</td>
        <td>${esc(dp.target_field ? dp.target_field.value : "N/A")}<br>${citeBtn([dp.target_field], "Target DPA")}</td>
        <td>${sameChip(dp.same)}${dp.same_acronym_different_expansion ? '<br><span class="chip flag">V08 mismatch</span>' : ""}</td>
      </tr>
      <tr>
        <td><strong>${fr ? "Régulateur sectoriel" : "Sector regulator"}</strong><br><small style="color:var(--muted)">${esc(fr ? sr.role_fr : sr.role_en)}</small></td>
        <td>${esc(sr.home.expected_canonical || "N/A")} ${citeBtn([sr.home.expected_field], "Home Sector Regulator")}${sr.home.section4_conflict ? `<br><span class="chip flag">§4 conflict</span> ${citeBtn([sr.home.section4_named_field], "Home §4 Conflict")}` : ""}</td>
        <td>${esc(sr.target.expected_canonical || "N/A")} ${citeBtn([sr.target.expected_field], "Target Sector Regulator")}${sr.target.section4_conflict ? `<br><span class="chip flag">§4 conflict</span> ${citeBtn([sr.target.section4_named_field], "Target §4 Conflict")}` : ""}</td>
        <td>${sameChip(sr.same)}</td>
      </tr>
    </tbody>`;
  document.getElementById("meaning-reg").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (cb.same
      ? (fr ? "Vous restez sous la même banque centrale (l'institution publique qui gère la monnaie et les règles bancaires), mais vérifiez séparément l'autorité nationale de protection des données dans le pays cible." : "You stay under the same central bank (the public authority that manages money and approves financial services), though you still need to confirm the target country's privacy office (the agency overseeing customer personal data).")
      : (fr ? "Vous changez de banque centrale : prévoyez une nouvelle demande d'agrément locale dans le pays cible." : "You are moving to a different central bank (the public authority that manages money and approves financial services), so plan for a fresh local licensing process."));

  // 2. First steps checklist
  document.getElementById("steps-warning").innerHTML = steps.has_template_flagged_steps
    ? `<div class="disclaimer" style="background:var(--flag-bg);border-left-color:var(--flag-ink);margin:0 0 12px;">${fr ? "Attention : la ligne section 4 contient des défauts du modèle (marqués ci-dessous) — ne les prenez pas pour des faits établis." : "Warning: the Section 4 row contains template defects (marked below) — do not treat flagged text as fact."}</div>`
    : "";
  const tSteps = steps.target_steps || [];
  document.getElementById("steps-list").innerHTML = tSteps.map((st, i) => `
    <li class="${st.template_flagged ? "flagged" : ""}" id="step-li-${i}">
      <input type="checkbox" id="step-cb-${i}" onchange="document.getElementById('step-li-${i}').classList.toggle('done', this.checked)">
      <div>
        <label for="step-cb-${i}" style="cursor:pointer;">
          <strong>${st.order}.</strong>
          ${st.template_flagged ? `<span class="chip flag">${fr ? "Défaut du modèle" : "FLAGGED — template defect"}</span> ` : ""}
          ${esc(st.text)}
        </label><br>
        ${citeBtn([st.field], `Target Step ${st.order}`)}
      </div>
    </li>`).join("");
  document.getElementById("meaning-steps").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (steps.has_template_flagged_steps
      ? (fr ? "Utilisez cette liste comme aide-mémoire de départ uniquement et confirmez chaque démarche directement auprès de la banque centrale ou du ministère compétent." : "Parts of this checklist mix up the wrong agency or insert a sales-tax rate where a registration fee belongs, so confirm every step with the real licensing office.")
      : (fr ? "Suivez ces premières démarches dans l'ordre en confirmant les frais actuels auprès de chaque autorité locale." : "Work through these steps in order and confirm current fees directly with each local office."));

  // 3. Taxes table
  function taxRow(label, tc) {
    const hVal = tc.home_field ? tc.home_field.value : "N/A";
    const tVal = tc.target_field ? tc.target_field.value : "N/A";
    const hW = tc.home_headline !== null ? Math.min(100, (tc.home_headline / 50) * 100) : 0;
    const tW = tc.target_headline !== null ? Math.min(100, (tc.target_headline / 50) * 100) : 0;
    let deltaHtml = "";
    if (tc.comparable) {
      const sign = tc.delta_pp > 0 ? "+" : "";
      deltaHtml = `<span class="chip info">${sign}${fmtNum(tc.delta_pp)} pp</span><br>${citeBtn([tc.home_field, tc.target_field], label + " Delta")}`;
    } else if (tc.same_headline && tc.home_headline !== null) {
      deltaHtml = `<span class="chip note">${fr ? "Même taux principal" : "Same headline rate"} (${fmtNum(tc.home_headline)}%)</span><br><small style="color:var(--muted)">${fr ? "Taux variantes présents — aucun écart soustrait" : "Variant rates present — no numeric delta claimed"}</small><br>${citeBtn([tc.home_field, tc.target_field], label + " Caveat")}`;
    } else {
      deltaHtml = `<span class="chip flag">${fr ? "Non comparable en l'état" : "Uncomparable as-is"}</span><br>${citeBtn([tc.home_field, tc.target_field], label)}`;
    }
    return `<tr>
      <td><strong>${esc(label)}</strong></td>
      <td><code>${esc(hVal)}</code><div class="tax-bar-wrap"><div class="tax-bar" style="width:${hW}%"></div></div>${citeBtn([tc.home_field], label + " Home")}</td>
      <td><code>${esc(tVal)}</code><div class="tax-bar-wrap"><div class="tax-bar target" style="width:${tW}%"></div></div>${citeBtn([tc.target_field], label + " Target")}</td>
      <td>${deltaHtml}</td>
    </tr>`;
  }
  document.getElementById("tbl-tax").innerHTML = `
    <thead><tr>
      <th>${fr ? "Impôt" : "Tax"}</th>
      <th>${esc(m.home_country)}</th>
      <th>${esc(m.target_country)}</th>
      <th>${fr ? "Écart (cible − origine)" : "Delta (target − home)"}</th>
    </tr></thead>
    <tbody>
      ${taxRow(fr ? "Impôt sur les sociétés (IS)" : "Corporate income tax (CIT)", taxes.cit)}
      ${taxRow(fr ? "TVA / taxe sur les ventes" : "VAT / sales tax", taxes.vat)}
    </tbody>`;
  document.getElementById("meaning-tax").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (fr ? "Vérifiez le taux exact applicable à votre activité auprès de l'administration fiscale locale avant de figer vos prix (l'IS porte sur les bénéfices annuels, la TVA s'ajoute aux ventes)." : "Confirm the exact rate for your sector with the local tax office before locking in pricing (corporate income tax is paid on yearly profit, and VAT is added to customer sales).");

  // 4. Languages table
  const hOff = (langs.home_official || []).map(f => f.value).join(", ");
  const tOff = (langs.target_official || []).map(f => f.value).join(", ");
  const hDom = (langs.home_dominant || []).map(f => f.value).join(", ");
  const tDom = (langs.target_dominant || []).map(f => f.value).join(", ");
  const dropped = (langs.dropped_official || []).join(", ");
  document.getElementById("tbl-lang").innerHTML = `
    <thead><tr>
      <th>${fr ? "Type" : "Type"}</th>
      <th>${esc(m.home_country)}</th>
      <th>${esc(m.target_country)}</th>
      <th>${fr ? "Changement" : "Change"}</th>
    </tr></thead>
    <tbody>
      <tr>
        <td><strong>${fr ? "Langues officielles" : "Official languages"}</strong></td>
        <td>${esc(hOff)}<br>${citeBtn(langs.home_official.slice(0,1), "Home Official Languages")}</td>
        <td>${esc(tOff)}<br>${citeBtn(langs.target_official.slice(0,1), "Target Official Languages")}</td>
        <td>${sameChip(!langs.official_differs)}${dropped ? `<br><small>${fr ? "Absente cible :" : "Drops out:"} <strong>${esc(dropped)}</strong></small>` : ""}</td>
      </tr>
      <tr>
        <td><strong>${fr ? "Langues parlées / d'affaires" : "Dominant spoken / business"}</strong></td>
        <td>${esc(hDom)}<br>${citeBtn(langs.home_dominant.slice(0,1), "Home Dominant Languages")}</td>
        <td>${esc(tDom)}<br>${citeBtn(langs.target_dominant.slice(0,1), "Target Dominant Languages")}</td>
        <td>${sameChip(!langs.dominant_differs)}</td>
      </tr>
    </tbody>`;
  document.getElementById("meaning-lang").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (langs.official_differs
      ? (fr ? "Les langues officielles changent : prévoyez de traduire vos contrats, écrans clients et dossiers administratifs dans la langue du pays cible." : "Official languages change across this border, so plan time and budget to translate contracts, customer screens, and government filings.")
      : (fr ? "Les mêmes langues officielles s'appliquent des deux côtés, réduisant les coûts de traduction." : "Both countries share the same official languages, letting you reuse most legal and customer text."));

  // 5. Blocs + CEMAC / Shared Bloc Consistency Matrix
  const sharedHtml = (blocs.shared || []).map(b => `
    <div style="margin-bottom:8px;">
      <strong>${esc(fr ? b.name_fr : b.name_en)}:</strong> ${esc(fr ? b.meaning_fr : b.meaning_en)}
      ${citeBtn([b.home_entry.field, b.target_entry.field], b.canonical)}
    </div>`).join("");
  const onlyHome = (blocs.only_in_home || []).map(e => `<code>${esc(e.raw_value)}</code> ${citeBtn([e.field], e.raw_value)}`).join(", ");
  const onlyTarget = (blocs.only_in_target || []).map(e => `<code>${esc(e.raw_value)}</code> ${citeBtn([e.field], e.raw_value)}`).join(", ");
  document.getElementById("blocs-summary").innerHTML = sharedHtml +
    (onlyHome ? `<div style="margin-top:6px;"><strong>${fr ? "Uniquement origine :" : "Only in home:"}</strong> ${onlyHome}</div>` : "") +
    (onlyTarget ? `<div style="margin-top:6px;"><strong>${fr ? "Uniquement cible :" : "Only in target:"}</strong> ${onlyTarget}</div>` : "");

  const matrices = FACTS.bloc_matrices || {};
  const mKeys = Object.keys(matrices);
  const mWrap = document.getElementById("bloc-matrix-wrap");
  if (mKeys.length) {
    mWrap.innerHTML = mKeys.map(bk => {
      const mx = matrices[bk];
      return `
        <h3 style="margin:6px 0 10px;font-size:0.98rem;">${fr ? "Matrice de cohérence du bloc" : "Bloc Consistency Matrix"} — ${esc(bk)} (${mx.member_count})</h3>
        <table class="cmp">
          <thead><tr>
            <th>${fr ? "Pays" : "Country"}</th>
            <th>${fr ? "Devise" : "Currency"}</th>
            <th>${fr ? "Banque centrale" : "Central bank"}</th>
            <th>${fr ? "Symétrie blocs" : "Bloc symmetry"}</th>
            <th>${fr ? "DPA" : "DPA naming"}</th>
            <th>${fr ? "À vérifier" : "Placeholders"}</th>
            <th>${fr ? "Alertes" : "Flags"}</th>
          </tr></thead>
          <tbody>${mx.rows.map(r => `
            <tr>
              <td><strong>${esc(r.country)}</strong></td>
              <td><span class="chip ${esc(r.currency.status)}">${esc(r.currency.status)}</span> ${esc(r.currency.label)}<br>${citeBtn(r.currency.evidence, r.country + " Currency")}</td>
              <td><span class="chip ${esc(r.central_bank.status)}">${esc(r.central_bank.status)}</span> ${esc(r.central_bank.label)}<br>${citeBtn(r.central_bank.evidence, r.country + " Central Bank")}</td>
              <td><span class="chip ${esc(r.bloc_symmetry.status)}">${esc(r.bloc_symmetry.status)}</span> ${esc(r.bloc_symmetry.label)}<br>${citeBtn(r.bloc_symmetry.evidence, r.country + " Blocs")}</td>
              <td><span class="chip ${esc(r.dpa_naming.status)}">${esc(r.dpa_naming.status)}</span> ${esc(r.dpa_naming.label)}<br>${citeBtn(r.dpa_naming.evidence, r.country + " DPA")}</td>
              <td><span class="chip ${esc(r.placeholders.status)}">${esc(r.placeholders.status)}</span> ${esc(r.placeholders.label)}<br>${citeBtn(r.placeholders.evidence, r.country + " Placeholders")}</td>
              <td><span class="chip ${esc(r.flag_counts.status)}">${esc(r.flag_counts.label)}</span></td>
            </tr>`).join("")}
          </tbody>
        </table>`;
    }).join("");
  } else {
    mWrap.innerHTML = "";
  }
  document.getElementById("meaning-blocs").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (fr ? "Un bloc régional partagé simplifie certains paiements et échanges, mais vous devez toujours enregistrer votre entreprise dans le pays cible." : "Sharing a regional bloc (an agreement among neighbouring countries on currency or trade) can ease transfers and customs, but you still need local registration.");

  // 6. Verify-first panel
  const routeFlags = (FACTS.flags || []).filter(f => f.scope === "country" || f.scope === "bloc");
  const ruleSel = document.getElementById("rule-filter");
  const uniqueRules = Array.from(new Set(routeFlags.map(f => f.v_number))).sort();
  ruleSel.innerHTML = `<option value="all">${fr ? "Toutes les règles" : "All rules"}</option>` +
    uniqueRules.map(r => `<option value="${esc(r)}"${activeRule === r ? " selected" : ""}>${esc(r)}</option>`).join("");
  renderFlags(routeFlags);
  document.getElementById("meaning-flags").innerHTML = `<strong>${fr ? "Ce que cela signifie pour vous :" : "What this means for you:"}</strong> ` +
    (fr ? "Traitez ces alertes avant toute dépense juridique ou dépôt officiel : chacune signale une contradiction ou une information manquante dans les dossiers." : "Review these flags before paying legal fees or filing applications, because each marks a contradiction or missing name inside the source dossiers.");

  // Our checks (unverified)
  document.getElementById("ext-intro").textContent = fr
    ? "Points fondés sur des vérifications extérieures aux dossiers — jamais présentés comme des faits issus des dossiers."
    : "Items below come from checks outside the source dossiers and are never presented as dossier facts.";
  const exts = FACTS.our_checks || [];
  document.getElementById("ext-list").innerHTML = exts.length
    ? exts.map(c => `
      <div class="external-card">
        <span class="chip note">${esc(c.id)} · ${esc(c.status)}</span>
        <span class="chip info">our-check</span>
        <div style="margin-top:6px;">${esc(fr && c.claim_fr ? c.claim_fr : c.claim)}</div>
        <div style="font-size:0.8rem;color:var(--muted);margin-top:4px;">${fr ? "URL source :" : "Source URL:"} ${esc(c.source_url || (fr ? "aucune URL enregistrée" : "none recorded yet"))}</div>
      </div>`).join("")
    : `<p>${fr ? "Aucune vérification externe enregistrée." : "No external checks recorded for this route."}</p>`;
}

function renderFlags(routeFlags) {
  const fr = currentLang === "fr";
  const filtered = routeFlags.filter(f =>
    (activeSev === "all" || f.severity === activeSev) &&
    (activeRule === "all" || f.v_number === activeRule)
  );
  const el = document.getElementById("flags-list");
  if (!filtered.length) {
    el.innerHTML = `<p style="color:var(--muted);">${fr ? "Aucune alerte correspondant à ce filtre." : "No flags match the selected filter."}</p>`;
    return;
  }
  el.innerHTML = filtered.map(f => {
    const sevCls = f.severity === "high" ? "flag" : (f.severity === "med" ? "note" : "info");
    return `
      <div class="flag-card ${esc(f.severity)}">
        <div class="flag-head">
          <span class="chip ${sevCls}">${esc(f.v_number)} · ${esc(f.severity.toUpperCase())}</span>
          <span class="chip info">${esc(f.scope)}</span>
          <span class="chip ok">${esc(f.confidence)}</span>
          ${citeBtn(f.evidence, `${f.v_number} Evidence`)}
        </div>
        <div><strong>${esc(f.message)}</strong></div>
        <div class="flag-meta"><strong>${fr ? "Pourquoi c'est important :" : "Why it matters:"}</strong> ${esc(f.why_it_matters)}</div>
        <div class="flag-meta"><strong>${fr ? "Qui interroger :" : "Who to ask:"}</strong> ${esc(f.suggested_check)}</div>
      </div>`;
  }).join("");
}

document.addEventListener("click", ev => {
  const btn = ev.target.closest(".cite-btn");
  if (btn) { openDrawer(Number(btn.dataset.ev)); return; }
  const sevBtn = ev.target.closest("[data-sev]");
  if (sevBtn) {
    activeSev = sevBtn.dataset.sev;
    document.querySelectorAll("[data-sev]").forEach(b => b.classList.toggle("active", b === sevBtn));
    renderFlags((FACTS.flags || []).filter(f => f.scope === "country" || f.scope === "bloc"));
  }
});

document.getElementById("rule-filter").addEventListener("change", ev => {
  activeRule = ev.target.value;
  renderFlags((FACTS.flags || []).filter(f => f.scope === "country" || f.scope === "bloc"));
});
document.getElementById("btn-close-drawer").addEventListener("click", closeDrawer);
document.getElementById("drawer-backdrop").addEventListener("click", closeDrawer);
document.addEventListener("keydown", ev => { if (ev.key === "Escape") closeDrawer(); });

document.getElementById("btn-lang-en").addEventListener("click", () => {
  currentLang = "en";
  document.getElementById("btn-lang-en").classList.add("active");
  document.getElementById("btn-lang-fr").classList.remove("active");
  document.getElementById("btn-lang-en").setAttribute("aria-pressed", "true");
  document.getElementById("btn-lang-fr").setAttribute("aria-pressed", "false");
  renderAll();
});
document.getElementById("btn-lang-fr").addEventListener("click", () => {
  currentLang = "fr";
  document.getElementById("btn-lang-fr").classList.add("active");
  document.getElementById("btn-lang-en").classList.remove("active");
  document.getElementById("btn-lang-fr").setAttribute("aria-pressed", "true");
  document.getElementById("btn-lang-en").setAttribute("aria-pressed", "false");
  renderAll();
});
document.getElementById("btn-export-md").addEventListener("click", () => {
  const md = BRIEFS[currentLang] || BRIEFS.en;
  const blob = new Blob([md], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `passerelle_${FACTS.meta.home_slug}_to_${FACTS.meta.target_slug}_${currentLang}.md`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 500);
});
document.getElementById("btn-print").addEventListener("click", () => window.print());

renderAll();
</script>
</body>
</html>
"""


def _safe_inline_json(obj: Any) -> str:
    """Serialise an object to JSON safe for embedding inside an HTML ``<script>`` tag.

    Purpose:
        Escape ``</`` sequences so embedded JSON can never accidentally terminate the
        inline ``<script>`` block.

    Inputs:
        obj: JSON-serialisable Python object.

    Outputs:
        Escaped JSON string.

    Failure behaviour:
        Raises ``TypeError`` if ``obj`` is not JSON-serialisable.
    """
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def render_dashboard_html(facts: dict[str, Any]) -> str:
    """Render a single self-contained offline HTML dashboard from ``facts``.

    Purpose:
        Embed ``facts`` and its EN/FR Markdown briefs directly inside one standalone
        HTML file with zero external requests and zero invented figures (A9, A11).

    Inputs:
        facts: Dictionary returned by ``facts.build_facts``.

    Outputs:
        Complete HTML string ready to write to ``dashboard.html``.

    Failure behaviour:
        Never raises on valid ``facts`` payloads.
    """
    meta = facts["meta"]
    title = f"Passerelle — {meta['home_country']} to {meta['target_country']} ({meta['sector_display_en']})"
    briefs = {
        "en": render_brief(facts, lang="en"),
        "fr": render_brief(facts, lang="fr"),
    }
    html = _HTML_TEMPLATE.replace("__PAGE_TITLE__", title)
    html = html.replace("__FACTS_JSON__", _safe_inline_json(facts))
    html = html.replace("__BRIEFS_JSON__", _safe_inline_json(briefs))
    return html


def write_dashboard(facts: dict[str, Any], out_path: Path | str | None = None) -> Path:
    """Write ``dashboard.html`` to disk from a ``facts`` payload.

    Purpose:
        Save the offline standalone dashboard file inside ``Group 1/`` (or a custom
        path passed by the caller).

    Inputs:
        facts: Dictionary returned by ``facts.build_facts``.
        out_path: Optional destination path (defaults to ``<Group 1>/dashboard.html``).

    Outputs:
        ``Path`` to the written HTML file.

    Failure behaviour:
        Creates parent directories automatically; raises ``OSError`` only on write failure.
    """
    target = (
        Path(out_path)
        if out_path is not None
        else Path(__file__).resolve().parent / "dashboard.html"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_dashboard_html(facts), encoding="utf-8")
    return target


def main() -> None:
    """Regenerate ``dashboard.html`` from ``facts.json`` in ``Group 1/``.

    Purpose:
        Provide a direct standalone entry point for rebuilding ``dashboard.html``
        offline from an existing ``facts.json``.

    Inputs:
        None (reads ``facts.json`` in the module directory).

    Outputs:
        Writes ``dashboard.html`` and prints its location.

    Failure behaviour:
        Raises ``FileNotFoundError`` if ``facts.json`` has not been generated yet.
    """
    base = Path(__file__).resolve().parent
    facts_path = base / "facts.json"
    facts = json.loads(facts_path.read_text(encoding="utf-8"))
    out = write_dashboard(facts, base / "dashboard.html")
    print(f"Dashboard written to: {out}")


if __name__ == "__main__":
    main()
