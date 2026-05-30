**Lire en [English](./CONTRIBUTING.md) / [Français](./CONTRIBUTING.fr.md)**

# Contribuer à Ortholyse

Merci de prendre le temps de regarder comment aider. Ce projet est maintenu sur du temps disponible ; les contributions font une vraie différence.

## Règles de base

- Ouvrir une issue avant une pull request non triviale. Le design se discute avant que la moindre ligne de code soit écrite.
- Un seul sujet par PR. Les petits diffs passent plus vite.
- Messages de commit conventionnels : `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`.
- Le code reste en anglais (identifiants, commentaires, messages de commit). Les chaînes user-facing restent en français ; l'UI anglaise est dans la feuille de route.
- Aucun secret, aucune donnée patient, aucun échantillon audio committé dans le dépôt.

## Signaler un bug

Utiliser le template d'issue **Bug report**. Inclure :

- Une description claire de ce qui s'est passé versus ce qui était attendu.
- Les étapes pour reproduire, avec des inputs concrets.
- Votre OS, version de Python, et le SHA ou tag du commit concerné.
- Les logs et la traceback éventuelle, copiés en texte plutôt qu'en capture.

## Demander une fonctionnalité

Utiliser le template d'issue **Feature request**. Décrire le besoin clinique ou de recherche derrière la demande, pas seulement la solution technique. Ça aide à choisir la bonne forme pour le fix.

## Setup local

```bash
git clone https://github.com/assinscreedFC/ortholyse.git
cd ortholyse
python -m venv .venv
source .venv/bin/activate     # macOS / Linux
.\.venv\Scripts\activate      # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m spacy download fr_core_news_lg
python -m spacy download fr_core_news_sm
```

Lancer l'app :

```bash
python app/main.py
```

## Tests

Lancer la suite avant de push :

```bash
pytest
pytest --cov=app --cov-report=term-missing
```

La CI échoue si la couverture des modules gatés (`app/feuille/`, `app/exportation/`, `app/operation_fichier/`) descend sous 80 %. Les widgets UI et les wrappers Whisper / Spacy sont exclus du gate.

Si vous ajoutez un module métier, ajouter des tests dans le dossier correspondant sous `tests/`.

## Style

- Lancer `ruff check app tests` avant de committer.
- Type hints sur toutes les fonctions publiques.
- Garder des fonctions focalisées ; au-delà de 50 lignes, envisager un découpage.

## Flux pull request

1. Forker le dépôt.
2. Créer une branche depuis `main` : `git checkout -b feat/courte-description`.
3. Committer par petits changements ciblés.
4. Lancer `ruff` et `pytest` en local.
5. Push et ouvrir une PR via le template.
6. Référencer l'issue associée avec `Closes #N`.

Un reviewer répondra dès que possible. Merci d'être patient ; c'est un projet annexe maintenu, pas une activité à plein temps.

## Code de conduite

Respect mutuel. On suppose la bonne foi. Pas de harcèlement, pas d'attaque personnelle. Si quelque chose ne va pas, ouvrir une issue et on règle ça.

## Licence

En soumettant une contribution, vous acceptez qu'elle soit publiée sous la [licence MIT](./LICENSE).
