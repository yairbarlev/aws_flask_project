import json
import pytest
from helloworld.application import application


@pytest.fixture
def client():
    return application.test_client()


def test_response(client):
    print ('Test')