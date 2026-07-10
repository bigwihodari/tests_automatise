from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

TIMEOUT_PAR_DEFAUT = 10


class BasePage:
    """Interactions Selenium generiques, sans connaissance des locators d'une page precise."""

    def __init__(self, driver, base_url=""):
        self.driver = driver
        self.base_url = base_url

    def ouvrir(self, chemin=""):
        self.driver.get(f"{self.base_url}{chemin}")

    def _attendre(self, locator, condition=EC.presence_of_element_located, timeout=TIMEOUT_PAR_DEFAUT):
        return WebDriverWait(self.driver, timeout).until(condition(locator))

    def cliquer(self, locator):
        element = self._attendre(locator, EC.element_to_be_clickable)
        element.click()

    def saisir_texte(self, locator, texte):
        element = self._attendre(locator, EC.visibility_of_element_located)
        element.clear()
        element.send_keys(texte)

    def lire_texte(self, locator):
        element = self._attendre(locator, EC.visibility_of_element_located)
        return element.text

    def est_present(self, locator, timeout=TIMEOUT_PAR_DEFAUT):
        try:
            self._attendre(locator, EC.presence_of_element_located, timeout)
            return True
        except TimeoutException:
            return False

    def titre(self):
        return self.driver.title
