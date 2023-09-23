"""
This file (test_models.py) contains the unit tests for the models.py file.
"""
from src.models import Package, Freelancer

def test_new_user():
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email, password_hashed, authenticated, and active fields are defined correctly
    """
    freelancer = Freelancer('Sophat Chhay', 'tovban.freelancer@gmail.com', 'SecretPass')
    assert freelancer.full_name == 'Sophat Chhay'
    assert freelancer.email == 'tovban.freelancer@gmail.com'
    assert freelancer.password_hashed != 'SecretPass'
    assert freelancer.__repr__() == '<Freelancer: tovban.freelancer@gmail.com>'
    assert freelancer.is_authenticated
    assert freelancer.is_active
    assert not freelancer.is_anonymous


def test_new_user_with_fixture(freelancer):
    """
    GIVEN a User model
    WHEN a new User is created
    THEN check the email and password_hashed fields are defined correctly
    """
    assert freelancer.full_name == 'Sophat Chhay'
    assert freelancer.email == 'tovban.freelancer@gmail.com'
    assert freelancer.password_hashed != 'SecretPass'


def test_setting_password(new_user):
    """
    GIVEN an existing User
    WHEN the password for the user is set
    THEN check the password is stored correctly and not as plaintext
    """
    new_user.set_password('MyNewPassword')
    assert new_user.password_hashed != 'MyNewPassword'
    assert new_user.is_password_correct('MyNewPassword')
    assert not new_user.is_password_correct('MyNewPassword2')
    assert not new_user.is_password_correct('FlaskIsAwesome')


def test_user_id(new_user):
    """
    GIVEN an existing User
    WHEN the ID of the user is defined to a value
    THEN check the user ID returns a string (and not an integer) as needed by Flask-WTF
    """
    new_user.id = 1
    assert isinstance(new_user.get_id(), str)
    assert not isinstance(new_user.get_id(), int)
    assert new_user.get_id() == '1'


def test_new_package():
    """
    GIVEN a Package model
    WHEN a new Package is created
    THEN check the package_name, category, and rating fields are defined correctly
    """
    package = Package('Build Python with Pytest', 'Web Development', '5', 1)
    assert package.package_name == 'Build Python with Pytest'
    assert package.category == 'Web Development'
    assert package.rating == 5
    assert package.__repr__() == '<Package: Build Python with Pytest>'


def test_update_package():
    """
    GIVEN a Package model
    WHEN a new Package is updated
    THEN check the package_name, category, and rating fields are updated correctly
    """
    package = Package('Build Python with Pytest', 'Web Development', '5', 1)

    package.update(package_name='Build Python with Pytest')
    assert package.package_name == 'Build Python with Pytest'
    assert package.category == 'Web Development'
    assert package.rating == 5

    package.update(rating='4')
    assert package.package_name == 'Build Python with Pytest'
    assert package.category == 'Web Development'
    assert package.rating == 4

    package.update(category='Software Development')
    assert package.package_name == 'Build Python with Pytest'
    assert package.category == 'Software Development'
    assert package.rating == 4

    package.update(package_name='Build Python with Pytest', category='Software Development', rating='5')
    assert package.package_name == 'Build Python with Pytest'
    assert package.category == 'Software Development'
    assert package.rating == 5
