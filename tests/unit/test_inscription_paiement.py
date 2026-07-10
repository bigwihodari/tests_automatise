import pytest
import responses

from inscription import inscrire_cours_payant

BASE_URL = "http://localhost:8000"
PAYMENT_API = "https://paiement.codeunmax.fr/api/charge"


@pytest.mark.unit
@responses.activate
def test_inscription_payante_avec_paiement_accepte(apprenant):
    # Arrange
    responses.add(responses.POST, PAYMENT_API, json={"status": "accepte"}, status=200)

    # Act
    resultat = inscrire_cours_payant(BASE_URL, PAYMENT_API, apprenant, "python-avance")

    # Assert
    assert resultat["ok"] is True, f"Un paiement accepte (200) devrait reussir l'inscription, recu : {resultat}"
    assert "confirmee" in resultat["message"].lower(), resultat["message"]


@pytest.mark.unit
@responses.activate
def test_inscription_payante_avec_paiement_refuse(apprenant):
    # Arrange
    responses.add(responses.POST, PAYMENT_API, json={"error": "carte refusee"}, status=402)

    # Act
    resultat = inscrire_cours_payant(BASE_URL, PAYMENT_API, apprenant, "python-avance")

    # Assert
    assert resultat["ok"] is False, f"Un paiement refuse (402) ne devrait pas confirmer l'inscription, recu : {resultat}"
    assert "refuse" in resultat["message"].lower(), (
        f"Le message devrait indiquer un refus de paiement, recu : '{resultat['message']}'"
    )
