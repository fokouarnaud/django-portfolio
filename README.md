# Portfolio Django

Portfolio personnel minimaliste : liste de projets filtrable (tag, année, recherche),
paginée, gérée via l'admin Django. Front en Tailwind CSS, base SQLite en dev,
bascule PostgreSQL possible sans changement de code.

## Stack

- Django 5.2, apps `apps.projects` (modèle `Project`, tags via `django-taggit`,
  filtres via `django-filter`) et `apps.core` (accueil, à propos)
- `django-environ` pour la config par variables d'environnement (`.env`)
- `django-tailwind` pour le front (thème dans `theme/`)
- SQLite par défaut, `DATABASE_URL` pour basculer vers PostgreSQL

## Démarrage local

```bash
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash / macOS-Linux: source .venv/bin/activate
pip install -r requirements/dev.txt

cp .env.example .env
# éditer .env : générer une SECRET_KEY, ajuster NPM_BIN_PATH si besoin

python manage.py migrate
python manage.py createsuperuser
python manage.py tailwind install   # une fois, nécessite Node.js
python manage.py tailwind build     # ou `tailwind start` pour le mode watch

python manage.py runserver
```

Générer une `SECRET_KEY` :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## Tests

```bash
python manage.py test
```

Le projet suit une discipline TDD (test avant code) pour toute nouvelle
fonctionnalité — voir `apps/projects/tests.py` et `apps/core/tests.py`.

## Bascule SQLite → PostgreSQL

Aucune modification de code n'est nécessaire : `DATABASES` lit `DATABASE_URL`
via `django-environ` (`config/settings/base.py`).

1. Installer les dépendances de prod (inclut `psycopg2-binary`) :
   `pip install -r requirements/prod.txt`
2. Définir dans `.env` (ou les variables d'environnement du serveur) :
   `DATABASE_URL=postgres://user:password@host:5432/dbname`
3. `python manage.py migrate`

## Build Tailwind pour la production

Le CSS compilé (`theme/static/css/dist/`) est **committé dans le dépôt** — voir
la section déploiement ci-dessous pour la raison. Avant de déployer, reconstruire
après toute modification de template ou de `theme/static_src/src/styles.css` :

```bash
python manage.py tailwind build
git add theme/static/css/dist
```

## Réglages du site (admin)

`/admin/core/sitesettings/1/change/` (une seule instance, singleton) permet de
gérer, sans toucher au code :

- **Apparence** : police (`editorial` / `modern` / `classic`) et thème
  (`clair` / `sombre`) appliqués à tout le site. Les variantes sont déjà
  compilées dans `theme/static/css/dist/styles.css` (via des sélecteurs
  `:root[data-font=...]` / `:root[data-theme=...]`) — changer la valeur en
  admin n'exige donc **aucun rebuild Tailwind**.
- **Contact & réseaux** : numéro WhatsApp (lien `wa.me` généré
  automatiquement), lien YouTube, lien Facebook, lien vers la démo produit —
  affichés en pied de page uniquement s'ils sont renseignés.
- **Vidéo de présentation** : URL YouTube (`watch`, `youtu.be` ou `embed`,
  peu importe le format) intégrée sur la page d'accueil.

Pour ajouter une nouvelle police/thème, éditer `_GOOGLE_FONTS_URLS` et les
`choices` dans `apps/core/models.py`, puis ajouter le bloc CSS correspondant
dans `theme/static_src/src/styles.css` et relancer `tailwind build`.

## Déploiement (PythonAnywhere, compte gratuit)

Contraintes du compte gratuit PythonAnywhere à respecter :

- **Quota disque ~500 Mo** : ne jamais uploader `.venv/`, `node_modules/` ni
  `staticfiles/` — tout est dans `.gitignore`. Recréer un venv Python
  directement sur PythonAnywhere (`mkvirtualenv` + `pip install -r requirements/prod.txt`).
- **Pas de Node.js et accès réseau sortant limité (liste blanche)** : le build
  Tailwind (`npm`/`postcss`) doit se faire **en local**, jamais sur le serveur.
  C'est pourquoi `theme/static/css/dist/styles.css` est committé — le serveur
  n'a qu'à servir ce fichier déjà compilé.
- **`collectstatic` fonctionne normalement** sur PythonAnywhere (commande
  Python pure) :
  ```bash
  DJANGO_SETTINGS_MODULE=config.settings.prod python manage.py collectstatic --noinput
  ```
- **PostgreSQL externe potentiellement bloqué** sur le plan gratuit (accès
  réseau sortant restreint à une liste blanche). À vérifier avant la bascule
  PostgreSQL ; alternative : la base MySQL fournie par PythonAnywhere, ou un
  plan payant.
- Variables d'environnement à définir sur PythonAnywhere (onglet *Web* →
  fichier WSGI, ou un `.env` non committé) : `SECRET_KEY`, `DEBUG=False`,
  `ALLOWED_HOSTS=<votre-sous-domaine>.pythonanywhere.com`, `DATABASE_URL`
  si PostgreSQL/MySQL.
- Le fichier WSGI généré par PythonAnywhere doit pointer vers
  `config.settings.prod` (variable `DJANGO_SETTINGS_MODULE`).

## Structure

```
config/            settings (base/dev/prod), urls, wsgi/asgi
apps/projects/      modèle Project, admin, filtres, vues, tests
apps/core/           accueil, à propos
theme/              app django-tailwind (styles.css source + CSS compilé)
templates/          templates globaux (base, includes, projects, core)
requirements/       base / dev / prod
```
