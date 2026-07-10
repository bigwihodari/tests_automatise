from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .base_page import BasePage


class CataloguePage(BasePage):
    URL_PATH = "/catalogue"

    CARTES = (By.CLASS_NAME, "cours-card")
    TITRES = (By.CLASS_NAME, "cours-titre")

    def charger(self):
        self.ouvrir(self.URL_PATH)
        return self

    def titres_des_cours(self):
        return [e.text for e in self.driver.find_elements(*self.TITRES)]

    def s_inscrire_au_cours(self, nom_cours):
        cartes = self._attendre(self.CARTES, EC.presence_of_all_elements_located)
        for carte in cartes:
            titre = carte.find_element(*self.TITRES).text.strip()
            if titre == nom_cours:
                carte.find_element(By.TAG_NAME, "a").click()

                from .inscription_page import InscriptionPage

                return InscriptionPage(self.driver, self.base_url)

        raise ValueError(f"Cours introuvable dans le catalogue : {nom_cours}")
