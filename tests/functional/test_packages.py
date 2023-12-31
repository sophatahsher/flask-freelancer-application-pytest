"""
This file (test_books.py) contains the functional tests for the `books` blueprint.

These tests use GETs and POSTs to different URLs to check for the proper behavior
of the `books` blueprint.
"""
import os
import re

from src import create_app


def test_home_page():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.config.TestingConfig'
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.get('/')
        assert response.status_code == 200
        assert b"Welcome to the" in response.data
        assert b"Flask User Management Example!" in response.data
        assert b"Need an account?" in response.data
        assert b"Existing user?" in response.data


def test_home_page_post():
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' (Method Not Allowed) status code is returned
    """
    # Set the Testing configuration prior to creating the Flask application
    os.environ['CONFIG_TYPE'] = 'config.config.TestingConfig'
    flask_app = create_app()

    # Create a test client using the Flask application configured for testing
    with flask_app.test_client() as test_client:
        response = test_client.post('/')
        assert response.status_code == 405
        assert b"Flask User Management Example!" not in response.data


def test_home_page_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is requested (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the" in response.data
    assert b"Flask User Management Example!" in response.data
    assert b"Need an account?" in response.data
    assert b"Existing user?" in response.data


def test_home_page_post_with_fixture(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/' page is posted to (POST)
    THEN check that a '405' (Method Not Allowed) status code is returned
    """
    response = test_client.post('/')
    assert response.status_code == 405
    assert b"Flask User Management Example!" not in response.data


def test_get_add_book_page(test_client, init_database, log_in_default_user):
    """
    GIVEN a Flask application configured for testing and the user logged in
    WHEN the '/packages/add' page is requested (GET)
    THEN check the response is valid
    """
    response = test_client.get('/packages/add')
    assert response.status_code == 200
    assert b'Flask User Management Example' in response.data
    assert b'Add a Package' in response.data
    assert b'Package Name <em>(required)</em>' in response.data
    assert b' <em>(required)</em>' in response.data
    assert b'Rating <em>(required, 1-5)</em>' in response.data


def test_get_add_book_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/books/add' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/packages/add', follow_redirects=True)
    assert response.status_code == 200
    assert b'Add a Package' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_post_add_book_page(test_client, log_in_default_user):
    """"
    GIVEN a Flask application configured for testing and the user logged in
    WHEN the '/packages/add' page is posted to (POST)
    THEN check that a message is displayed to the user that the package was added
    """
    response = test_client.post('/packages/add',
                                data={'book_package_name': 'The Guest List',
                                      'book_category': 'Lucy Foley',
                                      'book_rating': '5'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Package' in response.data
    assert b'Package Name' in response.data
    assert b'Category' in response.data
    assert b'Rating' in response.data
    assert b'The Guest List' in response.data
    assert b'Lucy Foley' in response.data
    assert b'5' in response.data
    assert b'Added new book (The Guest List)!' in response.data


def test_post_add_book_page_invalid_book_rating(test_client, log_in_default_user):
    """"
    GIVEN a Flask application configured for testing and the user logged in
    WHEN the '/packages/add' page is posted to (POST) with an invalid rating for the book
    THEN check that an error message is displayed to the user
    """
    response = test_client.post('/packages/add',
                                data={'book_package_name': 'The Guest List',
                                      'book_category': 'Lucy Foley',
                                      'book_rating': '6'},  # Invalid! Needs to be between 1-5
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Error with book data submitted!' in response.data
    assert b'Packages' in response.data
    assert b'Added new package (The Guest List)!' not in response.data


def test_post_add_book_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/packages/add' page is posted to (POST) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.post('/books/add',
                                data={'book_package_name': 'The Guest List',
                                      'book_category': 'Lucy Foley',
                                      'book_rating': '5'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert b'Added new book (The Guest List)!' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_get_book_list_logged_in(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of packages in the database
    WHEN the '/packages/' page is requested (GET)
    THEN check the response is valid and each default book is displayed
    """
    headers = [b'Package Name', b'Category', b'Rating']
    data = [b'Malibu Rising', b'Taylor Jenkins Reid', b'5',
            b'Carrie Soto is Back', b'Taylor Jenkins Reid', b'4',
            b'Book Lovers', b'Emily Henry', b'3']

    response = test_client.get('/pages/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Packages' in response.data
    for header in headers:
        assert header in response.data
    for element in data:
        assert element in response.data


def test_get_book_list_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/packages/' page is requested (GET) when the user is not logged in
    THEN check that the user is redirected to the login page
    """
    response = test_client.get('/packages/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data


def test_delete_book_logged_in_own_book(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of packages in the database
    WHEN the '/packages/2/delete' page is retrieved (GET)
    THEN check that the response is valid and a success message is displayed
    """
    response = test_client.get('/packages/2/delete', follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"Package \(.*\) was deleted!", str(response.data))
    assert b'Packages' in response.data


def test_delete_book_logged_in_not_owning_book(test_client, log_in_second_user):
    """
    GIVEN a Flask application configured for testing, with the second user logged in
          and the default set of packages in the database
    WHEN the '/packages/3/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/3/delete', follow_redirects=True)
    assert response.status_code == 403
    assert not re.search(r"Package \(.*\) was deleted!", str(response.data))


def test_delete_book_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/packages/1/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/1/delete', follow_redirects=True)
    assert response.status_code == 200
    assert not re.search(r"Package \(.*\) was deleted!", str(response.data))
    assert b'Please log in to access this page.' in response.data


def test_delete_book_invalid_book(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of packages in the database
    WHEN the '/packages/178/delete' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/178/delete', follow_redirects=True)
    assert response.status_code == 404
    assert not re.search(r"Package \(.*\) was deleted!", str(response.data))


def test_get_edit_book_page_logged_in_own_book(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of books in the database
    WHEN the '/packages/1/edit' page is retrieved (GET)
    THEN check that the response is valid
    """
    response = test_client.get('/packages/1/edit', follow_redirects=True)
    assert response.status_code == 200
    assert b'Edit Package' in response.data
    assert b'Package Name' in response.data
    assert b'Category' in response.data
    assert b'Rating' in response.data


def test_get_edit_book_page_logged_in_not_owning_book(test_client, log_in_second_user):
    """
    GIVEN a Flask application configured for testing, with the second user logged in
          and the default set of books in the database
    WHEN the '/packages/1/edit' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/1/edit', follow_redirects=True)
    assert response.status_code == 403
    assert b'Edit Book' not in response.data


def test_get_edit_book_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/packages/1/edit' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/1/edit', follow_redirects=True)
    assert response.status_code == 200
    assert b'Edit Book' not in response.data
    assert b'Please log in to access this page.' in response.data


def test_get_edit_book_page_invalid_book(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing with the default user logged in
    WHEN the '/packages/379/edit' page is retrieved (GET)
    THEN check that an error message is displayed
    """
    response = test_client.get('/packages/379/edit', follow_redirects=True)
    assert response.status_code == 404
    assert b'Edit Book' not in response.data


def test_post_edit_book_valid(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing, with the default user logged in
          and the default set of books in the database
    WHEN the '/packages/1/edit' page is posted to (POST)
    THEN check that a message is displayed to the user that the book was updated
    """
    response = test_client.post('/packages/1/edit',
                                data={'package_name': 'Malibu Rising 2',
                                      'category': 'Taylor J. Reid',
                                      'rating': '2'},
                                follow_redirects=True)
    assert response.status_code == 200
    assert re.search(r"Package \(.*\) was updated!", str(response.data))
    assert b'Malibu Rising 2' in response.data
    assert b'Taylor J. Reid' in response.data
    assert b'2' in response.data


def test_post_edit_book_invalid_user(test_client, log_in_second_user):
    """
    GIVEN a Flask application configured for testing, with the second user logged in
          and the default set of books in the database
    WHEN the '/packages/1/edit' page is posted to (POST)
    THEN check that an error message is displayed
    """
    response = test_client.post('/packages/1/edit',
                                data={'package_name': 'Malibu Rising 2',
                                      'category': 'Taylor J. Reid',
                                      'rating': '2'},
                                follow_redirects=True)
    assert response.status_code == 403
    assert not re.search(r"Package \(.*\) was updated!", str(response.data))


def test_post_edit_book_page_not_logged_in(test_client):
    """
    GIVEN a Flask application configured for testing without a user logged in
    WHEN the '/packages/1/edit' page is posted to (POST)
    THEN check that an error message is displayed
    """
    response = test_client.post('/packages/1/edit',
                                data={'package_name': 'Malibu Rising 2',
                                      'category': 'Taylor J. Reid',
                                      'rating': 2},
                                follow_redirects=True)
    assert response.status_code == 200
    assert not re.search(r"Package \(.*\) was updated!", str(response.data))
    assert b'Please log in to access this page.' in response.data


def test_get_edit_book_page_invalid_book(test_client, log_in_default_user):
    """
    GIVEN a Flask application configured for testing with the default user logged in
    WHEN the '/packages/379/edit' page is posted to (POST)
    THEN check that an error message is displayed
    """
    response = test_client.post('/packages/379/edit',
                                data={'package_name': 'Malibu Rising 2',
                                      'category': 'Taylor J. Reid',
                                      'rating': '2'},
                                follow_redirects=True)
    assert response.status_code == 404
    assert not re.search(r"Package \(.*\) was updated!", str(response.data))
