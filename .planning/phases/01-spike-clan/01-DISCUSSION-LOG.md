# Phase 1: Spike CLAN - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-02
**Phase:** 01-spike-clan
**Areas discussed:** Plateforme cible, Oracle de validation, Nature du livrable code, Seuil Go/No-Go

---

## Plateforme cible du spike

| Option | Description | Selected |
|--------|-------------|----------|
| Windows d'abord | Plateforme primaire de dev + cible orthophonistes ; valide où le risque packaging est réel ; macOS reporté Phase 6 | ✓ |
| Cross-platform d'emblée | Valider Windows + macOS dès le spike ; double le travail avant Go/No-Go | |
| unix-CLAN (dev Linux/WSL) | Plus simple à scripter, mais éloigné de la cible Windows | |

**User's choice:** Windows d'abord
**Notes:** —

---

## Oracle de validation (SPIKE-03)

| Option | Description | Selected |
|--------|-------------|----------|
| Sample CHILDES FR publié | `.cha` du corpus French CHILDES avec MLU documentée ; oracle crédible et citable | ✓ |
| Fait-main minimal | Petit `.cha` à la main, MLU calculée manuellement ; contrôle total, moins crédible | |
| Transcription réelle de l'app | Proche du cas d'usage mais aucune MLU de référence ; pas un oracle | |

**User's choice:** Sample CHILDES FR publié
**Notes:** —

---

## Nature du livrable code

| Option | Description | Selected |
|--------|-------------|----------|
| Amorce réutilisable Phase 2 | Appel `mor` + parsing %mor écrits proprement (pattern find_ffmpeg), repris par Phase 2 | ✓ |
| Mixte | Exploration licence/CLI jetable, bout mor+parsing gardé propre | |
| Jetable (throwaway) | Tout en script jetable, vitesse max | |

**User's choice:** Amorce réutilisable Phase 2
**Notes:** Première formulation pas comprise par l'utilisateur ; re-expliquée en clair (le code = appeler CLAN `mor` + parser `%mor` pour la MLU ; la question portait sur la qualité/réutilisabilité). Choix confirmé après clarification.

---

## Seuil Go/No-Go

| Option | Description | Selected |
|--------|-------------|----------|
| Strict licence / souple métrique | Go si redistribution totalement libre, sinon No-Go ; tolérant sur écart MLU | ✓ |
| Pragmatique global | Go si licence exploitable même ambiguë ET MLU dans tolérance | |
| Strict total | Go si redistribution libre ET MLU quasi-exacte | |

**User's choice:** Strict licence / souple métrique
**Notes:** L'utilisateur a d'abord répondu « je veux une utilisation totale et libre, j'imagine que c'est opt3 ». Clarification : son intention = redistribution totalement libre (= strict licence). Côté métrique il a confirmé préférer la souplesse → option « Strict licence / souple métrique ».

---

## Claude's Discretion

- Choix exact du `.cha` CHILDES FR de référence
- Forme et gabarit du rapport de spike
- Détails d'implémentation du wrapper subprocess CLAN
- Stratégie de repli précise si No-Go

## Deferred Ideas

- Source/licence détaillée de la grammaire MOR FR (recherche de phase)
- Format précis du rapport de spike
- Stratégies de repli si No-Go (permission TalkBank, MOR-lite via Démonette/UD, heuristique améliorée)
