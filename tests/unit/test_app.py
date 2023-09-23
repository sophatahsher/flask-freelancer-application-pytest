"""
This file (test_app.py) contains the unit tests for the Flask application.
"""
import pytest
from pydantic import ValidationError

from src.packages.routes import PackageModel


def test_validate_package_data_nominal():
    """
    GIVEN a helper class to validate the form data
    WHEN valid data is passed in
    THEN check that the validation is successful
    """
    request_data = PackageModel(
        package_name='Build Python with Pytest',
        category='Web Development',
        rating=5
    )
    assert request_data.package_name == 'Build Python with Pytest'
    assert request_data.category == 'Web Development'
    assert request_data.rating == 5


def test_validate_package_data_invalid_rating():
    """
    GIVEN a helper class to validate the form data
    WHEN invalid data (invalid rating) is passed in
    THEN check that the validation raises a ValueError
    """
    with pytest.raises(ValueError):
        PackageModel(
            package_name='Build Python with Pytest',
            category='Web Development',
            rating='5.5'  # Invalid
        )


def test_validate_package_data_invalid_package_name():
    """
    GIVEN a helper class to validate the form data
    WHEN invalid data (invalid package_name) is passed in
    THEN check that the validation raises a ValidationError
    """
    with pytest.raises(ValidationError):
        PackageModel(
            package_name=[1, 2, 3],  # Invalid
            category='Sophat Chhay',
            rating='5'
        )


def test_validate_package_data_missing_inputs():
    """
    GIVEN a helper class to validate the form data
    WHEN invalid data (missing input) is passed in
    THEN check that the validation raises a ValidationError
    """
    with pytest.raises(ValidationError):
        PackageModel()  # Missing input data!


def test_validate_package_data_missing_author():
    """
    GIVEN a helper class to validate the form data
    WHEN invalid data (missing author) is passed in
    THEN check that the validation raises a ValidationError
    """
    with pytest.raises(ValidationError):
        PackageModel(
            title='Pytest',
            # Missing author!
            rating='6'  # Invalid
        )
