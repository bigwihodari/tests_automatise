from selenium.webdriver.common.by import By

from .base_page import BasePage


class LoginPage(BasePage):
    URL_PATH = "/login"

    EMAIL = (By.ID, "email")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.ID, "submit")
    ERREUR = (By.CSS_SELECTOR, ".alert-error")

    def charger(self):
        self.ouvrir(self.URL_PATH)
        return self

    def login(self, email, mot_de_passe):
        self.saisir_texte(self.EMAIL, email)
        self.saisir_texte(self.PASSWORD, mot_de_passe)
        self.cliquer(self.SUBMIT)

        if self.est_present(self.ERREUR, timeout=3):
            return self

        from .dashboard_page import DashboardPage

        return DashboardPage(self.driver, self.base_url)

    def message_erreur(self):
        return self.lire_texte(self.ERREUR)
