---
phase: 01-spike-clan
plan: "02"
subsystem: spike-clan
tags: [mor, clan, headless, cli, gpl, mingw]
dependency_graph:
  requires:
    - tests/fixtures/sample_fra.cha
  provides:
    - artifacts/MOR-CLI-TRIAL.md
  affects:
    - Plan 01-03 (SPIKE-03 — informe la résolution binaire + le verdict du rapport)
tech_stack:
  added: []
  patterns:
    - Investigation CLI headless en direct (subprocess + timeout)
    - Tentative de compilation unix-clan via MinGW
key_files:
  created:
    - .planning/phases/01-spike-clan/artifacts/MOR-CLI-TRIAL.md
  modified:
    - .planning/phases/01-spike-clan/artifacts/LICENSE-VERDICT.md
decisions:
  - "WinCLAN (CLAN.EXE) est GUI-only — mor ne tourne PAS en headless via CLI"
  - "Headless mor = seulement via unix-clan (GPL) à compiler ; build POSIX→Windows bloquant sous MinGW (sgtty.h/sys/ioctl.h/curses absents)"
  - "Aucun env POSIX dispo (MSYS2/Cygwin absents, WSL Ubuntu en désinstallation)"
metrics:
  duration: "~session interactive (orchestrateur)"
  completed: "2026-06-02"
  tasks_completed: 2
  tasks_pending: 0
  files_created: 1
---

# Phase 01 Plan 02 : Spike CLAN Wave 1 — Essai `mor` headless Summary

**One-liner :** Investigation menée en direct sur la machine Windows cible : CLAN installé, grammaire MOR FR téléchargée+installée, mais `mor` headless indisponible (WinCLAN GUI-only ; unix-clan GPL non compilable clé-en-main sous MinGW). Constat décisif pour le Go/No-Go.

> Note de procédure : ce plan a été exécuté **en direct par l'orchestrateur** (et non par un agent exécuteur isolé), car il nécessitait un accès live à l'environnement Windows (installation, compilation, tests CLI). Les artefacts et commits sont réels.

---

## État d'exécution

| Task | Nom | Statut | Commit |
|------|-----|--------|--------|
| 1 | Essai CLI `mor` headless sur `.cha` FR | COMPLETE (résultat négatif documenté) | ba3670e |
| 2 | Rédiger MOR-CLI-TRIAL.md (commande retenue / verdict) | COMPLETE | ba3670e |

---

## Travail réalisé en direct

1. **Localisation CLAN** : `C:\TalkBank\CLAN\CLAN.EXE` (un seul exe, pas de `mor.exe`).
2. **Grammaire MOR FR** : téléchargée (`https://talkbank.org/0info/mor/fra.zip`, 344 Ko) + extraite vers `C:\TalkBank\CLAN\lib\fra\`. → résout aussi l'install grammaire de l'action humaine 01-01.
3. **Test headless WinCLAN** : `CLAN.EXE mor +l... test.cha` → ouvre le GUI, **aucune sortie** → headless impossible avec WinCLAN.
4. **Tentative compilation unix-clan** : source GPL confirmée (en-têtes), cible `mor` du makefile isolée ; build MinGW bloqué sur headers POSIX absents (`stdafx.h` contourné via `-U_WIN32`, puis `sgtty.h`/`sys/termio.h`/`sys/ioctl.h`/curses manquants). Pas d'env POSIX (MSYS2/Cygwin/WSL) dispo.

---

## Conclusion SPIKE-02

`mor` + grammaire FR **existe et fonctionne dans le GUI WinCLAN** (vérification visuelle manuelle possible), mais **aucun `mor` headless embarquable n'est disponible clé en main sur Windows**. Le seul chemin headless (unix-clan compilé) est **GPL + porting POSIX non trivial**, en tension avec la contrainte « bundle invisible, zéro install ». Détails complets : `artifacts/MOR-CLI-TRIAL.md`.

---

## Self-Check: PASS

- `.planning/phases/01-spike-clan/artifacts/MOR-CLI-TRIAL.md` : TROUVÉ (contient "## Synthèse SPIKE-02")
- Commit ba3670e : TROUVÉ
- Grammaire installée : `C:\TalkBank\CLAN\lib\fra\cr.cut` présent
