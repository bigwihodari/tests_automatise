import os
import random
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
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from inscription import supprimer_compte
from pages.login_page import LoginPage

APP_ROOT = Path(__file__).resolve().parent.parent

# Charge .env en local (absent en CI : les variables y sont fournies par le workflow).
# override=False : une variable deja definie dans l'environnement (ex: par la CI) n'est jamais ecrasee.
load_dotenv(APP_ROOT / ".env", override=False)


_BASE_URL_EXPLICITE = os.getenv("BASE_URL")

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


def _demarrer_serveur_local(max_tentatives=5):
    """Demarre server.py sur un port choisi au hasard, avec nouvelle tentative si ca rate.

    Sous pytest-xdist, chaque worker est un process separe qui demarre son propre
    serveur local : s'ils tombent sur le meme port, ils se marchent dessus (port deja
    utilise, ou pire : un worker termine "son" serveur pendant qu'un autre s'en sert
    encore).

    Deux methodes precedentes pour garantir un port unique par worker (calcul par index
    xdist, puis port sonde via bind(0)) ont chacune produit le meme symptome en CI
    (Linux) : plusieurs tests en erreur partageant tous le meme port. La cause exacte
    n'a pas pu etre confirmee (meme avec un diagnostic dedie qui ecrivait PID et
    PYTEST_XDIST_WORKER dans un fichier). Plutot que de deviner un troisieme schema
    cense garantir l'unicite a coup sur, cette version accepte qu'une collision de
    port puisse arriver et s'en remet : port aleatoire, verification qu'il repond
    vraiment, sinon nouvelle tentative avec un autre port. Auto-cicatrisant quelle que
    soit la cause reelle de la collision.
    """
    derniere_erreur = None
    for _ in range(max_tentatives):
        port = random.randint(20000, 60000)
        base_url = f"http://localhost:{port}"
        if _serveur_deja_actif(base_url):
            continue  # ce port est deja pris (par nous ou quelqu'un d'autre), on en tire un autre

        processus = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=APP_ROOT,
            env={**os.environ, "BASE_URL": base_url, "PORT": str(port)},
        )
        try:
            _attendre_serveur_pret(base_url, timeout=8)
            return processus, base_url
        except RuntimeError as erreur:
            derniere_erreur = erreur
            processus.terminate()
            processus.wait(timeout=5)

    raise RuntimeError(
        f"Impossible de demarrer un serveur local apres {max_tentatives} tentatives : {derniere_erreur}"
    )


@pytest.fixture(scope="session")
def live_server():
    """Fournit l'URL de base d'un serveur Flask actif, en le demarrant si besoin."""
    if _BASE_URL_EXPLICITE:
        # BASE_URL fixee volontairement (ex: serveur partage en CI) : on la respecte telle quelle.
        if _serveur_deja_actif(_BASE_URL_EXPLICITE):
            yield _BASE_URL_EXPLICITE
            return
        processus = subprocess.Popen(
            [sys.executable, "server.py"], cwd=APP_ROOT, env=os.environ
        )
        try:
            _attendre_serveur_pret(_BASE_URL_EXPLICITE)
            yield _BASE_URL_EXPLICITE
        finally:
            processus.terminate()
            processus.wait(timeout=5)
        return

    processus, base_url = _demarrer_serveur_local()
    # Propage vers os.environ pour que le reste du code de ce process (ex:
    # inscription.supprimer_compte, qui relit BASE_URL via os.getenv) cible ce serveur.
    os.environ["BASE_URL"] = base_url
    try:
        yield base_url
    finally:
        processus.terminate()
        processus.wait(timeout=5)


def _navigateur_chrome(headless):
    options = ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def _navigateur_firefox(headless):
    options = FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.add_argument("--width=1280")
    options.add_argument("--height=900")
    return webdriver.Firefox(options=options)


NAVIGATEURS = {
    "chrome": _navigateur_chrome,
    "firefox": _navigateur_firefox,
}


@pytest.fixture(params=["chrome", "firefox"])
def driver(request):
    """Fournit un WebDriver (Chrome ou Firefox selon le parametre), headless par defaut.

    Parametree : chaque test qui utilise cette fixture s'execute une fois par navigateur,
    avec un nom de test distinct (ex: test_xxx[chrome], test_xxx[firefox]).
    """
    headless = os.getenv("HEADLESS", "1") != "0"
    navigateur = NAVIGATEURS[request.param](headless)
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


def pytest_collection_modifyitems(items):
    """Applique un rerun cible, uniquement aux tests qui dependent du fixture 'driver'.

    Pourquoi : la stabilisation des tests E2E se fait d'abord via des attentes explicites
    (WebDriverWait, voir pages/base_page.py) : aucun 'time.sleep' fixe n'existe dans le
    code de page ou de test. Ce rerun n'est PAS la pour masquer un test qui echoue sur une
    assertion metier (celui-la echouera de la meme facon a chaque tentative).

    Il couvre une seule cause identifiee et documentee : le lancement du processus
    navigateur (Chrome/Firefox) echoue parfois pour des raisons d'environnement local
    (contention memoire/CPU au demarrage), independamment du code applicatif. Observe
    concretement pendant ce projet :
      - Chrome : SessionNotCreatedException "DevToolsActivePort file doesn't exist"
      - Firefox : WebDriverException "Process unexpectedly closed with status 0"
    Dans les deux cas, un simple retry a suffi (la deuxieme tentative passait).

    reruns=1 (pas 3) : un seul filet de securite, pas une machine a cacher les bugs.
    Les tests unitaires (aucun fixture 'driver') ne sont jamais concernes.
    """
    for item in items:
        if "driver" in item.fixturenames:
            item.add_marker(pytest.mark.flaky(reruns=1, reruns_delay=2))
