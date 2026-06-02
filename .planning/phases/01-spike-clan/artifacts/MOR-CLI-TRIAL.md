# Essai CLI `mor` headless — SPIKE-02

Rédigé le : 2026-06-02 (session interactive sur la machine Windows cible)

## Objectif

Déterminer si la commande `mor` (grammaire MOR FR) peut s'exécuter **en headless** (sans GUI, en `subprocess`) sur Windows — prérequis du wrapper Python embarqué (D-05) et de la Phase 2.

## Environnement réel

- OS : Windows 11
- CLAN installé : `C:\TalkBank\CLAN\CLAN.EXE` (WinCLAN, **un seul exécutable, pas de `mor.exe`**)
- Grammaire MOR FR : `C:\TalkBank\CLAN\lib\fra\` (téléchargée depuis `https://talkbank.org/0info/mor/fra.zip`)
- Compilateur dispo : MinGW.org g++ 6.3.0 (32-bit) + mingw32-make 3.82

## Piste 1 — WinCLAN en ligne de commande : ÉCHEC (GUI-only)

Commande testée :
```powershell
& "C:\TalkBank\CLAN\CLAN.EXE" mor +lC:\TalkBank\CLAN\lib\fra test_fra.cha
```
Résultat : `CLAN.EXE` **ouvre sa fenêtre GUI** (titre « Clan - [newfile.cha] ») et **ne produit aucun fichier de sortie** ni sortie stdout. La commande `mor` n'est pas traitée en batch — elle doit être tapée dans la fenêtre *Commands* du GUI.

**Conclusion piste 1 :** WinCLAN ne convient PAS pour une automatisation headless. Il peut servir uniquement à une vérification visuelle manuelle de SPIKE-02 (l'humain tape `mor` dans le GUI et constate le tier `%mor`).

## Piste 2 — Compiler unix-clan `mor` (le vrai chemin headless) : PARTIEL / porting requis

- Source : `https://dali.talkbank.org/clan/unix-clan.zip` (20.8 Mo, 481 fichiers)
- **Licence confirmée = GNU GPL** : en-tête de chaque source — *« Copyright 1990-2026 Brian MacWhinney. Use is subject to Gnu Public License as stated in the attached gpl.txt file. »*
- Makefile : cible `mor` dédiée (`src/makefile:298`), ne lie ni curses ni termcap. MinGW.org est 32-bit (conforme à l'exigence « CLAN has to be 32bit »).

Blocages de compilation rencontrés (build MinGW natif) :
1. `common.h:21` → `#include "stdafx.h"` sous `#if defined(_WIN32)` (artefact MSVC). Contourné avec `-U_WIN32 -U_WIN64`.
2. `cutt.cpp:49` → `#include <sgtty.h>` (header terminal BSD absent de MinGW). La branche `USE_TERMIO` exige `<sys/termio.h>` / `<sys/errno.h>` (absents aussi), puis suivent `<sys/ioctl.h>`, `c_curses.h`…

**Conclusion piste 2 :** unix-clan est une base **POSIX (Linux/macOS)**. Un build **MinGW natif** nécessite de stubber/porter plusieurs headers POSIX (`sgtty.h`, `sys/termio.h`, `sys/ioctl.h`, curses) — effort non trivial et fragile. Alternative : compiler sous **MSYS2/Cygwin** (couche POSIX) → ajoute une dépendance runtime, en tension avec la contrainte « bundle invisible, zéro install ».

## Synthèse SPIKE-02

| Question | Réponse |
|----------|---------|
| `mor` + grammaire FR existe et fonctionne ? | Oui (via le GUI WinCLAN, à confirmer visuellement) |
| Headless via WinCLAN (subprocess) ? | **Non** — GUI uniquement |
| Headless via unix-clan compilé ? | **Possible mais coûteux** — porting POSIX→Windows requis, source GPL |
| Compatible « bundle invisible offline » sans effort ? | **Non** en l'état |

## Implication pour le Go/No-Go

Le `mor` headless embarquable n'est PAS disponible « clé en main » sur Windows :
- soit on investit dans le portage/compilation d'unix-clan (GPL, fragile, à maintenir),
- soit on retient la **stratégie de repli pure-Python** (Stanza/spaCy UD + Démonette-2 pour la morphologie dérivationnelle FR) — permissive, multiplateforme, sans cauchemar de packaging binaire.

Ce constat est exactement la valeur du spike : décider AVANT d'investir dans le moteur.
