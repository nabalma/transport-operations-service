# test_user_fixture
# Vérifie que la fixture crée bien un utilisateur persistant.
def test_user_fixture(user):
    """
    Vérifie que la fixture user retourne l’utilisateur attendu.
    """
    assert user.pk is not None
    assert user.username == "fleet_manager"