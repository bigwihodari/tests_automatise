import pytest


@pytest.mark.e2e
def test_deconnexion_retourne_a_l_ecran_de_login(session_connectee):
    # Arrange
    dashboard = session_connectee

    # Act
    login_page = dashboard.se_deconnecter()

    # Assert
    assert login_page.est_present(login_page.EMAIL), (
        "L'ecran de connexion (champ email) devrait etre affiche apres deconnexion"
    )
    url_actuelle = dashboard.driver.current_url
    assert "/login" in url_actuelle, f"URL inattendue apres deconnexion : {url_actuelle}"
