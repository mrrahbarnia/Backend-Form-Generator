import pytest

from rest_framework.test import APIClient
from django.contrib.auth.models import User

@pytest.fixture
def anon_client():
    """
    Create and return anonymous
    client without authenticated.
    """
    return APIClient()


@pytest.fixture
def normal_client():
    """
    Create and return authenticated
    client as a normal user.
    """
    client = APIClient()
    normal_user = User.objects.create_user(
        username='normal',
        password='1234@example.com'
    )
    client.force_authenticate(user=normal_user)
    return client


@pytest.fixture
def admin_client():
    """
    Create and return authenticated
    client as a admin user.
    """
    client = APIClient()
    admin_user = User.objects.create_superuser(
        email='admin',
        password='1234@example.com'
    )
    client.force_authenticate(user=admin_user)
    return client