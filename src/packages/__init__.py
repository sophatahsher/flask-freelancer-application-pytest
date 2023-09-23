"""
The books Blueprint handles the creation, modification, deletion,
and viewing of books for the users of this application.
"""
from flask import Blueprint


packages_blueprint = Blueprint('packages', __name__, template_folder='templates')

from . import routes
