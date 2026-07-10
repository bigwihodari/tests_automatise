import pytest
import responses
from requests.exceptions import ConnectionError as RequestsConnectionError

from inscription import supprimer_compte


@pytest.mark.unit
@responses.activate
def test_supprimer_compte_ignore_les_erreurs_reseau():
    """supprimer_compte est un nettoyage best-effort : une panne reseau ne doit pas faire
    planter le teardown des tests (voir fixture 'apprenant' dans conftest.py)."""
    responses.add(
        responses.DELETE,
        "http://localhost:8000/api/users",
        body=RequestsConnectionError("simulation panne reseau"),
    )

    supprimer_compte("fantome@example.com")
