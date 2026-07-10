import pytest

from validation import email_valide


@pytest.mark.unit
def test_email_valide_avec_adresse_correcte():
    adresse = "alice@example.com"
    resultat = email_valide(adresse)
    assert resultat is True, f"'{adresse}' devrait etre valide, recu : {resultat}"


@pytest.mark.unit
def test_email_valide_avec_adresse_sans_arobase():
    adresse = "alice.example.com"
    resultat = email_valide(adresse)
    assert resultat is False, f"'{adresse}' (sans @) devrait etre invalide, recu : {resultat}"
