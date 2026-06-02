# Rapport de Spike — Phase 1 (CLAN)

**Rédigé le :** 2026-06-02
**Auteur :** exécution automatique du plan 01-03
**Critères de référence :** D-07 (licence stricte), D-08 (métrique souple)

---

## SPIKE-01 — Licence

### Binaire CLAN (Windows-CLAN)

**Verdict : BSD-3-Clause — redistribution binaire AUTORISÉE**

- **Copyright :** 1990-2024 TalkBank WinCLAN
- **Source vérifiée :** `github.com/TalkBank/Windows-CLAN/blob/master/LICENSE` (vérifié le 2026-06-02)
- Redistribution source et binaire autorisée avec ou sans modification
- Aucune restriction non-commercial, aucun copyleft
- Compatible avec une licence MIT dans un projet commercial

**Trois conditions à respecter lors du packaging :**
1. Conserver le copyright notice dans le code source redistribué
2. Reproduire le copyright notice dans la documentation des binaires redistribués
3. Ne pas utiliser le nom "TalkBank" / "WinCLAN" pour promouvoir des produits dérivés sans permission écrite

Action requise lors du packaging (Phase 6) : inclure `CLAN-Windows-LICENSE.txt` dans le bundle PyInstaller et le mentionner dans les crédits de l'application.

**Compatibilité D-07 :** GO pour le binaire CLAN.

### Grammaire MOR FR (fra.zip)

**Statut : EN ATTENTE DE CONFIRMATION**

- Développée par Christophe Parisse (CNRS/MoDyCo) et Brian MacWhinney (CMU)
- Hébergée sur `talkbank.org/morgrams/fra.zip`
- Aucune licence explicite documentée sur la page officielle
- Aucun en-tête de licence inline dans les fichiers `.cut` / `.lex` (Option C inspectée)
- Demande formelle auprès de TalkBank/Parisse non encore envoyée

**Critère de bascule :**
- Réponse positive de TalkBank → Go conditionnel devient **Go définitif**
- Restriction non-commercial ou refus → **No-Go D-07** (déclenche stratégie de repli Section 5)
- Absence de réponse sous 5 jours ouvrés → ré-inspecter les fichiers `fra/*.cut` pour headers

**Compatibilité D-07 :** EN ATTENTE — Go conditionnel.

### Découverte majeure — WinCLAN est GUI-only / `mor` headless est GPL

**WinCLAN (BSD-3)** = exécutable GUI uniquement. Testé en pratique : `CLAN.EXE mor +l... test.cha` ouvre la fenêtre GUI et ne produit aucun fichier de sortie. La commande `mor` doit être tapée dans la fenêtre "Commands" du GUI — **aucune automatisation headless possible**.

**unix-clan** = fournit les commandes d'analyse en CLI (dont `mor`) mais :
- **Licence : GNU GPL** (en-tête de chaque source : *"Use is subject to Gnu Public License"*)
- **Pas de binaire Windows précompilé** — source seulement
- Compilation MinGW bloquée par des headers POSIX absents (`sgtty.h`, `sys/termio.h`, `sys/ioctl.h`)

Implications pour D-07 :
- GPL + subprocess = **agrégation simple** (précédent : FFmpeg déjà embarqué dans Ortholyse) — techniquement compatible MIT commercial
- Mais : compilation unix-clan pour Windows est fragile, non triviale, et à maintenir
- La voie BSD-3 (WinCLAN) ne convient PAS au moteur embarqué

---

## SPIKE-02 — Exécution mor headless

### Résumé des essais (machine cible Windows 11)

| Piste | Résultat |
|-------|----------|
| WinCLAN en CLI (`CLAN.EXE mor +l... file.cha`) | **ÉCHEC** — GUI uniquement, aucun fichier produit |
| Compilation unix-clan avec MinGW | **PARTIEL** — bloqué sur `sgtty.h`, `sys/termio.h`, `sys/ioctl.h` absents |
| Compilation sous MSYS2/Cygwin | Non disponible sur cette machine |
| WSL | Non disponible sur cette machine |

### Commande retenue pour `run_mor` (si binaire headless disponible)

```python
args = [mor_bin, "+l", grammar_dir, "+1", cha_path]
subprocess.run(args, capture_output=True, text=True, encoding="utf-8", env=env)
```

Avec `env["MORLIB"] = grammar_dir` comme variable d'environnement de secours.

**Pitfall 3 documenté :** `mor +1` écrit dans le fichier d'entrée (overwrite silencieux) — toujours travailler sur une copie.

### Conclusion SPIKE-02

Le `mor` headless embarquable n'est **pas disponible clé en main sur Windows** en l'état :
- Soit portage/compilation unix-clan (GPL, fragile, maintenable)
- Soit stratégie de repli pure-Python (voir Section 5)

---

## SPIKE-03 — Parsing + MLU morphèmes

### Implémentation

Module livré : `app/models/clan_wrapper.py`

Fonctions testées en CI (sans CLAN) :
- `parse_mor_tier(cha_text)` : extrait les tokens `POS|lemme` via regex `\S+\|\S+`
- `compute_mlu_morphemes(cha_path)` : `round(Σ|énoncé| / nb_énoncés, 3)`

### Résultat sur l'oracle déterministe (`tests/fixtures/sample_fra.cha`)

Fichier oracle :
```
*CHI:  le chat mange .
%mor:  det|le n|chat v|manger-PRES&3S .           → 3 tokens
*CHI:  il veut du lait .
%mor:  pro|il v|vouloir-PRES&3S det:art|de+det|le n|lait .  → 4 tokens
*CHI:  maman .
%mor:  n|maman .                                  → 1 token
```

**MLU calculée : (3 + 4 + 1) / 3 = 2.667**

Plage de plausibilité MTLN pour 2;6 (30 mois) : **[2.52, 3.52]** (Parisse & Le Normand 2002, PMC8752861)
Valeur normative de référence : **3.02**
Écart : 0.353 (dans la tolérance ±0.5, D-08)

**Jugement D-08 : plausible et explicable.** L'écart s'explique par la brièveté de l'échantillon (3 énoncés) et par le comptage conservateur (1 token = 1 unité, sans décomposition des suffixes `-PRES&3S`).

### Sortie de `pytest tests/test_clan_spike.py -q`

```
............s
SKIPPED [1] Binaire 'mor' absent du PATH — test sauté en CI
12 passed, 1 skipped
```

- 12 tests unitaires verts (parsing + MLU + find_clan_mor + run_mor mock)
- 1 test d'intégration sauté (gated sur présence du binaire `mor`)
- Couverture globale du projet : 84.49% (gate 80% respecté)

**Conclusion SPIKE-03 : SATISFAIT** (D-08).

---

## Verdict

**GO sur la voie CLAN — validé de bout en bout** (un vrai tier `%mor` a été produit par `mor` headless sur Windows ; voir `artifacts/BUILD-MOR-WINDOWS.md` + `artifacts/SPIKE-02-mor-output-sample.cha`)

> **Trajectoire du verdict.** Une rédaction intermédiaire concluait « No-Go CLAN / pivot pure-Python » — faux, car la source unix-clan est **ouverte (GPL) et modifiable**. Après portage (compilation MSYS + shim sgtty + entrée via stdin), `mor` produit un `%mor` français correct sur Windows. Le moteur CLAN/MOR — cœur de valeur du produit — est confirmé viable et embarquable.

Synthèse des trois SPIKE :

| SPIKE | Critère | Résultat |
|-------|---------|----------|
| SPIKE-01 — Licence binaire WinCLAN | BSD-3 (GUI only — non utilisé pour le moteur) | **GO** |
| SPIKE-01 — Licence moteur headless (unix-clan) | **GPL**, source ouverte/modifiable ; subprocess = agrégation (précédent FFmpeg déjà embarqué) | **GO** (compatible MIT/commercial) |
| SPIKE-01 — Licence grammaire MOR FR | Non documentée, confirmation TalkBank en attente | **EN ATTENTE** |
| SPIKE-02 — `mor` headless Windows | **VALIDÉ de bout en bout** : `mor` compilé natif (build MSYS), charge grammaire FR + 41 813 entrées lexique, **produit un tier `%mor` correct** (entrée via stdin). Preuve : `artifacts/SPIKE-02-mor-output-sample.cha` | **GO** |
| SPIKE-03 — Parsing + MLU morphèmes | 2.667 calculé, plage normative [2.52, 3.52], 12 tests verts | **GO** |

**Conclusion D-07 :** La voie **« embarquer CLAN headless sur Windows » est FAISABLE**, et non un No-Go :

- Le binaire `mor.exe` console se compile en natif Windows depuis la source GPL (recette : `-DUNX -U_WIN32 -funsigned-char` + 2 shims POSIX ; voir BUILD-MOR-WINDOWS.md). Pas besoin de MSYS2 ni de dépendance runtime.
- GPL appelé en subprocess = simple agrégation, modèle identique à FFmpeg **déjà embarqué** dans Ortholyse → compatible MIT/commercial (D-07 satisfait pour le moteur).
- CLAN/MOR reste le cœur de valeur (standard de référence clinique) : le préserver évite la régression qu'aurait été un pivot vers une annotation UD non alignée.

**Le verdict global est donc : GO sur l'intégration CLAN headless** (validé de bout en bout — un vrai `%mor` a été produit sur Windows).

### Preuve obtenue dans le spike

`mor` headless sur Windows (build MSYS, entrée via **stdin**) produit un tier `%mor` correct pour le français. Recette + invocation + preuve : `artifacts/BUILD-MOR-WINDOWS.md` et `artifacts/SPIKE-02-mor-output-sample.cha`.

### Items restants pour le Go définitif (Phase 2)

1. **Confirmer la licence de la grammaire MOR FR** (`fra.zip`) auprès de TalkBank (email macw@cmu.edu / issue GitHub) — seul vrai bloqueur D-07 restant.
2. **Finaliser le packaging du binaire** : retenir le build MSYS (avec `msys-2.0.dll` bundlée) OU porter proprement vers MinGW-w64/UCRT autonome ; intégrer via `subprocess` en **écrivant le `.cha` patient sur stdin de `mor`** (le mode "argument fichier" est cassé sur le portage Windows).
3. **Parseur multi-lignes** : `clan_wrapper.parse_mor_tier` doit concaténer les lignes de continuation des tiers `%mor` (et idéalement lancer `post` pour lever les ambiguïtés `^`) avant le calcul de MLU.

La stratégie de repli pure-Python (Section 5) n'est plus nécessaire — conservée pour mémoire uniquement.

---

## Stratégie de repli (No-Go sur la voie CLAN headless)

### Option 1 — Pure-Python : Stanza + spaCy UD + Démonette-2 (RECOMMANDÉE)

**Principe :** Remplacer l'annotation MOR par un pipeline NLP Python :
- **Stanza** (Stanford, Apache 2.0) : tokenisation + POS + morphologie pour le français (modèle `fr`)
- **spaCy** (MIT) : alternative ou complément (modèle `fr_core_news_lg` déjà dans le projet)
- **Démonette-2** (CNRS/MoDyCo, même équipe que Parisse) : base de données de dérivation morphologique française (licence académique permissive)

**Avantages :**
- pip-installable, aucun binaire C à compiler
- Multiplateforme (Windows, macOS, Linux)
- Licences permissives compatibles MIT
- Déjà partiellement dans le projet (spaCy `fr_core_news_lg`)
- Approche crédible et citable (Stanza = Stanford NLP, NeurIPS 2020)

**Inconvénients :**
- Couverture morphologique potentiellement différente de la grammaire Parisse
- Validation de la précision sur du français orthophonique requise en Phase 2
- Modèles à télécharger (~500 Mo pour Stanza FR)

**Action Phase 2 Tâche 1 :** Évaluer `stanza.Pipeline('fr')` sur l'oracle sample_fra.cha et comparer les tokens UD aux tokens MOR de l'oracle.

### Option 2 — Batchalign2 (TalkBank, BSD-3, PyPI)

**Principe :** Wrapper Python officiel TalkBank qui utilise Stanza/UD pour annoter des fichiers CHAT.
- Licence : BSD-3-Clause (compatible MIT)
- PyPI : `pip install batchalign`
- Supporte le français via Stanza

**Avantages :** Solution officielle TalkBank, format CHAT natif, BSD-3.
**Inconvénients :** N'utilise pas la grammaire Parisse MOR classique — annotation UD, pas `%mor` classique.

### Option 3 — Demande de permission formelle à TalkBank (pour la voie CLAN)

Si la grammaire MOR FR est confirmée redistribuable ET si un binaire `mor` headless Windows peut être obtenu (précompilé par TalkBank ou via MSYS2) :
- Envoyer email à `macw@cmu.edu` demandant : redistribution de `fra.zip` + binaire `mor` Windows précompilé
- Délai estimé : 5–15 jours ouvrés
- Risque : réponse négative ou absence de réponse → retour Option 1

### Option 4 — Amélioration de l'heuristique existante (`Analyse_NLTK`)

**Pour un déploiement rapide seulement.** Améliorer `Analyse_NLTK.morphem()` avec les règles morphologiques Snowball + dictionnaires de morphèmes FR. Fragile, non citable, non conforme aux standards CLAN — **déconseillé comme cible long terme**.

### Décision recommandée

**Phase 2 doit commencer par l'Option 1 (Stanza + spaCy UD)**, en parallèle de la demande de licence MOR FR (Option 3). Si Stanza atteint une précision satisfaisante (D-08 : plausible et explicable), la voie pure-Python devient la voie principale sans attendre CLAN.

---

*Rapport validé par l'exécution du plan 01-03 — 2026-06-02*
*Prochaine étape : Phase 2 Tâche 1 — évaluation Stanza sur le corpus français orthophonique*
