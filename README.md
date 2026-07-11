# Code un max, plateforme de cours et suite de tests automatises

Mini plateforme Flask et sa suite de tests (unitaires, mockes, E2E cross-browser) fournies pour le projet fil rouge du module TESE860.

## Prerequis

- Python 3.11 ou plus recent
- Git
- Google Chrome installe (pour les tests E2E)
- Mozilla Firefox installe (pour les tests E2E cross-browser)

## Cloner le depot

```bash
git clone https://github.com/bigwihodari/tests_automatise.git
cd tests_automatise
```

## Installer

```bash
python -m venv .venv

# Activer le venv
source .venv/bin/activate          # Linux/macOS
.venv\Scripts\Activate.ps1         # Windows PowerShell
.venv\Scripts\activate.bat         # Windows cmd.exe

pip install -r requirements.txt
```

Copier `.env.example` en `.env` si vous voulez personnaliser les variables locales (facultatif, des valeurs par defaut fonctionnelles sont deja utilisees si `.env` est absent) :

```bash
cp .env.example .env    # Linux/macOS
copy .env.example .env  # Windows
```

## Lancer l'application seule

```bash
python server.py
```

L'application ecoute par defaut sur **http://localhost:8000**. Ce n'est pas necessaire pour lancer les tests : la suite demarre et arrete automatiquement son propre serveur si besoin (voir fixture `live_server` dans `tests/conftest.py`).

## Lancer les tests

Toutes les commandes ci-dessous s'executent depuis la racine du depot, avec le venv active.

Suite complete (unitaires et E2E, sequentiel) :

```bash
pytest -v
```

Seulement les tests unitaires (rapides, sans navigateur ni reseau) :

```bash
pytest -v -m unit
```

Seulement les tests E2E (Selenium, Chrome et Firefox) :

```bash
pytest -v -m e2e
```

Suite complete en parallele, avec couverture de code et rapport HTML (commande utilisee en CI) :

```bash
pytest --cov --cov-report=html --cov-report=term-missing -n auto --junitxml=rapport-junit.xml --html=rapport.html --self-contained-html
```

Deboguer un test E2E avec un navigateur visible (au lieu du mode headless par defaut) :

```bash
# PowerShell
$env:HEADLESS="0"; pytest -v -m e2e

# cmd.exe
set HEADLESS=0 && pytest -v -m e2e

# Linux/macOS
HEADLESS=0 pytest -v -m e2e
```

## Lire le rapport

Apres un run avec `--html` ou `--cov-report=html` :

- `rapport.html` : rapport de tests auto-contenu (ouvrir directement dans un navigateur).
- `htmlcov/index.html` : rapport de couverture de code navigable, module par module.

En CI (GitHub Actions), ces deux rapports sont publies comme artefacts telechargeables depuis l'onglet **Actions** de chaque execution (`rapport-tests` et `rapport-couverture`), avec le rapport JUnit (`rapport-junit`).

Un instantane du dernier rapport (tests et couverture) est aussi versionne dans le depot, consultable directement sans rien executer :

- `rapport/rapport.html`
- `rapport/couverture/index.html`

## Comptes de test

| Email | Mot de passe | Role |
|---|---|---|
| `eleve.test@codeunmax.fr` | `Test1234!` | Apprenant (compte principal utilise par les tests) |
| `apprenant@codeunmax.fr` | `MotDePasse123` | Apprenant (tests cross-browser) |
| `eleve@codeunmax.fr` | `Test1234!` | Apprenant (tests login refuse) |

## Routes disponibles

- `/login` : formulaire de connexion (`#email`, `#password`, `#submit`)
- `/dashboard` : tableau de bord (`#dashboard`, `h1.dashboard-title`, `#logout`)
- `/catalogue` : liste des cours (`.cours-card`, `.cours-titre`)
- `/cours/<id>/inscription` : formulaire d'inscription (`#nom`, `#motivation`, `.alert-success`)
- `DELETE /api/users?email=...` : suppression d'un compte de test (204)

## Structure du projet

```
.
├── server.py                  Application Flask (routes, pages)
├── validation.py               email_valide()
├── tarification.py             prix_inscription() (remise fidelite, developpe en TDD)
├── inscription.py              inscrire_cours_payant() et supprimer_compte()
├── pages/                      Page Object Model (BasePage + une classe par page)
├── tests/
│   ├── conftest.py             Fixtures partagees : driver, live_server, session_connectee, apprenant
│   ├── unit/                   Tests unitaires et mockes (marqueur @pytest.mark.unit)
│   └── e2e/                    Tests de bout en bout Selenium (marqueur @pytest.mark.e2e)
├── .github/workflows/ci.yml    Pipeline GitHub Actions (lint, suite complete)
├── pytest.ini                  Configuration pytest
└── .coveragerc                 Configuration de la couverture de code
```

## Pipeline CI

Chaque `push` et chaque `pull_request` declenchent automatiquement le workflow GitHub Actions :

1. **lint** : `ruff check .`
2. **tests_complets** : suite complete (unitaires et E2E, Chrome et Firefox) en parallele, avec couverture de code. Publie les rapports en artefacts.

## Couverture de code

Cible convenue : 90 %, appliquee sur les modules de logique metier (`validation.py`, `tarification.py`, `inscription.py`). `server.py` est exclu de cette mesure car il tourne dans un sous-processus separe pendant les tests E2E (voir `.coveragerc`) ; il reste couvert fonctionnellement par les scenarios E2E.
