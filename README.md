# Application de demo — Code un max

Mini-plateforme Flask fournie pour les exercices du module TESE860.

## Lancement

```bash
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\Activate.ps1       # Windows PowerShell
pip install -r requirements.txt
python -m app.server
```

L'application ecoute par defaut sur **http://localhost:8000**.

Variables d'environnement utiles :

| Variable | Defaut | Description |
|---|---|---|
| `PORT` | `8000` | Port du serveur |
| `BASE_URL` | `http://localhost:8000` | URL utilisee par les tests |

## Comptes de test

| Email | Mot de passe | Role |
|---|---|---|
| `eleve.test@codeunmax.fr` | `Test1234!` | Apprenant (tests POM) |
| `apprenant@codeunmax.fr` | `MotDePasse123` | Apprenant (tests cross-browser) |
| `eleve@codeunmax.fr` | `Test1234!` | Apprenant (tests login refuse) |

## Routes disponibles

- `/login` — formulaire de connexion (`#email`, `#password`, `#submit`)
- `/dashboard` — tableau de bord (`#dashboard`, `h1.dashboard-title`, `#logout`)
- `/catalogue` — liste des cours (`.cours-card`, `.cours-titre`)
- `/cours/<id>/inscription` — formulaire d'inscription (`#nom`, `#motivation`, `.alert-success`)
- `DELETE /api/users?email=...` — suppression d'un compte de test (204)

## Modules de logique metier

- `app/validation.py` — `email_valide()` (test unitaire, exercice 01)
- `app/tarification.py` — `prix_inscription()` (TDD, exercice 04)
- `app/inscription.py` — `inscrire_cours_payant()` (mock paiement, exercice 03)
