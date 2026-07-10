import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from pages.login_page import LoginPage

APP_ROOT = Path(__file__).resolve().parent.parent
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

# Identifiants du compte de test, centralises ici : un seul endroit a changer.
COMPTE_TEST_EMAIL = os.getenv("TEST_EMAIL", "eleve.test@codeunmax.fr")
COMPTE_TEST_MOT_DE_PASSE = os.getenv("TEST_PASSWORD", "Test1234!")


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
