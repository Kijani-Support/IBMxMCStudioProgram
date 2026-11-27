# Passerelle — Note de lancement transfrontalier: Cameroon -> Gabon

*Franchir la frontière, vérifier d'abord.* — Christopher Damian Munene, Mark Lekayia (Group 1, IBM x MC Studio Dev Day)

> **Disclaimer / Avertissement:** Référence de planification uniquement — ce document ne constitue pas un conseil juridique, fiscal ou financier. Vérifiez chaque élément auprès des autorités compétentes avant d'agir.

> **Défauts systémiques du modèle de dossier (hors score pays)**
> Ces anomalies touchent la plupart des 54 dossiers d'origine (erreurs de génération du modèle) et sont affichées séparément de la confiance propre à votre itinéraire :
> - [TPL-S4-LICENSOR] 54 dossiers sur 54 partagent ce défaut : Section 4 Fintech row names the data protection authority as the payments and lending licensor instead of the central bank. (source: cameroon.md §4, line 33; gabon.md §4, line 33)
> - [TPL-S4-VAT-LEAK] 54 dossiers sur 54 partagent ce défaut : Section 4 Fintech row inserts the Section 5 VAT percentage inside the data-protection registration fee slot. (source: cameroon.md §4, line 33; gabon.md §4, line 33)

## 0. Vue d'ensemble

- **Itinéraire:** Cameroon (Pays d'origine) -> Gabon (Pays cible) (source: cameroon.md, line 1); (source: gabon.md, line 1)
- **Secteur:** Fintech
- **Blocs partagés:** African Union (source: cameroon.md §1, line 13; gabon.md §1, line 13), CEMAC (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **Alertes « Vérifier d'abord » (pays & bloc):** 0 Élevée, 4 Moyenne, 1 Faible (5 total; bannière modèle: 2)
- **Fiabilité des données du dossier:** **Élevée** (0 Élevée, 4 Moyenne, 1 Faible) — Mesure uniquement la qualité des dossiers sources pour cet itinéraire (pays et bloc), jamais le risque juridique.

## 1. Régulateurs à contacter

- **Banque centrale** (`Identique`):
  - Cameroon: Banque des États de l'Afrique Centrale (BEAC) [normalisé: `BEAC`] (source: cameroon.md §2, line 19)
  - Gabon: BEAC [normalisé: `BEAC`] (source: gabon.md §2, line 19)
- **Devise** (`Identique`): Cameroon: `XAF` (source: cameroon.md §1, line 12) | Gabon: `XAF` (source: gabon.md §1, line 12)
- **Autorité de protection des données** (`Diffère`):
  - Cameroon: CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) (source: cameroon.md §2, line 21)
  - Gabon: CNPD (Commission Nationale pour la Protection des Données) (source: gabon.md §2, line 21)
  - *Même acronyme (CNPD) mais intitulés complets différents entre les deux dossiers* (source: cameroon.md §2, line 21; gabon.md §2, line 21)
- **Régulateur sectoriel (contact d'agrément)** — Banque centrale (contact principal pour l'agrément des paiements et du crédit) (`Identique`):
  - Cameroon: Banque des États de l'Afrique Centrale (BEAC) [normalisé: `BEAC`] (source: cameroon.md §2, line 19)
    - **Autorité citée en section 4 (conflit détecté):** `CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) licensing for payments and lending` [À vérifier — défaut du modèle] (source: cameroon.md §4, line 33)
  - Gabon: BEAC [normalisé: `BEAC`] (source: gabon.md §2, line 19)
    - **Autorité citée en section 4 (conflit détecté):** `CNPD (Commission Nationale pour la Protection des Données) licensing for payments and lending` [À vérifier — défaut du modèle] (source: gabon.md §4, line 33)

**Ce que cela signifie pour vous:** Vous restez sous la même banque centrale (l'institution publique qui gère la monnaie et les règles bancaires), mais vous devez vérifier séparément l'autorité nationale chargée de protéger les données personnelles dans le pays cible.

## 2. Étapes de conformité sectorielle (Premières démarches)

> Attention : la ligne section 4 de ce secteur comporte un défaut connu du modèle de dossier (signalé ci-dessous). Les étapes concernées sont marquées « À vérifier — défaut du modèle » et ne doivent pas être prises pour des faits établis.

### Gabon (Pays cible)
1. **[À vérifier — défaut du modèle]** *"CNPD (Commission Nationale pour la Protection des Données) licensing for payments and lending"* (source: gabon.md §4, line 33)
2. AML/CFT compliance (source: gabon.md §4, line 33)
3. **[À vérifier — défaut du modèle]** *"data protection registration (18%)"* (source: gabon.md §4, line 33)
4. consumer protection (source: gabon.md §4, line 33)

### Cameroon (Pays d'origine)
1. **[À vérifier — défaut du modèle]** *"CNPD (Commission Nationale pour la Protection des Données à Caractère Personnel) licensing for payments and lending"* (source: cameroon.md §4, line 33)
2. AML/CFT compliance (source: cameroon.md §4, line 33)
3. **[À vérifier — défaut du modèle]** *"data protection registration (19.25%)"* (source: cameroon.md §4, line 33)
4. consumer protection (source: cameroon.md §4, line 33)

**Ce que cela signifie pour vous:** Certaines étapes listées dans le dossier mélangent le mauvais organisme ou un taux de taxe à la place d'un frais de dossier ; utilisez cette liste comme aide-mémoire de départ et confirmez chaque démarche auprès de la banque centrale ou du ministère compétent.

## 3. Écarts fiscaux (IS et TVA)

- **Impôt sur les sociétés (IS):**
  - Cameroon: `30% (33% for some sectors)` (source: cameroon.md §5, line 44)
  - Gabon: `30%` (source: gabon.md §5, line 44)
  - **Écart (cible − origine):** `Même taux principal (30%)` — Attention : taux variantes présents (Cameroon: 30%, 33%) ; aucun écart chiffré calculé au-delà du taux principal (source: cameroon.md §5, line 44; gabon.md §5, line 44)
- **TVA / taxe sur les ventes:**
  - Cameroon: `19.25%` (source: cameroon.md §5, line 45)
  - Gabon: `18%` (source: gabon.md §5, line 45)
  - **Écart (cible − origine):** `-1.25 points de pourcentage` (source: cameroon.md §5, line 45; gabon.md §5, line 45)

**Ce que cela signifie pour vous:** Au moins un taux comporte plusieurs tranches ou n'est pas chiffré dans le dossier ; ne calculez pas de budget définitif sans confirmer le taux exact applicable à votre activité auprès de l'administration fiscale locale.

## 4. Langues officielles et langues d'affaires

- **Langues officielles** (`Diffère`):
  - Cameroon: English, French (source: cameroon.md §1, line 14)
  - Gabon: French (source: gabon.md §1, line 14)
  - Langues officielles communes: French (source: cameroon.md §1, line 14; gabon.md §1, line 14)
  - Langues présentes à l'origine mais absentes dans le pays cible: English (source: cameroon.md §1, line 14)
- **Langues parlées / d'affaires** (`Diffère`):
  - Cameroon: French, English, Cameroonian Pidgin, Fulfulde, Ewondo, Duala (source: cameroon.md §1, line 15)
  - Gabon: French, Fang, Myene, Punu, Nzebi (source: gabon.md §1, line 15)

**Ce que cela signifie pour vous:** Les langues officielles changent entre les deux pays : prévoyez de traduire vos contrats, vos écrans clients et vos dossiers administratifs dans la langue utilisée par les autorités du pays cible.

## 5. Blocs régionaux partagés et effets pratiques

- **Union africaine**: Organisation continentale soutenant la Zone de libre-échange continentale africaine (ZLECAf), mais les agréments quotidiens restent délivrés au niveau national ou sous-régional. (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **CEMAC (Communauté Économique et Monétaire de l'Afrique Centrale)**: Zone monétaire commune (XAF) avec une banque centrale unique (BEAC), ce qui supprime le risque de change entre pays membres et harmonise les règles bancaires régionales. (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **Uniquement dans le pays d'origine (Cameroon):** `ECOWAS (observer)` (source: cameroon.md §1, line 13)

**Ce que cela signifie pour vous:** Appartenir à un même groupe régional (un accord entre États voisins sur la monnaie ou le commerce) simplifie certains échanges et paiements, mais ne supprime pas l'obligation de vous enregistrer dans le pays cible.

## 6. Points à vérifier en priorité

### Moyenne (4)
- **[DPA-EXPANSION-MISMATCH]** (Portée: `bloc` | Origine: `in-dossier`): Both dossiers use the data-protection acronym 'CNPD' with different full names ('Commission Nationale pour la Protection des Données à Caractère Personnel' vs 'Commission Nationale pour la Protection des Données'). (source: cameroon.md §2, line 21; gabon.md §2, line 21)
  - *Pourquoi c'est important:* Conflicting agency names suggest the dossier entry may be templated rather than verified against national law.
  - *Qui interroger:* Confirm the official legal name and active registration office of each country's privacy regulator directly.
- **[PLACEHOLDER-VALUE]** (Portée: `country` | Origine: `in-dossier`): Target dossier has placeholder text in energy regulator: 'Ministry of Energy (verify current regulator)'. (source: gabon.md §3, line 25)
  - *Pourquoi c'est important:* The dossier does not name a verified office to contact for this step.
  - *Qui interroger:* Check the national government portal or Ministry of Finance/Commerce for the current energy regulator.
- **[PLACEHOLDER-VALUE]** (Portée: `country` | Origine: `in-dossier`): Target dossier has placeholder text in investment promotion agency: 'Verify current agency'. (source: gabon.md §5, line 47)
  - *Pourquoi c'est important:* The dossier does not name a verified office to contact for this step.
  - *Qui interroger:* Check the national government portal or Ministry of Finance/Commerce for the current investment promotion agency.
- **[TAX-UNCOMPARABLE]** (Portée: `country` | Origine: `in-dossier`): Corporate income tax (CIT) cannot be subtracted directly (compound/multi-rate cell); all rates are shown without computing a single delta. (source: cameroon.md §5, line 44; gabon.md §5, line 44)
  - *Pourquoi c'est important:* Different business sectors or company sizes can face different tax rates, so a single subtraction could mislead your budget.
  - *Qui interroger:* Confirm which tax bracket applies to your company with each country's national revenue authority.

### Faible (1)
- **[BLOC-QUALIFIER-UNCONFIRMED]** (Portée: `bloc` | Origine: `in-dossier`): Home dossier lists 'ECOWAS (observer)', which carries a 'observer' qualifier and is absent from the partner dossier. (source: cameroon.md §1, line 13)
  - *Pourquoi c'est important:* Observer or unverified bloc status does not grant the trade or licensing benefits of full membership.
  - *Qui interroger:* Do not rely on this bloc for cross-border licensing; confirm membership status on the bloc's official registry.

**Ce que cela signifie pour vous:** Traitez en priorité les alertes les plus critiques avant toute dépense juridique ou dépôt officiel : elles signalent des informations contradictoires ou manquantes dans les dossiers sources.

## Nos vérifications externes (non vérifié)

Les points ci-dessous reposent sur des connaissances extérieures aux dossiers (jamais présentés comme des faits issus des dossiers). Statut : non vérifié tant qu'une source officielle n'est pas jointe.

- **[EXT-01]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Dans la zone CEMAC, l'agrément et la supervision des banques et établissements de paiement impliquent un superviseur bancaire régional aux côtés de la BEAC et des ministères des Finances ; aucun superviseur bancaire régional n'est cité dans les dossiers CEMAC.
- **[EXT-02]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Vérifier si le Cameroun dispose réellement d'un statut d'observateur auprès de la CEDEAO ; le Cameroun est membre de la CEMAC et ce statut n'est pas confirmé par les dossiers partenaires.
- **[EXT-03]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Vérifier l'autorité nationale de protection des données actuellement opérationnelle dans les deux pays plutôt que de s'appuyer sur les intitulés CNPD divergents figurant dans les dossiers.
