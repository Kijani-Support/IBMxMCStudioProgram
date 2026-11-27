# Passerelle — Note de lancement transfrontalier: Cameroon -> Gabon

*Franchir la frontière, vérifier d'abord.* — Christopher Damian Munene, Mark Lekayia (Group 1, IBM x MC Studio Dev Day)

> **Disclaimer / Avertissement:** Référence de planification uniquement — ce document ne constitue pas un conseil juridique, fiscal ou financier. Vérifiez chaque élément auprès des autorités compétentes avant d'agir.

> **Défauts systémiques du modèle de dossier (hors score pays)**
> Ces anomalies touchent la plupart des 54 dossiers d'origine (erreurs de génération du modèle) et sont affichées séparément de la confiance propre à votre itinéraire :
> - [V01] 54 dossiers sur 54 partagent ce défaut : La ligne Fintech de la section 4 cite l'autorité de protection des données comme organisme d'agrément pour les paiements et le crédit au lieu de la banque centrale (54 dossiers sur 54). (source: cameroon.md §4, line 33; gabon.md §4, line 33)
> - [V02] 54 dossiers sur 54 partagent ce défaut : La ligne Énergie & industrie de la section 4 place un pourcentage dans l'emplacement prévu pour le régulateur de l'énergie (54 dossiers sur 54). (source: cameroon.md §4, line 38; gabon.md §4, line 38)
> - [V03] 54 dossiers sur 54 partagent ce défaut : Un pourcentage de la section 4 correspond au taux de TVA ou d'IS de la section 5 (valeur fiscale recopiée par erreur dans 54 dossiers sur 54). (source: cameroon.md §4, line 33; gabon.md §4, line 33)

## 0. Vue d'ensemble

- **Itinéraire:** Cameroon (Pays d'origine) -> Gabon (Pays cible) (source: cameroon.md, line 1); (source: gabon.md, line 1)
- **Secteur:** Fintech
- **Blocs partagés:** African Union (source: cameroon.md §1, line 13; gabon.md §1, line 13), CEMAC (source: cameroon.md §1, line 13; gabon.md §1, line 13)
- **Alertes « Vérifier d'abord » (pays & bloc):** 0 Élevée, 5 Moyenne, 0 Faible (5 total; bannière modèle: 3)
- **Fiabilité des données du dossier:** **Élevée** (0 Élevée, 5 Moyenne, 0 Faible) — Mesure uniquement la qualité des dossiers sources pour cet itinéraire (pays et bloc), jamais le risque juridique.

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

### Matrice de cohérence du bloc (CEMAC)

| Pays | Devise | Banque centrale | Symétrie blocs | Nom DPA | Champs à vérifier | Alertes | Source |
|---|---|---|---|---|---|---|---|
| Cameroon | `ok` XAF | `note` BEAC (full name) | `flag` V06 (ECOWAS (observer)) | `flag` V08 (CNPD mismatch) | `ok` 0 | `note` 0H/3M/0L (3) | (source: cameroon.md §1, line 12) |
| Central African Republic | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: central-african-republic.md §1, line 12) |
| Chad | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: chad.md §1, line 12) |
| Equatorial Guinea | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: equatorial-guinea.md §1, line 12) |
| Gabon | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V08 (CNPD mismatch) | `flag` 2 (§3,§5) | `note` 0H/3M/0L (3) | (source: gabon.md §1, line 12) |
| Congo (Republic) | `ok` XAF | `ok` BEAC | `ok` ok | `flag` V20 (unnamed) | `flag` 3 (§2,§3,§5) | `note` 0H/4M/0L (4) | (source: republic-of-congo.md §1, line 12) |

**Ce que cela signifie pour vous:** Appartenir à un même groupe régional (un accord entre États voisins sur la monnaie ou le commerce) simplifie certains échanges et paiements, mais ne supprime pas l'obligation de vous enregistrer dans le pays cible.

## 6. Points à vérifier en priorité

### Moyenne (5)
- **[V04 · PLACEHOLDER-S3]** (Portée: `country` | Origine: `in-dossier`): Le dossier Gabon contient un texte provisoire (« energy regulator: 'Ministry of Energy (verify current regulator)' ») en section 3. (source: gabon.md §3, line 25)
  - *Pourquoi c'est important:* Le dossier ne fournit pas un nom d'organisme ou un taux vérifié pour cette démarche.
  - *Qui interroger:* Vérifiez l'organisme ou le paramètre actuel sur le portail gouvernemental national ou auprès du ministère concerné.
- **[V04 · PLACEHOLDER-S5]** (Portée: `country` | Origine: `in-dossier`): Le dossier Gabon contient un texte provisoire (« investment promotion agency: 'Verify current agency' ») en section 5. (source: gabon.md §5, line 47)
  - *Pourquoi c'est important:* Le dossier ne fournit pas un nom d'organisme ou un taux vérifié pour cette démarche.
  - *Qui interroger:* Vérifiez l'organisme ou le paramètre actuel sur le portail gouvernemental national ou auprès du ministère concerné.
- **[V06 · BLOC-ASYMMETRY]** (Portée: `bloc` | Origine: `in-dossier`): Asymétrie d'appartenance régionale : Cameroon mentionne « ECOWAS (observer) » sans confirmation dans les dossiers partenaires du bloc. (source: cameroon.md §1, line 13)
  - *Pourquoi c'est important:* Un statut d'observateur ou une appartenance non confirmée n'accorde pas les avantages commerciaux ou d'agrément d'un membre à part entière.
  - *Qui interroger:* Ne vous appuyez pas sur ce bloc pour vos agréments ; confirmez l'adhésion officielle sur le registre du bloc.
- **[V08 · DPA-EXPANSION-MISMATCH]** (Portée: `bloc` | Origine: `in-dossier`): Même acronyme de protection des données (CNPD) avec des intitulés complets différents entre dossiers ('Commission Nationale pour la Protection des Données' (Gabon) vs 'Commission Nationale pour la Protection des Données à Caractère Personnel' (Cameroon)). (source: cameroon.md §2, line 21; gabon.md §2, line 21)
  - *Pourquoi c'est important:* Des intitulés contradictoires suggèrent un texte issu d'un modèle plutôt qu'une vérification directe dans le droit national.
  - *Qui interroger:* Confirmez le nom légal exact et le guichet actif de l'autorité de protection des données dans chaque pays.
- **[V10 · TAX-CIT-ANOMALY]** (Portée: `country` | Origine: `in-dossier`): Anomalie fiscale (CIT) dans le dossier Cameroon : « 30% (33% for some sectors) » (compound/multi-rate cell). (source: cameroon.md §5, line 44)
  - *Pourquoi c'est important:* Un taux multiple, hors plage ou non chiffré empêche une soustraction simple et peut fausser votre modèle financier.
  - *Qui interroger:* Confirmez le taux exact applicable à votre activité auprès de l'administration fiscale nationale.

**Ce que cela signifie pour vous:** Traitez en priorité les alertes les plus critiques avant toute dépense juridique ou dépôt officiel : elles signalent des informations contradictoires ou manquantes dans les dossiers sources.

## Nos vérifications externes (non vérifié)

Les points ci-dessous reposent sur des connaissances extérieures aux dossiers (jamais présentés comme des faits issus des dossiers). Statut : non vérifié tant qu'une source officielle n'est pas jointe.

- **[EXT-01]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Dans la zone CEMAC, l'agrément et la supervision des banques et établissements de paiement impliquent un superviseur bancaire régional aux côtés de la BEAC et des ministères des Finances ; aucun superviseur bancaire régional n'est cité dans les dossiers CEMAC.
- **[EXT-02]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Vérifier si le Cameroun dispose réellement d'un statut d'observateur auprès de la CEDEAO ; le Cameroun est membre de la CEMAC et ce statut n'est pas confirmé par les dossiers partenaires.
- **[EXT-03]** (Statut: `non vérifié` | URL source: aucune URL enregistrée): Vérifier l'autorité nationale de protection des données actuellement opérationnelle dans les deux pays plutôt que de s'appuyer sur les intitulés CNPD divergents figurant dans les dossiers.
