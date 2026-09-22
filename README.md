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

### Contraintes du compte gratuit à respecter

- **Quota disque ~500 Mo** : ne jamais uploader `.venv/`, `node_modules/` ni
  `staticfiles/` — tout est dans `.gitignore`. Le venv Python est recréé
  directement sur PythonAnywhere (étape 3 ci-dessous).
- **Pas de Node.js et accès réseau sortant limité (liste blanche)** : le build
  Tailwind (`npm`/`postcss`) doit se faire **en local**, jamais sur le
  serveur. C'est pourquoi `theme/static/css/dist/styles.css` est committé —
  le serveur n'a qu'à servir ce fichier déjà compilé (voir « Build Tailwind
  pour la production » ci-dessus — à refaire et committer avant chaque
  déploiement si des templates ont changé).
- **PostgreSQL externe potentiellement bloqué** sur le plan gratuit (accès
  réseau sortant restreint à une liste blanche). À vérifier avant toute
  bascule PostgreSQL ; alternative : la base MySQL fournie par
  PythonAnywhere, ou un plan payant. Par défaut (`DATABASE_URL` non défini),
  le site tourne en SQLite — suffisant pour un portfolio à faible trafic.
- **Les fichiers médias (`media/`) ne sont servis par Django qu'en
  `DEBUG=True`** (`config/urls.py`) : en production, c'est PythonAnywhere qui
  doit les servir via un mapping statique (étape 8), sinon les images
  uploadées via l'admin (ex. captures de projets) renverront une 404.

### Procédure

1. **Créer le compte** sur [pythonanywhere.com](https://www.pythonanywhere.com)
   (plan *Beginner* gratuit) — le site sera accessible sur
   `<votre-compte>.pythonanywhere.com`.

2. **Cloner le dépôt** depuis une console Bash PythonAnywhere (onglet
   *Consoles* → *Bash*) :
   ```bash
   git clone https://github.com/fokouarnaud/django-portfolio.git
   cd django-portfolio
   ```

3. **Créer et activer le virtualenv, puis installer les dépendances de
   prod** (`mkvirtualenv` est fourni par `virtualenvwrapper`, préinstallé
   sur PythonAnywhere) :
   ```bash
   mkvirtualenv --python=python3.12 django-portfolio-env
   # mkvirtualenv crée ET active le venv dans la foulée — le prompt affiche
   # un préfixe (django-portfolio-env) tant qu'il est actif dans cette console.
   pip install -r requirements/prod.txt
   ```
   Si vous rouvrez une nouvelle console Bash plus tard (le venv n'y est
   **pas** actif automatiquement), réactivez-le avant toute commande
   `manage.py` :
   ```bash
   workon django-portfolio-env
   ```

4. **Configurer les variables d'environnement.** Créer un `.env` à la racine
   du projet cloné (il reste sur le serveur, jamais committé — déjà dans
   `.gitignore`) :
   ```bash
   cat > .env <<'EOF'
   SECRET_KEY=<générer une valeur, voir "Démarrage local" ci-dessus>
   DEBUG=False
   ALLOWED_HOSTS=<votre-compte>.pythonanywhere.com
   EOF
   ```
   Ajouter `DATABASE_URL=...` dans ce même fichier uniquement si vous basculez
   vers PostgreSQL/MySQL (voir « Bascule SQLite → PostgreSQL » ci-dessus).

5. **Appliquer les migrations et créer le superutilisateur** :
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collecter les fichiers statiques** (commande Python pure, fonctionne
   normalement sur le plan gratuit) :
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Créer l'application web** : onglet *Web* → *Add a new web app* →
   choisir le domaine gratuit proposé → **Manual configuration** (pas
   « Django », pour garder le contrôle du fichier WSGI) → sélectionner la
   même version de Python qu'à l'étape 3 (3.12).
   - Dans la section *Virtualenv*, renseigner le chemin du venv créé à
     l'étape 3 (ex. `/home/<votre-compte>/.virtualenvs/django-portfolio-env`).
   - Dans la section *Code*, renseigner *Source code*
     (`/home/<votre-compte>/django-portfolio`) et *Working directory*
     (idem).

8. **Éditer le fichier WSGI** généré par PythonAnywhere (lien cliquable dans
   l'onglet *Web*, section *Code*) : remplacer son contenu par un import du
   `application` du projet, en pointant vers les settings de prod :
   ```python
   import os
   import sys

   path = "/home/<votre-compte>/django-portfolio"
   if path not in sys.path:
       sys.path.insert(0, path)

   os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings.prod"

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```

9. **Mapper les fichiers statiques et médias** (onglet *Web*, section
   *Static files*), pour de meilleures performances et parce que les médias
   ne sont pas servis par Django en prod (voir contraintes ci-dessus) :

   | URL       | Directory                                        |
   |-----------|---------------------------------------------------|
   | `/static/` | `/home/<votre-compte>/django-portfolio/staticfiles` |
   | `/media/`  | `/home/<votre-compte>/django-portfolio/media`       |

10. **Recharger l'application** : bouton vert *Reload* en haut de l'onglet
    *Web*. Le site est alors accessible sur
    `https://<votre-compte>.pythonanywhere.com`.

### Récapitulatif : commandes console (Bash PythonAnywhere)

Toutes les commandes des étapes 2 à 6 ci-dessus, à saisir dans l'ordre dans
une console Bash PythonAnywhere (onglet *Consoles* → *Bash*) — les étapes 7
à 10 se font, elles, dans l'onglet *Web* (interface graphique, pas de
console) :

```bash
# 2. Cloner le dépôt
git clone https://github.com/fokouarnaud/django-portfolio.git
cd django-portfolio

# 3. Créer + activer le virtualenv, installer les dépendances de prod
mkvirtualenv --python=python3.12 django-portfolio-env
pip install -r requirements/prod.txt

# 4. Variables d'environnement (adapter SECRET_KEY et <votre-compte>)
cat > .env <<'EOF'
SECRET_KEY=<générer une valeur, voir "Démarrage local" ci-dessus>
DEBUG=False
ALLOWED_HOSTS=<votre-compte>.pythonanywhere.com
EOF

# 5. Migrations + superutilisateur (commande interactive : suit des invites)
python manage.py migrate
python manage.py createsuperuser

# 6. Fichiers statiques
python manage.py collectstatic --noinput
```

Dans une console Bash rouverte plus tard, réactiver le venv avant toute
commande `manage.py` :

```bash
workon django-portfolio-env
cd django-portfolio
```

### Mettre à jour un déploiement existant

Depuis une console Bash PythonAnywhere, se positionner à la racine du projet
et activer le venv avant toute commande `manage.py` :

```bash
cd ~/django-portfolio
workon django-portfolio-env

git pull
pip install -r requirements/prod.txt   # si requirements/prod.txt a changé
python manage.py migrate               # si de nouvelles migrations existent
python manage.py collectstatic --noinput
```

Puis recharger l'application depuis l'onglet *Web* (bouton *Reload*) —
indispensable après tout `git pull`, PythonAnywhere ne redémarre pas
l'application tout seul.

## Structure

```
config/            settings (base/dev/prod), urls, wsgi/asgi
apps/projects/      modèle Project, admin, filtres, vues, tests
apps/core/           accueil, à propos
theme/              app django-tailwind (styles.css source + CSS compilé)
templates/          templates globaux (base, includes, projects, core)
requirements/       base / dev / prod
```
