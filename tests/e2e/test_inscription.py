import pytest


@pytest.mark.e2e
def test_inscription_a_un_cours_affiche_la_confirmation(session_connectee):
    # Arrange
    dashboard = session_connectee
    catalogue = dashboard.ouvrir_catalogue()
    titres = catalogue.titres_des_cours()
    assert titres, "Le catalogue devrait contenir au moins un cours pour pouvoir s'inscrire"
    premier_cours = titres[0]

    # Act
    inscription = catalogue.s_inscrire_au_cours(premier_cours)
    inscription.valider_inscription(nom="Alice Dupont", motivation="Envie d'apprendre")

    # Assert
    message = inscription.message_confirmation()
    assert "confirmee" in message.lower() or "enregistree" in message.lower(), (
        f"Le message de confirmation d'inscription est inattendu : '{message}'"
    )
