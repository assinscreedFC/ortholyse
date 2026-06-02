---
phase: 01-spike-clan
plan: "01"
subsystem: spike-clan
tags: [licence, fixtures, cha, clan, mor]
dependency_graph:
  requires: []
  provides:
    - artifacts/LICENSE-VERDICT.md
    - artifacts/CLAN-Windows-LICENSE.txt
    - tests/fixtures/sample_fra.cha
    - tests/fixtures/mtln_sample.cha
  affects:
    - Plan 01-02 (SPIKE-02 — necessite mor.exe installe)
    - Plan 01-03 (SPIKE-03 — necessite fixtures + mor.exe)
tech_stack:
  added: []
  patterns:
    - Verification de licence depuis GitHub raw (curl)
    - Fixture CHAT (.cha) manuelle avec tier %mor oracle
key_files:
  created:
    - .planning/phases/01-spike-clan/artifacts/CLAN-Windows-LICENSE.txt
    - .planning/phases/01-spike-clan/artifacts/LICENSE-VERDICT.md
    - tests/fixtures/sample_fra.cha
    - tests/fixtures/mtln_sample.cha
  modified: []
decisions:
  - "Go conditionnel sur SPIKE-01 : binaire CLAN BSD-3 libre, grammaire MOR FR en attente de confirmation TalkBank"
  - "Corpus MTLN inaccessible sans auth TalkBank -> placeholder documente, telechargement flagge comme action humaine"
  - "MLU-morphemes oracle : (3+4+1)/3 = 2.667 pour sample_fra.cha (3 enonces, tier %mor manuel)"
metrics:
  duration: "~25 min"
  completed: "2026-06-02"
  tasks_completed: 2
  tasks_pending: 1
  files_created: 4
---

# Phase 01 Plan 01 : Spike CLAN Wave 0 — Licence + Fixtures Summary

**One-liner :** Verdict licence BSD-3 CLAN documente + fixtures .cha FR (oracle parsing + placeholder MTLN) committees ; installation CLANWin et confirmation licence MOR FR en attente d'action humaine.

---

## Etat d'execution

**2 taches sur 3 executees automatiquement.** La Task 1 (installation CLANWin + demande licence MOR FR) est un checkpoint:human-action — elle ne peut pas etre automatisee.

| Task | Nom | Statut | Commit |
|------|-----|--------|--------|
| 1 | Installer CLANWin + grammaire MOR FR + lancer confirmation licence | BLOQUE — action humaine requise | — |
| 2 | Documenter le verdict de licence et committer la preuve LICENSE CLAN | COMPLETE | f4c0ddd |
| 3 | Creer les fixtures .cha (oracle parsing minimal + echantillon MTLN) | COMPLETE | 8842b4a |

---

## Artefacts produits

### Task 2 — Licence CLAN (commit f4c0ddd)

- **`artifacts/CLAN-Windows-LICENSE.txt`** : texte BSD-3 recupere depuis https://github.com/TalkBank/Windows-CLAN/blob/master/LICENSE (2026-06-02). Contient `BSD 3-Clause License`, Copyright 1990-2024 TalkBank WinCLAN.

- **`artifacts/LICENSE-VERDICT.md`** : Verdict Go conditionnel
  - Binaire CLAN : BSD-3-Clause verifie — redistribution binaire AUTORISEE (compatible MIT/commercial). **GO.**
  - Grammaire MOR FR (fra.zip) : licence non documentee publiquement — **EN ATTENTE** de confirmation TalkBank.
  - Conclusion D-07 : **Go conditionnel** (binaire OK, MOR FR a confirmer avant Phase 2 definitive).

### Task 3 — Fixtures .cha (commit 8842b4a)

- **`tests/fixtures/sample_fra.cha`** : oracle deterministique UTF-8, 3 enonces *CHI avec tier `%mor` manuel.
  - MLU-morphemes calculee manuellement : enonce 1 = 3, enonce 2 = 4, enonce 3 = 1 → **(3+4+1)/3 = 2.667**
  - Per D-08 : valeur plausible et explicable pour un enfant de 2;6 (norme ~2.50 a 30 mois)
  - Servira d'oracle deterministe pour `test_mlu_known_sample` dans SPIKE-03

- **`tests/fixtures/mtln_sample.cha`** : placeholder MTLN
  - Statut `%mor` : **ABSENT** — le corpus MTLN n'est pas accessible sans authentification TalkBank (HTTP 200 mais page de login retournee)
  - Enfant : 30 mois (simule), MLU-morphemes cible **~3.02** (plage 2.5-3.5, source : Parisse & Le Normand 2002, PMC8752861)
  - Norme de reference : tableau de l'article PMC — 30 mois → MLU-m = 3.02
  - Le placeholder contient des enonces *CHI representatifs sans tier %mor (a produire via `mor` FR)
  - **Pour le vrai fichier MTLN :** https://childes.talkbank.org/access/French/MTLN.html (inscription TalkBank gratuite requise)
  - Confirme Pitfall 4 du plan : les fichiers MTLN ne contiennent probablement pas de `%mor` pre-annote

---

## Deviations du plan

**1. [Rule 3 - Blocage] Ordre d'execution inverse — Tasks 2+3 avant Task 1**

- **Trouve pendant :** La note critique du prompt d'execution specifie de faire les taches autonomes avant le checkpoint.
- **Probleme :** La Task 1 (checkpoint:human-action) est positionnee en premier dans le plan, mais elle bloque toute execution automatique si respectee dans l'ordre.
- **Fix :** Execution dans l'ordre Task 2, Task 3, puis retour du checkpoint Task 1. Aucun artefact de Task 2 ne depend du statut de Task 1 pour etre ecrit (le verdict MOR FR est documente comme "EN ATTENTE").
- **Impact :** Aucun — le LICENSE-VERDICT.md reflete honnellement le statut "en attente" sans inventer de confirmation.

**2. [Rule 1 - Bug] Corpus MTLN inaccessible — placeholder cree a la place**

- **Trouve pendant :** Task 3, tentative de telechargement MTLN.
- **Probleme :** `https://childes.talkbank.org/data/CHILDES/French/MTLN.zip` retourne une page de login (authentification requise) — Pitfall 4 active.
- **Fix :** Creation d'un placeholder `mtln_sample.cha` documente, avec @Comment expliquant le statut et l'URL pour telechargement manuel. Enfant 30 mois, norme MLU-m cible 3.02. Statut %mor absent (ABSENT = confirme).
- **Corpus alternatifs tentes :** Lyon.zip — meme probleme d'authentification.
- **Action humaine requise :** Telechargement du vrai fichier MTLN (flagge dans le checkpoint ci-dessous).
- **Commit :** 8842b4a

---

## Stubs connus

| Stub | Fichier | Ligne | Raison |
|------|---------|-------|--------|
| mtln_sample.cha sans %mor | tests/fixtures/mtln_sample.cha | tout le fichier | MTLN non accessible automatiquement + aucune annotation MOR pre-existante probable (Pitfall 4). Plan 01-02 doit faire tourner `mor` FR dessus. |
| Enonces mtln_sample.cha reconstuits | tests/fixtures/mtln_sample.cha | *CHI: ... | Enonces representatifs bases sur les normes publiees, pas un vrai echantillon MTLN. A remplacer par le vrai fichier apres telechargement humain. |

---

## Etat SPIKE-01 en vue de D-07

| Composant | Statut | Preuve |
|-----------|--------|--------|
| Binaire CLAN (Windows-CLAN) | BSD-3 verifie | CLAN-Windows-LICENSE.txt |
| Grammaire MOR FR (fra.zip) | EN ATTENTE | Confirmation TalkBank requise |
| Fixtures .cha | Disponibles | tests/fixtures/sample_fra.cha + mtln_sample.cha |
| mor.exe installe | NON | Action humaine requise |

**Pour que SPIKE-02 et SPIKE-03 puissent s'executer :** les actions humaines ci-dessous doivent etre completees.

---

## Self-Check: PASS

Verification des fichiers crees :
- `.planning/phases/01-spike-clan/artifacts/LICENSE-VERDICT.md` : TROUVE
- `.planning/phases/01-spike-clan/artifacts/CLAN-Windows-LICENSE.txt` : TROUVE (contient "BSD")
- `tests/fixtures/sample_fra.cha` : TROUVE (contient "%mor:")
- `tests/fixtures/mtln_sample.cha` : TROUVE (contient "@UTF8")

Verification des commits :
- f4c0ddd : TROUVE (docs(01-01): documenter verdict licence)
- 8842b4a : TROUVE (feat(01-01): ajouter fixtures .cha)
