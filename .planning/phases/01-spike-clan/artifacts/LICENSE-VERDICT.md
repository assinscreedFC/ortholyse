# Verdict de licence — SPIKE-01

Redige le: 2026-06-02
Critere de reference: D-07 (redistribution totalement libre, compatible MIT/commercial sans restriction bloquante)

---

## Binaire CLAN (Windows-CLAN)

**Verdict : BSD-3-Clause — redistribution binaire AUTORISEE**

- **Copyright :** 1990-2024 TalkBank WinCLAN
- **Source de la preuve :** `artifacts/CLAN-Windows-LICENSE.txt` (recupere depuis https://github.com/TalkBank/Windows-CLAN/blob/master/LICENSE le 2026-06-02)
- **OSX-CLAN :** meme licence BSD-3-Clause (https://github.com/TalkBank/OSX-CLAN)

### Trois conditions de redistribution (BSD-3)

1. Conserver le copyright notice dans le code source redistribue
2. Reproduire le copyright notice dans la documentation des binaires redistribues
3. Ne pas utiliser le nom "TalkBank" ni "WinCLAN" pour promouvoir des produits derives sans permission ecrite prealable

### Compatibilite avec le projet Ortholyse

- Licence MIT du projet Ortholyse : compatible BSD-3 (pas de copyleft, pas de restriction non-commercial)
- Usage commercial autorise
- Redistribution binaire (PyInstaller bundle) autorisee sous les 3 conditions ci-dessus
- Action requise lors du packaging : inclure le fichier `CLAN-Windows-LICENSE.txt` dans le bundle et le mentionner dans les credits de l'application

**Compatibilite D-07 : GO pour le binaire CLAN**

---

## Grammaire MOR FR (fra.zip)

**Statut : EN ATTENTE DE CONFIRMATION — licence non documentee publiquement**

- **Developpee par :** Christophe Parisse (CNRS/MoDyCo, Universite Paris Nanterre) et Brian MacWhinney (CMU)
- **Hebergee sur :** talkbank.org/morgrams/fra.zip
- **Page officielle :** https://talkbank.org/0info/mor/index.html
- **Constat :** La page officielle ne mentionne aucune licence explicite pour la grammaire MOR FR. Aucun avertissement "non-commercial" ou restriction visible dans les publications associees.

### Action humaine requise (Task 1 — non encore realisee)

Pour lever l'incertitude, l'une des deux demarches suivantes doit etre effectuee :

**Option A — GitHub Issue (prefere, trace publiquement) :**
Ouvrir un issue sur https://github.com/TalkBank/Windows-CLAN/issues avec la question :

> "Can the French MOR grammar (fra.zip, developed by Christophe Parisse) be redistributed
> in binary/data form inside a MIT-licensed desktop application intended for speech-language
> therapists? We would like to bundle it invisibly with our application."

**Option B — Email direct :**
Envoyer un email a macw@cmu.edu avec la meme question.

**Option C — Inspection des fichiers locaux (apres installation) :**
Inspecter les headers des fichiers `C:\TalkBank\CLAN\fra\*.cut` et `*.lex` pour une notice de licence inline.

### Critere de bascule

- Si reponse TalkBank confirme redistribution libre → **Go conditionnel devient Go definitif**
- Si restriction non-commercial ou requirement de permission → **No-Go D-07** (declenche strategie repli : Batchalign2/Stanza + Demonette-2)
- Si aucune reponse sous 5 jours ouvrés → inspecter les fichiers `fra/*.cut` pour header de licence

**Compatibilite D-07 : A CONFIRMER — demande de licence MOR FR non encore tracee**

---

## MISE A JOUR 2026-06-02 (session interactive) — constats de terrain

### Installation reelle effectuee

- CLAN installe : `C:\TalkBank\CLAN\CLAN.EXE` (un seul executable, **pas de `mor.exe` separe**)
- Grammaire MOR FR telechargee : `https://talkbank.org/0info/mor/fra.zip` (344 Ko) puis extraite vers `C:\TalkBank\CLAN\lib\fra\` (66 entrees, `cr.cut` + `lex/` presents)

### Option C realisee — inspection des fichiers grammaire FR

**Resultat : AUCUN en-tete de licence inline.** Les occurrences de "copyright"/"licencie" trouvees sont des entrees du lexique francais (mots du dictionnaire), pas une notice. → La licence de la grammaire MOR FR **reste non documentee** ; la demande humaine (email macw@cmu.edu / GitHub issue) demeure necessaire.

### DECOUVERTE MAJEURE — WinCLAN (BSD-3) est GUI uniquement / le headless est GPL

Source : page de telechargement officielle https://dali.talkbank.org/clan/

- **WinCLAN (`clanwin.exe`)** = binaire GUI sous **BSD-3**. Verifie en pratique : lancer `CLAN.EXE mor +l... test.cha` en ligne de commande **ouvre la fenetre GUI et ne produit aucun fichier de sortie** — `mor` ne s'execute PAS en headless avec WinCLAN. La commande `mor` se tape dans la fenetre "Commands" du GUI.
- **UnixCLAN (`unix-clan.zip`)** = fournit les commandes d'analyse en CLI (dont `mor`) **MAIS uniquement en SOURCE sous GNU GPL**, et **aucun binaire console pret-a-l'emploi n'est distribue** (citation : *"No binary command-line version is available. The Unix distribution provides only source code… distributed under the GNU General Public License."*).

### Implication pour D-07 et la Phase 2 (embarque, invisible, headless)

Le wrapper Python (D-05) a besoin d'un `mor` **headless** appele en `subprocess`. Le seul `mor` headless disponible vient d'**UnixCLAN = GPL**, qu'il faut **compiler depuis la source** (pas de binaire Windows prebuilt).

- GPL via `subprocess` = **simple agregation** (precedent : FFmpeg, deja embarque dans Ortholyse) → **compatible avec une app MIT/commerciale** tant que le binaire `mor` reste un executable separe appele en sous-process (pas de linkage).
- Obligations GPL a respecter pour CE binaire : fournir/offrir la source correspondante + conserver l'avis GPL.
- Cout additionnel reel : **compiler unix-clan pour Windows** (toolchain C type MinGW) — etape de packaging non triviale, a valider.

→ La voie BSD-3 (WinCLAN) ne sert PAS au moteur embarque (GUI only). Le moteur embarquable est **GPL (unix-clan compile)**. C'est une nuance qui modifie la lecture de D-07 (« totalement libre ») : GPL+agregation reste acceptable (modele FFmpeg) mais n'est pas « sans aucune contrainte ».

### Deux items ouverts pour le Go definitif

1. **Licence grammaire MOR FR** (`fra.zip`) — confirmation humaine TalkBank toujours requise.
2. **Acceptabilite GPL + faisabilite compilation** d'unix-clan `mor` pour Windows (alternative : valider que le GUI WinCLAN suffit, ou retenir la strategie de repli Batchalign2/Stanza).

---

## Verdict

**SPIKE-01 : Go conditionnel**

La decision D-07 s'applique comme suit :

- **Binaire CLAN (Windows-CLAN) :** BSD-3-Clause verifie — redistribution libre, compatible MIT. **GO.**
- **Grammaire MOR FR (fra.zip) :** Licence non documentee publiquement. La confirmation aupres de TalkBank/Parisse n'a pas encore ete initiee (Task 1 du plan en attente d'action humaine). **EN ATTENTE.**

**Conclusion D-07 :** Go conditionnel — le binaire CLAN est libre, mais la grammaire MOR FR necessite confirmation avant de conclure Go definitif sur SPIKE-01. Le spike technique (SPIKE-02, SPIKE-03) peut avancer en parallele. La conclusion Go/No-Go definitive attend la reponse de TalkBank.

> La conclusion deviendra **Go** si la grammaire MOR FR est confirmee redistribuable.
> Elle deviendra **No-Go** si une restriction bloquante est identifiee — la strategie de repli
> documentee est : Batchalign2 (TalkBank, BSD-3, PyPI) + grammaire UD via Stanza + Demonette-2
> pour la morphologie derivationnelle FR.

---

*Redige par : execution automatique du plan 01-01*
*Mise a jour requise : apres reception de la reponse de TalkBank sur la licence MOR FR*
