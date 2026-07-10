import pytest

from pages.catalogue_page import CataloguePage

COURS_ATTENDU = "Python avance"


@pytest.mark.e2e
def test_catalogue_affiche_les_cours_attendus(driver, live_server):
    # Arrange
    catalogue = CataloguePage(driver, live_server)

    # Act
    catalogue.charger()
    titres = catalogue.titres_des_cours()

    # Assert
    assert titres, "Le catalogue devrait afficher au moins un cours"
    assert COURS_ATTENDU in titres, (
        f"Le cours '{COURS_ATTENDU}' est absent du catalogue, cours trouves : {titres}"
    )
