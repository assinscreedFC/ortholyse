# Ortholyse

## What This Is

Application desktop (Python / PySide6, 100 % locale) pour orthophonistes francophones. Le cœur du produit est **l'analyse d'échantillon de langage (LSA)** : à partir d'une transcription de séance, l'outil calcule les indicateurs linguistiques d'un bilan (MLU, morphèmes, diversité lexicale, complexité syntaxique, temps/modes verbaux). La transcription audio (Whisper local) est une commodité d'entrée, pas la valeur centrale.

Positionnement : **« le LSA convivial que CLAN ne sait pas rendre utilisable »**. CLAN/CHILDES fait déjà l'analyse de référence mais reste imbuvable pour un clinicien en cabinet ; Orthonie/myCR couvrent la dictée de compte-rendu (marché distinct, déjà pris). Le trou réel : l'analyse de la production du patient avec une UX accessible, en français.

## Core Value

Un orthophoniste obtient des **indicateurs de bilan fiables (alignés sur les standards CLAN/MOR)** à partir d'une transcription, **sans rien installer ni configurer de technique**. Si tout le reste échoue, c'est ça qui doit marcher.

## Requirements

### Validated

<!-- Capacités existantes inférées de la carte du codebase (.planning/codebase/). -->

- ✓ Transcription audio locale via Whisper (offline, RGPD) — existing
- ✓ Enregistrement micro + import de fichiers audio dans l'app — existing
- ✓ Correction de transcription avec lecture audio synchronisée (mapping mot↔timestamp) — existing
- ✓ Calcul de métriques linguistiques de base (MLU/MLCU, comptage morphèmes, mots uniques) — existing, **fiabilité à refondre**
- ✓ Export PDF (transcription + métriques) — existing
- ✓ Pipeline FR spaCy `fr_core_news_lg` + NLTK — existing
- ✓ Archi MVC (Views / Controllers / Models / Widgets), suite pytest avec gate 80 % — existing

### Active

<!-- Objectifs de la refonte. Hypothèses jusqu'à validation. -->

**Moteur d'analyse (cœur)**
- [ ] Remplacer le moteur maison (`Analyse_NLTK.morphem()`, heuristique JSON+stemmer) par un moteur adossé à **CLAN + grammaire MOR française embarqués et invisibles** (sous-process)
- [ ] Adopter le format **CHAT (.cha)** comme pivot interne et format d'export interopérable
- [ ] Segmentation en énoncés adaptée à l'oral (remplacer `nltk.sent_tokenize`), corrigeable manuellement
- [ ] Set de métriques V1 : MLU mots + morphèmes, TTR / diversité lexicale, complexité syntaxique, temps & modes verbaux

**Entrée & workflow**
- [ ] Entrée texte directe (coller / importer une transcription sans audio)
- [ ] Conserver le pipeline audio Whisper existant (l'analyse marche avec ou sans audio)

**Usage clinique réel**
- [ ] Dossier patient local (persistance chiffrée, RGPD), historique de séances, suivi longitudinal
- [ ] Présentation des métriques avec repères développementaux indicatifs (Parisse/Le Normand, HAS)
- [ ] Distribution end-user : installeur 1 clic (CLAN + MOR FR + FFmpeg embarqués, modèle Whisper téléchargé au 1er lancement) — zéro ligne de commande

**Dérisquage**
- [ ] Phase 0 : spike de faisabilité CLAN embarqué (licence CLAN/TalkBank pour redistribution + appel `mor` FR en CLI + parsing du tier `%mor`)

### Out of Scope

- **Compte-rendu opposable / conformité nomenclature avenant 21** — V1 est un outil d'analyse / aide à la décision, pas un CRBO opposable ; conformité = chantier réglementaire prématuré, terrain déjà occupé par Orthonie/myCR
- **Concurrencer la dictée→compte-rendu** — marché distinct et déjà pris ; la transcription n'est pas le différenciateur
- **Public adulte / aphasie** — reporté en V2 (set de métriques façon EVAL/AphasiaBank + second référentiel de normes)
- **Fine-tuning d'un modèle spaCy sur corpus annoté** — fausse priorité ; les ressources validées (CLAN/MOR, Démonette) couvrent le besoin sans entraînement ni constitution de corpus
- **Réécriture from scratch** — refonte incrémentale ; l'archi MVC et la synchro audio/transcript sont des acquis à conserver

## Context

- **Codebase existant** (~5k lignes Python) cartographié dans `.planning/codebase/`. Archi MVC saine, synchro audio/transcript de valeur, suite de tests avec gate 80 %.
- **Concurrence** : CLAN/CHILDES (gratuit, standard académique, austère) = concurrent fonctionnel et socle technique ; SALT (commercial, anglophone) ; Exalang/Examath/GréMots (batteries de tests normés, pas du LSA spontané) ; Orthonie/myCR/HappyScribe (dictée→CR, marché distinct).
- **Ressources de référence** : CLAN + commande MOR (MLU morphèmes auto), grammaire MOR française (Christophe Parisse, MoDyCo/CNRS), Démonette-2 (morphologie dérivationnelle FR, applicable aux troubles du langage), treebanks UD French. CLAN est open source (GitHub).
- **Dette narrative** : 17 posts de diffusion publient le message « besoin = corpus annoté pour fine-tuner spaCy ». La refonte invalide cette priorité ; à assumer publiquement (bon sujet de contenu : « pourquoi j'ai abandonné l'entraînement IA pour les standards existants »).
- **Réception** : posts Reddit/Facebook diffusés ; retours surtout côté code pour l'instant, pas encore d'orthophonistes utilisateurs.

## Constraints

- **Tech stack** : Python 3.12+, PySide6 (Qt), refonte incrémentale — pas de changement de techno
- **Offline / RGPD** : tout reste sur le poste, zéro cloud, aucune donnée patient en télémétrie ni en logs
- **Dépendances embarquées** : CLAN + grammaire MOR FR + FFmpeg doivent être packagés de façon invisible pour l'utilisateur final
- **Licence** : projet MIT ; vérifier la licence CLAN/TalkBank avant de redistribuer les binaires (bloquant Phase 0)
- **Cible non technique** : orthophonistes libéraux sans support IT ni ligne de commande
- **Qualité** : maintenir le gate de couverture 80 % sur les modules métier

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Cœur = analyse (LSA), pas transcription | La transcription est une commodité déjà couverte (Orthonie/myCR) ; la valeur unique est l'analyse conviviale que CLAN ne rend pas utilisable | — Pending |
| Moteur = CLAN + MOR FR embarqués, invisibles | Réutiliser un moteur validé/standard plutôt que réinventer une heuristique fragile ; UX Ortholyse par-dessus | — Pending |
| Format pivot CHAT (.cha) | Interopérabilité et crédibilité (format reconnu, citable) | — Pending |
| Public enfant V1, adulte/aphasie V2 | « Les deux » en séquence pour ne pas diluer le MVP ; l'enfant correspond à l'existant (MLU/morphèmes) | — Pending |
| Statut outil d'analyse, non opposable | Évite le chantier réglementaire et la concurrence frontale ; suffisant pour l'adoption initiale | — Pending |
| Refonte incrémentale + réécriture ciblée du moteur | Garder l'acquis (MVC, synchro audio, UI) ; seul `Analyse_NLTK.py` se remplace | — Pending |
| Abandon du fine-tuning / corpus annoté | Ressources existantes (CLAN/MOR, Démonette) couvrent le besoin ; le vrai blocage est la validation et le packaging, pas la data | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-06-02 after initialization*
