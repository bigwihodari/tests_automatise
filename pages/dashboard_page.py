from selenium.webdriver.common.by import By

from .base_page import BasePage


class DashboardPage(BasePage):
    TITRE = (By.CLASS_NAME, "dashboard-title")
    LIEN_CATALOGUE = (By.LINK_TEXT, "Catalogue")
    LIEN_LOGOUT = (By.ID, "logout")

    def est_affiche(self):
        return self.est_present(self.TITRE)

    def ouvrir_catalogue(self):
        self.cliquer(self.LIEN_CATALOGUE)

        from .catalogue_page import CataloguePage

        return CataloguePage(self.driver, self.base_url)

    def se_deconnecter(self):
        self.cliquer(self.LIEN_LOGOUT)

        from .login_page import LoginPage

        return LoginPage(self.driver, self.base_url)
