import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

import pytest
import requests
from dotenv import load_dotenv
from faker import Faker
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from inscription import supprimer_compte
from pages.login_page import LoginPage

APP_ROOT = Path(__file__).resolve().parent.parent

# Charge .env en local (absent en CI : les variables y sont fournies par le workflow).
# override=False : une variable deja definie dans l'environnement (ex: par la CI) n'est jamais ecrasee.
load_dotenv(APP_ROOT / ".env", override=False)

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Identifiants du compte de test, centralises ici : un seul endroit a changer.
COMPTE_TEST_EMAIL = os.getenv("TEST_EMAIL", "eleve.test@codeunmax.fr")
COMPTE_TEST_MOT_DE_PASSE = os.getenv("TEST_PASSWORD", "Test1234!")

# Seed fixe : les donnees generees par Faker restent les memes d'un run a l'autre.
FAKER_SEED = 20260709
_faker = Faker("fr_FR")
Faker.seed(FAKER_SEED)


def _serveur_deja_actif(url):
    try:
        requests.get(url, timeout=1)
        return True
    except requests.RequestException:
        return False


def _attendre_serveur_pret(url, timeout=10):
    deadline = time.time() + timeout
    while time.time() < deadline:
        if _serveur_deja_actif(url):
            return
        time.sleep(0.2)
    raise RuntimeError(f"Le serveur n'a pas demarre a temps sur {url}")


@pytest.fixture(scope="session")
def live_server():
    """Fournit l'URL de base d'un serveur Flask actif, en le demarrant si besoin."""
    if _serveur_deja_actif(BASE_URL):
        yield BASE_URL
        return

    processus = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=APP_ROOT,
        env={**os.environ, "BASE_URL": BASE_URL},
    )
    try:
        _attendre_serveur_pret(BASE_URL)
        yield BASE_URL
    finally:
        processus.terminate()
        processus.wait(timeout=5)


@pytest.fixture
def driver():
    """Fournit un WebDriver Chrome, headless par defaut (HEADLESS=0 pour deboguer en local)."""
    headless = os.getenv("HEADLESS", "1") != "0"
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    navigateur = webdriver.Chrome(options=options)
    # Strategie d'attente unique : attentes explicites (WebDriverWait) via BasePage,
    # pas d'implicit wait ici pour ne pas cumuler les deux mecanismes.
    try:
        yield navigateur
    finally:
        navigateur.quit()


@pytest.fixture
def session_connectee(driver, live_server):
    """Renvoie un DashboardPage deja authentifie avec le compte de test centralise."""
    return LoginPage(driver, live_server).charger().login(
        COMPTE_TEST_EMAIL, COMPTE_TEST_MOT_DE_PASSE
    )


@pytest.fixture(scope="function")
def apprenant():
    """Genere un apprenant (nom, email, mot de passe) via Faker, seed fixe pour reproductibilite.

    Scope 'function' : un compte frais a chaque test. L'email est prefixe par un uuid
    pour rester unique malgre le seed fixe. Le compte est supprime apres le test (teardown)
    pour ne pas polluer les executions suivantes.
    """
    donnees = {
        "nom": _faker.name(),
        "email": f"{uuid.uuid4().hex[:8]}.{_faker.user_name()}@example.com",
        "mot_de_passe": _faker.password(length=12),
    }
    yield donnees
    supprimer_compte(donnees["email"])
