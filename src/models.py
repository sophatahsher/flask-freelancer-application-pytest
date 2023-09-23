from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import mapped_column, relationship
from werkzeug.security import check_password_hash, generate_password_hash

from src import db


class Freelancer(UserMixin, db.Model):
    """
    Class that represents a user of the application

    The following attributes of a user are stored in this table:
        * email - email address of the user
        * hashed password - hashed password (using werkzeug.security)
        * registered_on - date & time that the user registered

    REMEMBER: Never store the plaintext password in a database!
    """

    __tablename__ = 'freelancers'

    id = mapped_column(Integer(), primary_key=True, autoincrement=True)
    full_name = mapped_column(String(), nullable=False)
    email = mapped_column(String(), unique=True, nullable=False)
    password_hashed = mapped_column(String(128), nullable=False)
    created_at = mapped_column(DateTime(), nullable=False)

    # Define the relationship to the `Package` class
    packages_relationship = relationship('Package', back_populates='freelancer_relationship')

    def __init__(self, full_name: str, email: str, password_plaintext: str):
        """Create a new Freelancer object using the email address and hashing the
        plaintext password using Werkzeug.Security.
        """
        self.email = email
        self.full_name = full_name
        self.password_hashed = self._generate_password_hash(password_plaintext)
        self.created_at = datetime.now()

    def is_password_correct(self, password_plaintext: str):
        return check_password_hash(self.password_hashed, password_plaintext)

    def set_password(self, password_plaintext: str):
        self.password_hashed = self._generate_password_hash(password_plaintext)

    @staticmethod
    def _generate_password_hash(password_plaintext):
        return generate_password_hash(password_plaintext)

    def __repr__(self):
        return f'<Freelancer: {self.email}>'


class Package(db.Model):
    """
    Class that represents a Freelancer's package that has been created.

    The following attributes of a package are stored in this table:
        * package_name - Name of the package service
        * category - category of the package service
        * rating - rating (1 (bad) to 5 (amazing)) of the package service
    """

    __tablename__ = 'packages'

    id = mapped_column(Integer(), primary_key=True, autoincrement=True)
    package_name = mapped_column(String())
    category = mapped_column(String())
    rating = mapped_column(Integer())
    freelancer_id = mapped_column(ForeignKey('freelancers.id'))

    # Define the relationship to the `Freelancer` class
    freelancer_relationship = relationship('Freelancer', back_populates='packages_relationship')

    def __init__(self, package_name: str, category: str, rating: str, freelancer_id: int):
        """Create a new Package object using the package_name, category, and rating of the package."""
        self.package_name = package_name
        self.category = category
        self.rating = int(rating)
        self.freelancer_id = freelancer_id

    def update(self, package_name: str = '', category: str = '', rating: str = ''):
        """Update the fields of the Package object."""
        if package_name:
            self.package_name = package_name
        if category:
            self.category = category
        if rating:
            self.rating = int(rating)

    def __repr__(self):
        return f'<Package: {self.package_name}>'
