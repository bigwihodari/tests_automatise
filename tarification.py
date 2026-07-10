def prix_inscription(nb_cours: int) -> float:
    """Calcule le prix d'inscription avec remise fidelite des le 3e cours."""
    prix_unitaire = 40
    total = nb_cours * prix_unitaire
    if nb_cours >= 3:
        total = round(total * 0.85, 2)
    return total
