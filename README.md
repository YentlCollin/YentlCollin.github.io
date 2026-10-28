# Yentl Collin — Personal website

Site académique statique, hébergé sur https://yentlcollin.github.io.
Présentation, intérêts de recherche, publications, notes et contacts.

## Modifier le contenu

- `content.json` : présentation, liens de contact, intérêts, publications et actualités.
- `assets/style.css` : apparence et mise en page.
- `assets/Yentl-Collin-CV.pdf` : remplacer pour mettre à jour le CV.
- Photo : placer le portrait dans `assets/portrait.jpg`, puis mettre `"portrait": "assets/portrait.jpg"` dans `content.json`. Le schéma de la page d’accueil sera automatiquement remplacé par la photo. Le cadrage est au format 4:5.

## Ajouter une actualité ou une sortie

Ajouter une entrée à la liste `news` de `content.json` :

```json
{
  "date": "2026-10",
  "title": "Titre de l’annonce",
  "category": "Team release",
  "description": "Une phrase présentant la nouvelle.",
  "url": "https://example.com/annonce"
}
```

La date accepte `AAAA-MM` ou `AAAA-MM-JJ`. Les entrées sont classées de la plus récente à la plus ancienne ; à date égale, l’ordre du fichier est conservé. Utiliser `Contribution` pour une sortie à laquelle tu as participé, `Team release` pour une annonce de ton équipe, ou par exemple `Reading` pour une lecture intéressante. Préciser ta contribution dans la description lorsque c’est pertinent. Les liens pointent vers l’annonce ou la ressource d’origine. La rubrique apparaît à droite des publications sur ordinateur, dans une colonne plus discrète, et après les publications sur les écrans étroits.

## Publier une note

Copier `notes/example.md` vers `notes/mon-sujet.md` (minuscules et tirets), puis modifier le titre, la date (AAAA-MM-JJ) et le résumé. Passer `draft: true` à `draft: false`. Écrire le texte en Markdown sous la deuxième ligne `---`.

Les notes sont classées de la plus récente à la plus ancienne. La dernière apparaît aussi sur la page d’accueil. Les brouillons restent dans le dépôt public : ne pas y mettre d’informations confidentielles.

Chaque modification poussée sur `main` déclenche la reconstruction et la publication avec GitHub Actions. Aucun abonnement ni service de base de données n’est nécessaire.

## Aperçu local

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m http.server 8000 --directory dist
```

Ouvrir http://localhost:8000. Relancer la construction après une modification.

Les sources sont à la racine ; le dossier `dist/` est généré et n’est pas suivi par Git. Le CV de référence dans `Aide_au_site/` n’est pas suivi non plus ; seule la copie destinée au site est publiée.

## Visuels et typographie

- `assets/research/ssm-cgm.png` : figure d’architecture extraite de l’article SSM-CGM, arXiv:2510.04386.
- Les deux fichiers SVG de recherche sont des schémas conceptuels créés pour le site, pas des graphiques de résultats expérimentaux.
- Polices DM Sans et Newsreader, hébergées localement. Licences SIL Open Font License conservées dans `assets/fonts/`.
