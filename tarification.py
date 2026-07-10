PRIX_UNITAIRE = 40
SEUIL_REMISE_FIDELITE = 3
TAUX_REMISE_FIDELITE = 0.15


def prix_inscription(nb_cours: int) -> float:
    """Calcule le prix d'inscription avec remise fidelite des le 3e cours."""
    total = nb_cours * PRIX_UNITAIRE
    if nb_cours >= SEUIL_REMISE_FIDELITE:
        total = round(total * (1 - TAUX_REMISE_FIDELITE), 2)
    return total
