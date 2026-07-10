from selenium.webdriver.common.by import By

from .base_page import BasePage


class InscriptionPage(BasePage):
    NOM = (By.ID, "nom")
    MOTIVATION = (By.ID, "motivation")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit']")
    CONFIRMATION = (By.ID, "flash")

    def valider_inscription(self, nom, motivation=""):
        self.saisir_texte(self.NOM, nom)
        if motivation:
            self.saisir_texte(self.MOTIVATION, motivation)
        self.cliquer(self.SUBMIT)
        return self

    def message_confirmation(self):
        return self.lire_texte(self.CONFIRMATION)
