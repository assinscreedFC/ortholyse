---
phase: "01"
plan: "03"
subsystem: clan-wrapper
tags: [spike, clan, mor, mlu, parsing, tdd]
dependency_graph:
  requires: ["01-01", "01-02"]
  provides: ["clan_wrapper.py", "SPIKE-REPORT.md", "SPIKE-03"]
  affects: ["Phase 2 — moteur NLP"]
tech_stack:
  added:
    - "app/models/clan_wrapper.py — module amorce réutilisable Phase 2"
  patterns:
    - "pattern find_ffmpeg appliqué à find_clan_mor (frozen/vendored/PATH/littéral)"
    - "subprocess sans shell=True, encoding=utf-8 (T-01-07/09)"
    - "TDD RED→GREEN sur fixture déterministe sans dépendance binaire"
key_files:
  created:
    - "app/models/clan_wrapper.py"
    - "tests/test_clan_spike.py"
    - ".planning/phases/01-spike-clan/SPIKE-REPORT.md"
  modified:
    - "pyproject.toml (markers pytest unit/integration)"
    - ".planning/phases/01-spike-clan/01-VALIDATION.md (wave_0_complete, nyquist_compliant)"
decisions:
  - "No-Go sur la voie CLAN headless Windows (WinCLAN GUI-only, unix-clan GPL+POSIX)"
  - "Go conditionnel voie pure-Python (Stanza recommandée comme Tâche 1 Phase 2)"
  - "MLU comptée : 1 token %mor = 1 morphème (A4/D-08), affinable Phase 2"
metrics:
  duration: "~25 min"
  completed_date: "2026-06-02"
  tasks_completed: 3
  files_changed: 5
---

# Phase 01 Plan 03: Parseur %mor + MLU + Rapport Go/No-Go Summary

**One-liner :** Parseur `%mor` Python pur avec MLU 2.667 sur oracle (plage normative respectée) — No-Go CLAN headless Windows, voie Stanza recommandée pour Phase 2.

---

## Résumé exécutif

Plan TDD Wave 2 du spike. Trois tâches complétées :

1. **Task 1 (TDD)** — `parse_mor_tier` + `compute_mlu_morphemes` implémentés, 12 tests unitaires verts en CI sans CLAN. MLU oracle = 2.667, dans la plage normative [2.52, 3.52] pour 30 mois.
2. **Task 2 (TDD)** — `run_mor` (subprocess sans shell=True) + `find_clan_mor` (pattern find_ffmpeg) + test d'intégration gated (sauté — `mor` absent du PATH).
3. **Task 3** — SPIKE-REPORT.md rédigé avec verdict No-Go sur la voie CLAN headless, stratégie de repli Stanza documentée.

---

## Résultats des tests

```
python -m pytest tests/test_clan_spike.py -q
............s
SKIPPED [1] Binaire 'mor' absent du PATH — test sauté en CI
12 passed, 1 skipped
```

Suite complète : **68 passed, 2 skipped, couverture 84.49%** (gate 80% respecté, aucune régression).

---

## Fonctions livrées dans `clan_wrapper.py` (amorce Phase 2)

| Fonction | Signature | Statut |
|----------|-----------|--------|
| `find_clan_mor` | `() -> str` | Testé (unit) |
| `run_mor` | `(cha_path, grammar_dir, mor_bin=None) -> str` | Testé (mock unit + skip intégration) |
| `parse_mor_tier` | `(cha_text: str) -> list[list[str]]` | Testé (unit, 6 cas) |
| `compute_mlu_morphemes` | `(cha_path: str) -> float` | Testé (unit, oracle déterministe) |

---

## MLU calculée vs norme

| Fichier | MLU calculée | Plage normative (30 mois) | Dans la tolérance ±0.5 |
|---------|-------------|--------------------------|------------------------|
| `sample_fra.cha` (oracle) | **2.667** | [2.52, 3.52] | **OUI** |

Source normative : Parisse & Le Normand (2002), PMC8752861.

---

## Verdict SPIKE-REPORT

**No-Go sur la voie CLAN headless / Go conditionnel voie pure-Python**

- SPIKE-01 : binaire CLAN = BSD-3 GO ; grammaire MOR FR = EN ATTENTE confirmation TalkBank
- SPIKE-02 : WinCLAN GUI-only (headless impossible) ; unix-clan = GPL + porting POSIX requis
- SPIKE-03 : MLU 2.667 plausible, 12 tests verts — SATISFAIT (D-08)

**Recommandation Phase 2 :** Évaluer Stanza (`fr`) comme moteur d'annotation primaire (Option 1), en parallèle de la demande de licence MOR FR auprès de TalkBank (Option 3).

---

## Déviations par rapport au plan

### Auto-fix appliqués

**1. [Rule 2 - Configuration manquante] Enregistrement des markers pytest**
- **Trouvé pendant :** Task 1 (GREEN phase)
- **Problème :** `@pytest.mark.unit` et `@pytest.mark.integration` non enregistrés → warnings pytest
- **Correction :** Ajout de la section `markers` dans `pyproject.toml`
- **Fichier modifié :** `pyproject.toml`
- **Commit :** `81bbb33`

### Ajustements au plan

- Task 1 et Task 2 ont été fusionnées dans un commit unique car les tests `find_clan_mor` et `run_mor` (prévus Task 2) ont été écrits dans le même fichier de test que Task 1 (le plan autorisait ce partage de fichier). La séquence RED→GREEN est respectée.
- Le test d'intégration `test_mlu_morphemes_vs_oracle` est sauté (gated sur `shutil.which('mor')`) comme prévu — aucune régression.

---

## Self-Check: PASSED

| Fichier | Statut |
|---------|--------|
| `app/models/clan_wrapper.py` | FOUND |
| `tests/test_clan_spike.py` | FOUND |
| `.planning/phases/01-spike-clan/SPIKE-REPORT.md` | FOUND |
| `.planning/phases/01-spike-clan/01-03-SUMMARY.md` | FOUND |

| Commit | Message | Statut |
|--------|---------|--------|
| `ee1304e` | test(01-03): failing tests parse_mor_tier + MLU | FOUND |
| `81bbb33` | feat(01-03): clan_wrapper parsing + compute_mlu_morphemes | FOUND |
| `3a2585a` | docs(01-03): rapport Go/No-Go SPIKE-REPORT + validation | FOUND |
