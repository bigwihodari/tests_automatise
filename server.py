import os

from flask import Flask, redirect, render_template_string, request, url_for

app = Flask(__name__)

COMPTES = {
    "eleve.test@codeunmax.fr": "Test1234!",
    "apprenant@codeunmax.fr": "MotDePasse123",
    "eleve@codeunmax.fr": "Test1234!",
}

COURS = [
    {"id": "python-avance", "titre": "Python avance"},
    {"id": "selenium-nuls", "titre": "Selenium pour les nuls"},
]

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head><title>Code un max — Connexion</title></head>
<body>
  <h1>Code un max</h1>
  {% if erreur %}
  <div class="alert-error alert-danger">{{ erreur }}</div>
  {% endif %}
  <form method="post" novalidate>
    <label>Email <input id="email" name="email" type="email"></label>
    <label>Mot de passe <input id="password" name="password" type="password"></label>
    <button id="submit" type="submit">Se connecter</button>
  </form>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head><title>Code un max — Tableau de bord</title></head>
<body>
  <div id="dashboard">
    <h1 class="dashboard-title">Mon tableau de bord</h1>
    <a href="{{ url_for('catalogue') }}">Catalogue</a>
    <a id="logout" href="{{ url_for('logout') }}">Deconnexion</a>
  </div>
</body>
</html>
"""

CATALOGUE_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head><title>Code un max — Catalogue</title></head>
<body>
  <h1>Catalogue de cours</h1>
  {% for cours in cours %}
  <div class="cours-card">
    <h3 class="cours-titre">{{ cours.titre }}</h3>
    <a href="{{ url_for('inscription', cours_id=cours.id) }}">S inscrire</a>
  </div>
  {% endfor %}
</body>
</html>
"""

INSCRIPTION_HTML = """
<!DOCTYPE html>
<html lang="fr">
<head><title>Code un max — Inscription</title></head>
<body>
  <h1>Inscription — {{ titre }}</h1>
  {% if message %}
  <div id="flash" class="alert-success">{{ message }}</div>
  {% else %}
  <form method="post">
    <label>Nom <input id="nom" name="nom" type="text"></label>
    <label>Motivation <textarea id="motivation" name="motivation"></textarea></label>
    <button type="submit">Valider</button>
  </form>
  {% endif %}
</body>
</html>
"""


@app.route("/login", methods=["GET", "POST"])
def login():
    erreur = None
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        if not email or not password:
            erreur = "Les champs obligatoires doivent etre remplis."
        elif COMPTES.get(email) != password:
            erreur = "Identifiants invalides : mot de passe incorrect."
        else:
            return redirect(url_for("dashboard"))
    return render_template_string(LOGIN_HTML, erreur=erreur)


@app.route("/dashboard")
def dashboard():
    return render_template_string(DASHBOARD_HTML)


@app.route("/logout")
def logout():
    return redirect(url_for("login"))


@app.route("/catalogue")
def catalogue():
    return render_template_string(CATALOGUE_HTML, cours=COURS)


@app.route("/cours/<cours_id>/inscription", methods=["GET", "POST"])
def inscription(cours_id):
    cours = next((c for c in COURS if c["id"] == cours_id), None)
    if cours is None:
        cours = {"id": cours_id, "titre": cours_id.replace("-", " ").title()}
    message = None
    if request.method == "POST":
        message = "Inscription enregistree. Inscription confirmee."
    return render_template_string(INSCRIPTION_HTML, titre=cours["titre"], message=message)


@app.route("/api/users", methods=["DELETE"])
def supprimer_utilisateur():
    return ("", 204)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="127.0.0.1", port=port, debug=False)
