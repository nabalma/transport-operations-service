import pytest
from django.contrib.auth import get_user_model

# user
# Crée un utilisateur persistant dans la base de données de test.
@pytest.fixture
def user(db):
    """
    Retourne un utilisateur réel pour les tests.
    """
    User = get_user_model()

    return User.objects.create_user(
        username="fleet_manager",
        password="test-password",
    )