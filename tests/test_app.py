import pytest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_home_route(client):
    """Test que la route / renvoie bien le message attendu"""
    response = client.get('/')
    assert response.status_code == 200
    assert response.data == b"Hello from Kubernetes"
