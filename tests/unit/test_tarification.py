import pytest

from tarification import prix_inscription


@pytest.mark.unit
@pytest.mark.parametrize(
    "nb_cours, prix_attendu",
    [
        pytest.param(1, 40.0, id="1-cours-sans-remise"),
        pytest.param(2, 80.0, id="2-cours-sans-remise"),
        pytest.param(3, 102.0, id="3-cours-remise-15-pourcent"),
        pytest.param(5, 170.0, id="5-cours-remise-15-pourcent"),
    ],
)
def test_prix_inscription(nb_cours, prix_attendu):
    prix = prix_inscription(nb_cours)
    assert prix == prix_attendu, (
        f"Pour {nb_cours} cours, prix attendu {prix_attendu}, recu {prix}"
    )
