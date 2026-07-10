def email_valide(adresse: str) -> bool:
    """Verifie qu'une adresse e-mail est bien formee."""
    if not adresse or "@" not in adresse:
        return False
    local, _, domaine = adresse.partition("@")
    return bool(local and domaine and "." in domaine)
