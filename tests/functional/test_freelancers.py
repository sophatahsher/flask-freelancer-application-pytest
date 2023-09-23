"""
This file (test_users.py) contains the functional tests for the `users` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `users` blueprint.
"""


def test_login_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Email' in response.data
    assert b'Password' in response.data


def test_valid_login_logout(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST)
    THEN check the response is valid
    """
    response = test_client.post('/login', data=dict(email='tovban.freelancer@gmail.com', password='SecretPass'), follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for logging in, tovban.freelancer@gmail.com!' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goodbye!' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data


def test_invalid_login(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='tovban.freelancer@gmail.com', password='SecretPass'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'ERROR! Incorrect login credentials.' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data


def test_login_already_logged_in(test_client, init_database, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/login' page is posted to (POST) when the user is already logged in
    THEN check an error message is returned to the user
    """
    response = test_client.post('/login',
                                data=dict(email='tovban.freelancer@gmail.com', password='SecretPass'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Already logged in!  Redirecting to your User Profile page...' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data


def test_valid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST)
    THEN check the response is valid and the user is logged in
    """
    response = test_client.post('/register',
                                data=dict(email='tovban.freelancer@gmail.com',
                                          password='SecretPass',
                                          confirm='SecretPass'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for registering, tovban.freelancer@gmail.com!' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' in response.data
    assert b'Login' not in response.data
    assert b'Register' not in response.data

    """
    GIVEN a Flask application configured for testing
    WHEN the '/logout' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'Goodbye!' in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data


def test_invalid_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to with invalid credentials (POST)
    THEN check an error message is returned to the user
    """
    response = test_client.post('/register',
                                data=dict(email='tovban.freelancer@gmail.com',
                                          password='SecretPass',
                                          confirm='SecretPass'),   # Does NOT match!
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Thank you for registering, tovban.freelancer@gmail.com!' not in response.data
    assert b'[This field is required.]' not in response.data
    assert b'Flask User Management' in response.data
    assert b'Logout' not in response.data
    assert b'Login' in response.data
    assert b'Register' in response.data


def test_duplicate_registration(test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) using an email address already registered
    THEN check an error message is returned to the user
    """
    # Register the new account
    test_client.post('/register',
                     data=dict(email='tovban.freelancer@gmail.com',
                               password='SecretPass',
                               confirm='SecretPass'),
                     follow_redirects=True)

    # Since the registration process results in the user being logged in, log out the user
    test_client.get('/logout', follow_redirects=True)

    # Try registering with the same email address
    response = test_client.post('/register',
                                data=dict(email='tovban.freelancer@gmail.com',
                                          password='SecretPass',
                                          confirm='SecretPass'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'ERROR! Email (tovban.freelancer@gmail.com) already exists in the database.' in response.data
    assert b'Thank you for registering, tovban.freelancer@gmail.com!' not in response.data


def test_registration_when_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/register' page is posted to (POST) when the user is logged in
    THEN check an error message is returned to the user
    """
    response = test_client.post('/register',
                                data=dict(email='tovban.freelancer@gmail.com',
                                          password='SecretPass',
                                          confirm='SecretPass'),
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Already logged in!  Redirecting to your User Profile page...' in response.data
    assert b'Thank you for registering, tovban.freelancer@gmail.com!' not in response.data


def test_status_page(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/status' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/status')
    assert response.status_code == 200
    assert b'Web Application: Active' in response.data
    assert b'Configuration Type: config.TestingConfig' in response.data
    assert b'Database initialized: True' in response.data
    assert b'Database `users` table created: True' in response.data
    assert b'Database `books` table created: True' in response.data
