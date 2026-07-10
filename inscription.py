import os

import requests


def inscrire_cours_payant(base_url, payment_api, apprenant, cours_id):
    """Inscrit un apprenant a un cours payant via l'API de paiement externe."""
    paiement = requests.post(
        payment_api,
        json={
            "email": apprenant["email"],
            "cours": cours_id,
            "montant": 4000,
        },
        timeout=10,
    )
    if paiement.status_code == 402:
        return {"ok": False, "message": "Paiement refuse, verifiez votre carte"}
    paiement.raise_for_status()
    return {"ok": True, "message": "Inscription confirmee"}


def supprimer_compte(email: str) -> None:
    """Supprime un compte de test via l'API de la plateforme."""
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    try:
        requests.delete(
            f"{base_url}/api/users",
            params={"email": email},
            timeout=2,
        )
    except requests.RequestException:
        pass
