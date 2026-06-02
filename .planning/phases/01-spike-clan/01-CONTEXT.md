# Phase 1: Spike CLAN - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Spike de dérisquage technique (pas du code de production). Trois questions à trancher avant d'investir dans le moteur d'analyse :

1. **Licence** — la licence CLAN/TalkBank autorise-t-elle la redistribution des binaires dans Ortholyse (SPIKE-01) ?
2. **Exécution** — peut-on appeler `mor` avec la grammaire MOR française en CLI sur un `.cha` de test et obtenir un tier `%mor` lisible (SPIKE-02) ?
3. **Parsing/validation** — un script Python peut-il parser la sortie CLAN et calculer une MLU en morphèmes vérifiable contre un échantillon de référence connu (SPIKE-03) ?

**Livrable final** : un rapport de spike écrit concluant **Go** ou **No-Go**, avec stratégie de remplacement documentée si No-Go.

Hors périmètre : génération `.cha` depuis transcription, segmentation en énoncés, intégration UI, set de métriques complet — tout cela appartient aux Phases 2+.

</domain>

<decisions>
## Implementation Decisions

### Plateforme cible du spike
- **D-01:** Valider CLAN + `mor` sur **Windows d'abord** (plateforme primaire de dev et cible des orthophonistes). On valide là où le risque packaging est réel ; macOS est reporté à la Phase 6 (Distribution).
- **D-02:** Tester la build CLAN qui fournit la commande `mor` sur Windows (CLAN Windows / unix-CLAN selon disponibilité de `mor`) — le choix exact du binaire est à confirmer par la recherche.

### Oracle de validation (SPIKE-03)
- **D-03:** L'échantillon de référence est un **`.cha` issu du corpus French CHILDES avec MLU documentée/publiée**. Oracle crédible et citable, permettant de comparer notre parsing à une valeur reconnue.
- **D-04:** La validation compare la MLU morphèmes calculée par notre parsing à la MLU de référence de cet échantillon.

### Nature du livrable code
- **D-05:** Le code du spike est une **amorce réutilisable pour la Phase 2** : l'appel `mor` en sous-process + le parsing du tier `%mor` sont écrits proprement dès maintenant, en suivant le pattern de résolution de binaire existant (`operation_fichier.find_ffmpeg`, `app/models/operation_fichier.py:70`). La Phase 2 reprend ce code directement si Go.
- **D-06:** Seule l'exploration de la licence et les essais en ligne de commande exploratoires peuvent rester jetables ; le bout « appel `mor` + parsing → MLU » doit être propre.

### Seuil Go/No-Go
- **D-07:** **Strict sur la licence** : Go uniquement si la redistribution des binaires CLAN (et de la grammaire MOR FR) est **totalement libre** — compatible avec une distribution MIT/commerciale sans restriction bloquante. Sinon → **No-Go**, avec stratégie de repli documentée.
- **D-08:** **Souple sur la métrique** : un écart raisonnable entre la MLU calculée et l'oracle CHILDES ne bloque pas (les écarts de parsing fins se corrigent en Phase 2). Le critère métrique est « MLU plausible et explicable », pas « exacte au centième ».

### Claude's Discretion
- Choix exact du `.cha` CHILDES FR de référence (parmi les corpus disponibles avec MLU publiée).
- Forme précise du rapport de spike (Markdown dans le répertoire de phase recommandé).
- Détails d'implémentation du wrapper subprocess (gestion des chemins, encodage de la sortie CLAN).
- Stratégie de repli précise à proposer si No-Go (à étoffer pendant le spike).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

Pas de spec/ADR externe pour ce projet — les exigences sont capturées dans les artefacts de planification internes ci-dessous.

### Exigences du spike
- `.planning/REQUIREMENTS.md` — SPIKE-01 (licence), SPIKE-02 (appel `mor` FR → `%mor`), SPIKE-03 (parsing + MLU morphèmes)
- `.planning/ROADMAP.md` §Phase 1 — Goal + 4 Success Criteria (dont le rapport Go/No-Go)

### Stratégie produit (contexte bloquant)
- `.planning/PROJECT.md` — décisions actées : moteur = CLAN + MOR FR embarqués ; format pivot CHAT `.cha` ; licence = bloquant Phase 0

### Code existant à réutiliser/cohérence
- `app/models/operation_fichier.py` §`find_ffmpeg` (ligne 70) — pattern de résolution de binaire embarqué invisible (PyInstaller `_MEIPASS` + `_internal/`, fallback vendored, fallback PATH). Modèle à suivre pour l'orchestration du binaire CLAN.

### À investiguer pendant la recherche (sources externes, pas encore référencées localement)
- Licence CLAN/TalkBank (CLAN open source sur GitHub) — vérifier les termes exacts de redistribution
- Grammaire MOR française (Christophe Parisse, MoDyCo/CNRS) — **licence propre, distincte de CLAN**, à vérifier séparément (D-07 s'applique aussi à elle)
- Corpus French CHILDES avec MLU publiée (oracle D-03)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `operation_fichier.find_ffmpeg()` (`app/models/operation_fichier.py:70`) — résolution de binaire embarqué (frozen `_MEIPASS`/`_internal` → vendored `bin/` → PATH → littéral). Transposable tel quel à la découverte du binaire CLAN.
- Moteur actuel à remplacer (contexte, pas réutilisé) : `Analyse_NLTK.morphem()` — heuristique JSON + stemmer Snowball, jugée fragile (cible du remplacement Phase 2).

### Established Patterns
- Orchestration de binaires externes via `subprocess` déjà présente (`audio_worker.py`, `operation_fichier.py`) — cohérence pour l'appel CLAN.
- RGPD strict : **ne jamais logger de texte patient** ; ici l'échantillon CHILDES est public, donc loggable sans risque.
- Gate de couverture 80 % sur les modules métier — le code « amorce réutilisable » (D-05) devra être testable et testé en Phase 2 ; pour le spike, viser un parsing isolé et testable.

### Integration Points
- Le wrapper CLAN du spike (D-05) deviendra une brique du moteur Phase 2, en remplacement de `Analyse_NLTK.py`.
- Le packaging du binaire CLAN (Phase 6) réutilisera le mécanisme `find_ffmpeg` / `_internal/`.

</code_context>

<specifics>
## Specific Ideas

- L'utilisateur veut une **redistribution totalement libre** du binaire CLAN — c'est le critère dur du Go/No-Go (D-07). Si la licence impose une restriction bloquante (non-commercial, copyleft incompatible, autorisation au cas par cas), c'est un No-Go qui déclenche la stratégie de repli.

</specifics>

<deferred>
## Deferred Ideas

- Source/licence détaillée de la grammaire MOR FR — sera investiguée pendant la recherche de phase ; relève du même critère licence (D-07).
- Format précis et gabarit du rapport de spike — laissé à la discrétion de l'exécution.
- Stratégies de repli si No-Go (demande de permission écrite à TalkBank, ré-implémentation MOR-lite via Démonette/UD, amélioration de l'heuristique existante) — à documenter dans le rapport de spike lui-même, pas avant.

</deferred>

---

*Phase: 01-spike-clan*
*Context gathered: 2026-06-02*
