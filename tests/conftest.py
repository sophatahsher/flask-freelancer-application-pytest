import os

import pytest

from src import create_app, db
from src.models import Freelancer, Package


# --------
# Fixtures
# --------

@pytest.fixture(scope='module')
def new_user():
    freelancer = Freelancer('Sophat Chhay', 'tovban.freelancer@gmail.com', 'SecretPass')
    return freelancer


@pytest.fixture(scope='module')
def test_client():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.config.TestingConfig'
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as testing_client:
        # Establish an application context
        with flask_app.app_context():
            yield testing_client  # this is where the testing happens!


@pytest.fixture(scope='module')
def init_database(test_client):
    # Create the database and the database table
    db.create_all()

    # Insert user data
    default_user = Freelancer('Sophat Chhay', email='tovban.freelancer@gmail.com', password_plaintext='SecretPass')
    second_user = Freelancer('Sophat Chhay', email='tovban.freelancer+1@gmail.com', password_plaintext='SecretPass')
    db.session.add(default_user)
    db.session.add(second_user)

    # Commit the changes for the users
    db.session.commit()

    # Insert book data
    package1 = Package('Malibu Rising', 'Taylor Jenkins Reid', '5', default_user.id)
    package2 = Package('Carrie Soto is Back', 'Taylor Jenkins Reid', '4', default_user.id)
    package3 = Package('Book Lovers', 'Emily Henry', '3', default_user.id)
    db.session.add(package1)
    db.session.add(package2)
    db.session.add(package3)

    # Commit the changes for the books
    db.session.commit()

    yield  # this is where the testing happens!

    db.drop_all()


@pytest.fixture(scope='function')
def log_in_default_user(test_client):
    test_client.post('/login',
                     data={'email': 'tovban.freelancer@gmail.com', 'password': 'SecretPass'})

    yield  # this is where the testing happens!

    test_client.get('/logout')


@pytest.fixture(scope='function')
def log_in_second_user(test_client):
    test_client.post('/login',
                     data={'email': 'tovban.freelancer@gmail.com','password': 'FlaskIsTheBest987'})

    yield   # this is where the testing happens!

    # Log out the user
    test_client.get('/logout')


@pytest.fixture(scope='module')
def cli_test_client():
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.config.TestingConfig'
    flask_app = create_app()

    runner = flask_app.test_cli_runner()

    yield runner  # this is where the testing happens!
