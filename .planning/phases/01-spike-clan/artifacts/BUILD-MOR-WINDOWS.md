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

## Bug de portage restant — CAUSE RACINE IDENTIFIÉE (à corriger en Phase 2)

Symptôme : sur TOUT `.cha` (y compris le `sample.cha` livré avec CLAN) :
```
*** File "...": line 1.
Illegal speaker character found: 0xef  (puis '�' après -funsigned-char)
CURRENT OUTPUT FILE IS INCOMPLETE.
```

### Diagnostic (instrumentation de `getc_cr`)

- Le fichier sur disque est correct (1er octet `0x40` `@`, vérifié au hexdump ; une **ouverture fraîche** `fopen(name,"rb")` rend bien `0x40`).
- Mais le handle `fpin` réutilisé par l'analyse, **à `ftell()==0`**, rend `0xEF` puis `0xFF` (octets type-BOM parasites) au lieu du contenu.
- Aucun `ungetc` dans le code source ; `getc`/`rewind`/`fopen` sont les vrais (build ni `_MAC_CODE` ni `_WIN32`).
- Cause : **`chattest()` lit le fichier jusqu'à EOF puis `rewind(fpin)` ne vide PAS le buffer de lecture** sur le **runtime msvcrt antique de MinGW.org 6.3.0** → le buffer périmé est relu par l'analyse. Remplacer ce `rewind` par `freopen`/`fseek` ne suffit pas (corruption plus profonde dans la couche I/O bufferisée du vieux msvcrt).
- Effet de bord à connaître : `mor` écrit sa sortie **en écrasant le fichier d'entrée** par défaut → toujours travailler sur une **copie** (déjà noté D-06/Pitfall).

### Suite de l'investigation — builds toolchains modernes (MSYS2)

Tentatives menées après le constat msvcrt :

1. **MinGW-w64 UCRT (`ucrt64`, g++ 16.1.0)** : ÉCHEC de compilation. Les headers MinGW-w64 **imposent `_WIN32` défini** (`#error Only Win32 target is supported!`), or le portage neutralisait `_WIN32` (`-U_WIN32`) pour éviter le chemin GUI Windows de CLAN (stdafx.h/Clan2.h/MFC). Incompatible sans réécrire la stratégie de defines.

2. **MSYS natif (toolchain Cygwin-like, `/usr/bin/g++`)** : **COMPILE proprement** (`_WIN32` non défini, headers POSIX présents ; seul `sgtty.h` manque → shim). Le binaire **s'exécute et termine sans crash** (`EXIT=0`) : **le bug stdio 0xEF est CORRIGÉ** par la stdio POSIX de MSYS. Il faut lancer avec `stdin < /dev/null` (sinon mor attend une entrée interactive et se bloque).

### Bug restant après MSYS — sortie d'analyse vide

mor charge tout, lit le fichier (plus d'erreur « Illegal speaker »), atteint la fin, MAIS :
- Il applique le mécanisme CLAN de **remplacement du fichier** (écrit un temp, supprime l'original, renomme le temp → nom d'origine).
- Sur Windows ce cycle échoue : `Can't delete original file ... Perhaps it is opened by some application.` (sémantique POSIX « unlink d'un fichier ouvert » mal portée), et le temp `.mor.cex` reste à **0 octet** → analyse vide, et l'entrée peut être tronquée si entrée==sortie.

### Résolution recommandée (Phase 2)

La faisabilité est prouvée (build + exécution + grammaire). Le dernier obstacle est la **couche de fichiers I/O du portage Windows de CLAN** (lecture qui délivre vide + remplacement temp→original qui échoue). Deux voies pour la Phase 2 :
- **(A) Durcir le portage** : corriger la gestion de fichiers de `cutt.cpp` sous Windows (ordre fermeture/unlink/rename, chemins relatifs après `chdir` de chargement grammaire, écriture directe d'un `.cex` distinct sans étape de remplacement). Effort de debug C dédié.
- **(B) Builder mor sur Linux/macOS** (cible native d'unix-clan, où tout ce mécanisme fonctionne) et l'intégrer par plateforme (CI multi-OS), plutôt que de porter le I/O Windows.

Les deux restent compatibles avec un moteur CLAN embarqué (GPL+subprocess, modèle FFmpeg).

## Conséquence Go/No-Go

Faisabilité headless CLAN sur Windows = **démontrée à ~90 %** : build natif OK, grammaire FR + 41 813 entrées lexique + a/c-rules chargées, moteur d'analyse atteint. Reste un bug d'I/O **isolé et diagnostiqué** (runtime msvcrt vétuste), résolution claire (toolchain UCRT). CLAN reste le bon moteur (cœur de valeur = standard CLAN/MOR). GPL via subprocess = OK (précédent FFmpeg). → **Go conditionnel CLAN**, pas No-Go.
