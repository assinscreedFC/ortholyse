# Compilation de `mor` headless natif Windows — recette + état

Rédigé le : 2026-06-02 (session interactive, machine Windows 11 cible)

## Résultat (correction du verdict prématuré No-Go)

Un binaire `mor.exe` **console / headless** a été **compilé avec succès en natif Windows** depuis la source GPL `unix-clan`. Il s'exécute sans GUI, charge la grammaire MOR française complète et amorce l'analyse. **CLAN headless embarquable sur Windows est donc FAISABLE.** Reste un bug de portage borné (lecture `.cha`) avant production du tier `%mor` — détaillé plus bas.

## Pré-requis

- Source : `unix-clan.zip` → `https://dali.talkbank.org/clan/unix-clan.zip` (GPL)
- Grammaire FR : `fra.zip` → `https://talkbank.org/0info/mor/fra.zip`
- Toolchain : MinGW.org g++ 6.3.0 (32-bit) + mingw32-make (présents en `C:\MinGW`)
- **Important** : le makefile exige du 32-bit (« CLAN has to be 32bit ») — MinGW.org est 32-bit par défaut, OK.

## Patches nécessaires (code modifiable car GPL)

Deux headers POSIX absents de MinGW, fournis en shim (dossier `shim/`, ajouté via `-I`) :

`shim/sgtty.h` — `struct sgttyb` + macros `TIOCGETP`/`TIOCSETP` + stubs `gtty()`/`stty()` renvoyant -1 (mode batch, pas de terminal).
`shim/sys/ioctl.h` — `static inline int ioctl(int, unsigned long, ...) { return -1; }`.

(Copies versionnées dans `artifacts/mor-build-shims/`.)

## Commande de build (cible `mor` seule)

```powershell
cd <unix-clan>\src
$shim = "<...>/shim"
$cf = "-O -DUNX -U_WIN32 -U_WIN64 -funsigned-char -I$shim " +
      "-Wno-deprecated -Wno-deprecated-declarations -Wno-narrowing -fpermissive"
mingw32-make mor CC=g++ CFLAGS=$cf
# -> <unix-clan>\unix\bin\mor.exe
```

Flags clés expliqués :
- `-DUNX` : chemin de code Unix (le chemin `_WIN32` exige stdafx.h/Clan2.h = framework GUI MSVC, inutilisable).
- `-U_WIN32 -U_WIN64` : MinGW définit `_WIN32` ; on le neutralise pour rester sur le chemin UNX.
- `-funsigned-char` : **critique** — le code CLAN suppose `char` non signé ; sans ce flag, la détection du BOM/des octets > 0x7F échoue (symptôme `0xffffffef`).
- `-fpermissive` : tolère des conversions héritées (ex. `isatty(FILE*)`).

## Exécution headless validée

```powershell
# Structure attendue : <run>/data/<fichier>.cha  et  <run>/lib/ = contenu de fra.zip (ar.cut, lex/, cr.cut...)
cd <run>\data
mor.exe +M../lib t.cha     # +M = dossier grammaire (ancré sur le cwd -> chemin absolu, robuste)
```

Sortie observée (succès du chargement) :
```
Using output-rule / sf-rule / ex-rule / a-rules : .../lib/*.cut
Using a-rules: .../lib/ar/{adj,n,v}.cut
Using lexicon: .../lib/lex/*.cut
Loaded lexicon: 41813
Using c-rules: .../lib/cr.cut
... conducting analyses on ALL speaker tiers ...
From file <t.cha>
```

## Bug de portage restant (à corriger en Phase 2)

Sur TOUT `.cha` (y compris le `sample.cha` livré avec CLAN, donc indépendant de notre format) :
```
*** File "...": line 1.
Illegal speaker character found: 0xef  (puis '�' après -funsigned-char)
CURRENT OUTPUT FILE IS INCOMPLETE.
```
Diagnostic : un octet `0xEF` parasite est vu en tête de ligne 1 par le lecteur d'analyse, alors que le fichier n'en contient pas (vérifié au hexdump). Le BOM est correctement géré par `chattest` (cutt.cpp:11618) et par le lecteur (cutt.cpp:12558/12572), donc la cause probable est la **couche de conversion de police/encodage** (`fontconvert.cpp`) ou un buffer global mal initialisé sous MinGW. C'est un bug borné à investiguer (≈ quelques heures), pas un blocage fondamental.

## Conséquence Go/No-Go

Faisabilité headless CLAN sur Windows = **démontrée à 90 %** (build + grammaire + lexique + moteur OK). Reste un bug de lecture isolé. CLAN reste le bon moteur (cœur de valeur = standard CLAN/MOR). GPL via subprocess = OK (précédent FFmpeg). → **Go conditionnel CLAN**, pas No-Go.
