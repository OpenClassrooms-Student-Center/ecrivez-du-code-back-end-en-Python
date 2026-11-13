import pytest
from django.core.management import call_command


@pytest.fixture
def demo_data(db):
    """Charge le jeu de démonstration dans la base de test."""
    call_command("reset_demo")
