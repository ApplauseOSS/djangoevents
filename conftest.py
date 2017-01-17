from rest_framework.test import APIRequestFactory
import pytest


@pytest.fixture
def arf():
    return APIRequestFactory()
