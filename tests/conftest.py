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
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from inscription import supprimer_compte
from pages.login_page import LoginPage

APP_ROOT = Path(__file__).resolve().parent.parent

# Charge .env en local (absent en CI : les variables y sont fournies par le workflow).
# override=False : une variable deja definie dans l'environnement (ex: par la CI) n'est jamais ecrasee.
load_dotenv(APP_ROOT / ".env", override=False)


def _port_libre():
    """Port TCP local a utiliser pour le serveur de ce process, sans jamais l'ouvrir
    puis le relacher (voir historique des deux tentatives precedentes ci-dessous).

    Sous pytest-xdist, chaque worker est un process separe : s'ils demarrent chacun
    leur propre serveur local sur le meme port, ils se marchent dessus (port deja
    utilise, ou pire : un worker termine "son" serveur pendant qu'un autre s'en sert
    encore).

    Tentative 1 : port calcule a partir de l'index du worker xdist (PYTEST_XDIST_WORKER,
    ex: "gw0"). Observe en CI (Linux) : au moins deux workers sont retombes sur le meme
    port par defaut malgre ce calcul, collision reproductible a chaque rerun.

    Tentative 2 : demander un port libre a l'OS via bind(0) puis le relacher aussitot.
    Toujours en CI : plusieurs workers ont obtenu EXACTEMENT le meme port (ex: 42015)
    pour un run complet. Cause : fenetre de course classique de ce pattern -- entre le
    moment ou un worker relache le port "libre" qu'il vient de sonder et le moment ou
    son serveur Flask le reprend reellement, un autre worker peut sonder et recevoir ce
    meme numero fraichement libere.

    Solution retenue : deriver le port du PID du process courant. Chaque worker xdist
    est un process distinct, son PID est garanti unique parmi les processus qui tournent
    en meme temps sur la machine -- aucun socket ouvert puis relache, donc aucune fenetre
    de course possible.
    """
    return 20000 + (os.getpid() % 20000)


_BASE_URL_EXPLICITE = os.getenv("BASE_URL")
if _BASE_URL_EXPLICITE:
    # BASE_URL fixee volontairement (ex: serveur partage en CI) : on la respecte telle quelle.
    BASE_URL = _BASE_URL_EXPLICITE
    PORT_SERVEUR_LOCAL = None
else:
    PORT_SERVEUR_LOCAL = _port_libre()
    BASE_URL = f"http://localhost:{PORT_SERVEUR_LOCAL}"

# Propage vers os.environ pour que le reste du code de ce process (ex: inscription.supprimer_compte,
# qui relit BASE_URL via os.getenv) cible le meme serveur, y compris sous xdist.
os.environ["BASE_URL"] = BASE_URL

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

    port = PORT_SERVEUR_LOCAL if PORT_SERVEUR_LOCAL is not None else 8000
    processus = subprocess.Popen(
        [sys.executable, "server.py"],
        cwd=APP_ROOT,
        env={**os.environ, "BASE_URL": BASE_URL, "PORT": str(port)},
    )
    try:
        _attendre_serveur_pret(BASE_URL)
        yield BASE_URL
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
