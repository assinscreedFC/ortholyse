# Requirements: Ortholyse

**Defined:** 2026-06-02
**Core Value:** Un orthophoniste obtient des indicateurs de bilan fiables (alignés CLAN/MOR) à partir d'une transcription, sans rien installer ni configurer de technique.

## v1 Requirements

### Spike — Dérisquage (Phase 0)

- [ ] **SPIKE-01**: Vérifier que la licence CLAN/TalkBank autorise la redistribution des binaires CLAN dans l'application
- [ ] **SPIKE-02**: Appeler `mor` avec la grammaire MOR française en CLI sur un `.cha` de test et obtenir le tier `%mor`
- [ ] **SPIKE-03**: Parser la sortie CLAN (`%mor` + `mlu`) et valider une MLU en morphèmes sur un échantillon de référence

### Moteur d'analyse

- [ ] **ENGINE-01**: Le système génère un fichier CHAT (`.cha`) valide depuis une transcription corrigée (locuteurs, énoncés)
- [ ] **ENGINE-02**: Le système segmente la transcription en énoncés adaptés à l'oral, et l'utilisateur peut corriger manuellement les frontières d'énoncés
- [ ] **ENGINE-03**: Le système orchestre CLAN + grammaire MOR FR embarqués en sous-process, sans intervention de l'utilisateur
- [ ] **ENGINE-04**: Le système parse les sorties CLAN en métriques structurées exploitables par l'UI
- [ ] **ENGINE-05**: L'ancien moteur heuristique (`Analyse_NLTK.morphem()`, listes JSON + stemmer) est retiré

### Métriques

- [ ] **METRIC-01**: L'utilisateur voit la MLU en mots
- [ ] **METRIC-02**: L'utilisateur voit la MLU en morphèmes (via MOR)
- [ ] **METRIC-03**: L'utilisateur voit la diversité lexicale (TTR, types, tokens, mots uniques)
- [ ] **METRIC-04**: L'utilisateur voit des indices de complexité syntaxique
- [ ] **METRIC-05**: L'utilisateur voit la répartition des temps et modes verbaux
- [ ] **METRIC-06**: Chaque métrique est affichée avec un repère développemental indicatif (Parisse/Le Normand, HAS)

### Entrée

- [ ] **INPUT-01**: L'utilisateur peut coller ou importer une transcription texte directement, sans fournir d'audio
- [ ] **INPUT-02**: L'utilisateur peut enregistrer/importer un audio et obtenir une transcription Whisper locale (pipeline existant conservé)
- [ ] **INPUT-03**: L'utilisateur peut corriger la transcription avec lecture audio synchronisée (mécanisme existant conservé)

### Dossier patient

- [ ] **PATIENT-01**: L'utilisateur peut créer et gérer des dossiers patients
- [ ] **PATIENT-02**: Les séances et bilans sont persistés par patient localement, de façon chiffrée (RGPD)
- [ ] **PATIENT-03**: L'utilisateur peut comparer les bilans d'un patient dans le temps (suivi longitudinal)

### Restitution

- [ ] **REPORT-01**: L'utilisateur voit un tableau de métriques lisible après analyse
- [ ] **REPORT-02**: L'utilisateur peut exporter un PDF (transcription + métriques)
- [ ] **REPORT-03**: L'utilisateur peut exporter au format CHAT (`.cha`) interopérable

### Distribution

- [ ] **DIST-01**: L'utilisateur installe l'application en 1 clic (Windows/macOS), sans ligne de commande
- [ ] **DIST-02**: CLAN + grammaire MOR FR + FFmpeg sont embarqués de façon invisible dans l'installation
- [ ] **DIST-03**: Le modèle Whisper est téléchargé au premier lancement avec une barre de progression

## v2 Requirements

### Public adulte / aphasie

- **ADULT-01**: Set de métriques adapté à l'aphasie (densité informative, fluence, manque du mot) façon EVAL/AphasiaBank
- **ADULT-02**: Second référentiel de normes adulte

### Analyse avancée

- **ADV-01**: Comparaison côte à côte de plusieurs séances/patients
- **ADV-02**: Traitement par lot de plusieurs séances
- **ADV-03**: Modèles de rapport configurables

## Out of Scope

| Feature | Reason |
|---------|--------|
| Compte-rendu opposable / conformité avenant 21 | V1 = outil d'analyse, pas CRBO opposable ; chantier réglementaire prématuré, terrain pris (Orthonie/myCR) |
| Concurrencer la dictée→compte-rendu | Marché distinct déjà pris ; la transcription n'est pas le différenciateur |
| Fine-tuning spaCy sur corpus annoté | Fausse priorité ; CLAN/MOR + Démonette couvrent le besoin sans entraînement |
| Réécriture from scratch | Refonte incrémentale ; MVC + synchro audio/transcript sont des acquis |
| Cloud / télémétrie | Offline-first, données patient strictement locales (RGPD) |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SPIKE-01 | Phase 1 | Pending |
| SPIKE-02 | Phase 1 | Pending |
| SPIKE-03 | Phase 1 | Pending |
| ENGINE-01 | Phase 2 | Pending |
| ENGINE-02 | Phase 2 | Pending |
| ENGINE-03 | Phase 2 | Pending |
| ENGINE-04 | Phase 2 | Pending |
| ENGINE-05 | Phase 2 | Pending |
| METRIC-01 | Phase 3 | Pending |
| METRIC-02 | Phase 3 | Pending |
| METRIC-03 | Phase 3 | Pending |
| METRIC-04 | Phase 3 | Pending |
| METRIC-05 | Phase 3 | Pending |
| METRIC-06 | Phase 3 | Pending |
| INPUT-01 | Phase 4 | Pending |
| INPUT-02 | Phase 4 | Pending |
| INPUT-03 | Phase 4 | Pending |
| PATIENT-01 | Phase 4 | Pending |
| PATIENT-02 | Phase 4 | Pending |
| PATIENT-03 | Phase 4 | Pending |
| REPORT-01 | Phase 5 | Pending |
| REPORT-02 | Phase 5 | Pending |
| REPORT-03 | Phase 5 | Pending |
| DIST-01 | Phase 6 | Pending |
| DIST-02 | Phase 6 | Pending |
| DIST-03 | Phase 6 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Mapped to phases: 24 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-02*
*Last updated: 2026-06-02 after roadmap creation (traceability complete)*
