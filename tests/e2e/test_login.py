import pytest

from pages.login_page import LoginPage

COMPTE_VALIDE_EMAIL = "eleve.test@codeunmax.fr"
COMPTE_VALIDE_MOT_DE_PASSE = "Test1234!"


@pytest.mark.e2e
def test_login_valide_arrive_sur_dashboard(driver, live_server):
    # Arrange
    login_page = LoginPage(driver, live_server).charger()

    # Act
    dashboard = login_page.login(COMPTE_VALIDE_EMAIL, COMPTE_VALIDE_MOT_DE_PASSE)

    # Assert
    assert dashboard.est_affiche(), "Le tableau de bord devrait s'afficher apres un login valide"


CAS_LOGIN_REFUSE = [
    pytest.param(
        COMPTE_VALIDE_EMAIL, "mauvais_mot_de_passe", "invalides", id="mauvais-mot-de-passe"
    ),
    pytest.param(
        "inconnu@codeunmax.fr", "peu-importe-123", "invalides", id="utilisateur-inconnu"
    ),
    pytest.param("", COMPTE_VALIDE_MOT_DE_PASSE, "obligatoires", id="email-vide"),
    pytest.param(COMPTE_VALIDE_EMAIL, "", "obligatoires", id="mot-de-passe-vide"),
]


@pytest.mark.e2e
@pytest.mark.parametrize("email, mot_de_passe, fragment_attendu", CAS_LOGIN_REFUSE)
def test_login_refuse(driver, live_server, email, mot_de_passe, fragment_attendu):
    # Arrange
    login_page = LoginPage(driver, live_server).charger()

    # Act
    resultat = login_page.login(email, mot_de_passe)

    # Assert
    assert resultat is login_page, "Un login invalide doit laisser l'utilisateur sur la page de connexion"
    message = resultat.message_erreur()
    assert fragment_attendu in message.lower(), (
        f"Le message d'erreur devrait contenir '{fragment_attendu}', recu : '{message}'"
    )
