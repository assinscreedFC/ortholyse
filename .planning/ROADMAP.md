# Roadmap: Ortholyse

## Overview

Refonte incrémentale d'une application desktop d'analyse de langage (LSA) pour orthophonistes francophones. Le chemin commence par valider la faisabilité technique du cœur (CLAN embarqué), passe par la construction du moteur d'analyse fiable, enrichit l'expérience clinique (dossier patient, métriques normées), puis finalise la distribution one-click. Chaque phase livre une capacité complète et vérifiable ; l'architecture MVC existante et la synchronisation audio/transcript sont préservées.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Spike CLAN** - Valider la faisabilité du moteur CLAN embarqué (licence + `mor` FR + parsing `%mor`) (completed 2026-06-02)
- [ ] **Phase 2: Moteur d'analyse** - Remplacer le moteur heuristique fragile par le pipeline CLAN/CHAT/MOR
- [ ] **Phase 3: Métriques et affichage** - Exposer les 6 métriques V1 avec repères développementaux
- [ ] **Phase 4: Entrée et dossier patient** - Ajouter l'entrée texte directe et le dossier patient chiffré
- [ ] **Phase 5: Restitution** - Consolider l'affichage des résultats et les exports (PDF + CHAT)
- [ ] **Phase 6: Distribution** - Empaqueter CLAN/MOR/FFmpeg et produire un installeur 1-clic

## Phase Details

### Phase 1: Spike CLAN
**Goal**: L'équipe sait si CLAN + grammaire MOR française peuvent être embarqués et redistribués — avant d'investir dans le moteur
**Depends on**: Nothing (first phase)
**Requirements**: SPIKE-01, SPIKE-02, SPIKE-03
**Success Criteria** (what must be TRUE):
  1. La licence CLAN/TalkBank est documentée avec une conclusion claire (redistribution autorisée ou non)
  2. La commande `mor` avec la grammaire MOR française tourne sur un `.cha` de test et produit un tier `%mor` lisible
  3. Un script Python parse la sortie CLAN et calcule une MLU en morphèmes vérifiable sur un échantillon de référence connu
  4. Un rapport de spike écrit indique "Go" ou "No-Go" avec la stratégie de remplacement si No-Go
**Plans**: 3 plans
Plans:
- [x] 01-01-PLAN.md — Wave 0 : licence CLAN/MOR FR (SPIKE-01) + install CLANWin + fixtures .cha
- [x] 01-02-PLAN.md — Wave 1 : exécution headless de mor FR -> tier %mor (SPIKE-02)
- [x] 01-03-PLAN.md — Wave 2 : wrapper Python + parsing %mor + MLU morphèmes vs oracle MTLN + rapport Go/No-Go (SPIKE-03)

### Phase 2: Moteur d'analyse
**Goal**: Le pipeline CLAN/CHAT/MOR remplace l'heuristique fragile — la transcription corrigée produit des métriques linguistiques fiables
**Depends on**: Phase 1 (spike Go)
**Requirements**: ENGINE-01, ENGINE-02, ENGINE-03, ENGINE-04, ENGINE-05
**Success Criteria** (what must be TRUE):
  1. L'utilisateur peut corriger les frontières d'énoncés manuellement avant analyse
  2. Un fichier `.cha` valide est généré automatiquement depuis la transcription corrigée, sans intervention de l'utilisateur
  3. CLAN + grammaire MOR FR tournent en sous-process transparent — l'utilisateur ne voit aucune fenêtre de terminal ni étape technique
  4. L'ancien moteur (`Analyse_NLTK.morphem()`, JSON + stemmer) n'existe plus dans la codebase
  5. Les sorties CLAN sont parsées et disponibles sous forme de métriques structurées exploitables par l'UI
**Plans**: TBD
**UI hint**: yes

### Phase 3: Métriques et affichage
**Goal**: L'orthophoniste voit les 6 métriques V1 avec leurs repères développementaux — le cœur clinique du produit est utilisable
**Depends on**: Phase 2
**Requirements**: METRIC-01, METRIC-02, METRIC-03, METRIC-04, METRIC-05, METRIC-06
**Success Criteria** (what must be TRUE):
  1. L'utilisateur voit la MLU en mots et la MLU en morphèmes (via MOR) dans l'interface après analyse
  2. L'utilisateur voit la diversité lexicale (TTR, types, tokens, mots uniques)
  3. L'utilisateur voit des indices de complexité syntaxique et la répartition des temps/modes verbaux
  4. Chaque métrique affiche un repère développemental indicatif (Parisse/Le Normand, HAS) directement lisible par un clinicien
**Plans**: TBD
**UI hint**: yes

### Phase 4: Entrée et dossier patient
**Goal**: L'orthophoniste peut analyser sans audio et gérer ses patients avec persistance chiffrée — le workflow clinique réel est couvert
**Depends on**: Phase 2 (moteur opérationnel), Phase 1 (pipeline audio existant préservé)
**Requirements**: INPUT-01, INPUT-02, INPUT-03, PATIENT-01, PATIENT-02, PATIENT-03
**Success Criteria** (what must be TRUE):
  1. L'utilisateur peut coller ou importer une transcription texte brute et lancer l'analyse sans fournir d'audio
  2. Le pipeline audio Whisper existant (enregistrement + import + correction synchronisée) fonctionne tel quel après refonte
  3. L'utilisateur peut créer un dossier patient, y associer des séances et retrouver l'historique entre deux sessions
  4. Les données patients sont stockées chiffrées localement — aucune donnée sensible n'apparaît en clair sur disque ou dans les logs
  5. L'utilisateur peut comparer les métriques d'un patient sur plusieurs bilans successifs
**Plans**: TBD
**UI hint**: yes

### Phase 5: Restitution
**Goal**: L'orthophoniste peut présenter et exporter les résultats d'analyse dans un format utilisable en cabinet
**Depends on**: Phase 3 (métriques disponibles), Phase 4 (dossier patient disponible)
**Requirements**: REPORT-01, REPORT-02, REPORT-03
**Success Criteria** (what must be TRUE):
  1. L'utilisateur voit un tableau de métriques lisible et bien organisé après chaque analyse
  2. L'utilisateur peut exporter un PDF contenant la transcription et les métriques, prêt à archiver
  3. L'utilisateur peut exporter le fichier `.cha` interopérable (format CLAN standard)
**Plans**: TBD
**UI hint**: yes

### Phase 6: Distribution
**Goal**: N'importe quel orthophoniste peut installer et lancer Ortholyse sans ligne de commande — CLAN, MOR, FFmpeg et Whisper sont invisibles
**Depends on**: Phase 5 (application complète)
**Requirements**: DIST-01, DIST-02, DIST-03
**Success Criteria** (what must be TRUE):
  1. L'utilisateur installe l'application en double-cliquant sur un installeur (Windows et/ou macOS), sans ouvrir de terminal
  2. CLAN, la grammaire MOR française et FFmpeg sont embarqués dans l'installation et fonctionnent sans configuration manuelle
  3. Au premier lancement, le modèle Whisper se télécharge automatiquement avec une barre de progression visible — aucune commande requise
**Plans**: TBD

## Progress

**Execution Order:**
Phases exécutées dans l'ordre numérique : 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Spike CLAN | 3/3 | Complete    | 2026-06-02 |
| 2. Moteur d'analyse | 0/TBD | Not started | - |
| 3. Métriques et affichage | 0/TBD | Not started | - |
| 4. Entrée et dossier patient | 0/TBD | Not started | - |
| 5. Restitution | 0/TBD | Not started | - |
| 6. Distribution | 0/TBD | Not started | - |
