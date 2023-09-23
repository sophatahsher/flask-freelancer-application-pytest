import pytest
from flask import current_app
from app import app

@pytest.fixture(scope='function')
def client():
    with app.test_client() as client:
        print('config=====%s'%(current_app.config))
        assert current_app.config["ENV"] == "production" # Error!

def test_index_homepage(client):
    response = client.get('/')

    assert response.status_code == 200
    assert b'Welcome!' in response.data
