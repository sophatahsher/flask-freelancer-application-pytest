from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from pydantic import BaseModel, ValidationError, validator

from src import db
from src.models import Package

from . import packages_blueprint


# --------------
# Helper Classes
# --------------

class PackageModel(BaseModel):
    """Class for parsing new package data from a form."""
    package_name: str
    category: str
    rating: int

    @validator('rating')
    def package_rating_check(cls, value):
        if value not in range(1, 6):
            raise ValueError('Package rating must be a whole number between 1 and 5')
        return value


# ------
# Routes
# ------

@packages_blueprint.route('/')
def index():
    # If the user is already logged in, redirect to the list of packages
    if current_user.is_authenticated:
        return redirect(url_for('packages.list_packages'))

    return render_template('packages/index.html')


@packages_blueprint.get('/packages/')
@login_required
def list_packages():
    query = db.select(Package).where(Package.freelancer_id == current_user.id).order_by(Package.id)
    packages = db.session.execute(query).scalars().all()
    return render_template('packages/package.html', packages=packages)


@packages_blueprint.route('/packages/add', methods=['GET', 'POST'])
@login_required
def add_package():
    if request.method == 'POST':
        try:
            request_data = PackageModel(
                package_name=request.form['package_title'],
                category=request.form['package_author'],
                rating=request.form['package_rating']
            )
            print(request_data)

            # Save the form data to the database
            new_package = Package(request_data.package_name, request_data.category, request_data.rating, current_user.id)
            db.session.add(new_package)
            db.session.commit()

            flash(f"Added new package ({new_package.title})!")
            current_app.logger.info(f'Package ({new_package.title}) was added for user: {current_user.id}!')
            return redirect(url_for('packages.list_packages'))
        except ValidationError as e:
            flash("Error with package data submitted!")
            print(e)

    return render_template('packages/add_package.html')


@packages_blueprint.route('/packages/<id>/delete')
@login_required
def delete_package(id):
    query = db.select(Package).where(Package.id == id)
    package = db.session.execute(query).scalar_one_or_none()

    if package is None:
        abort(404)

    if package.freelancer_id != current_user.id:
        abort(403)

    db.session.delete(package)
    db.session.commit()
    flash(f'Package ({package.package_name}) was deleted!')
    current_app.logger.info(f'Book ({package.package_name}) was deleted for user: {current_user.id}!')
    return redirect(url_for('packages.list_packages'))


@packages_blueprint.route('/packages/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(id):
    query = db.select(Package).where(Package.id == id)
    package = db.session.execute(query).scalar_one_or_none()

    if package is None:
        abort(404)

    if package.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        # Edit the package data in the database
        package.update(request.form['package_name'],
                    request.form['category'],
                    request.form['rating'])
        db.session.add(package)
        db.session.commit()

        flash(f'Package ({ package.package_name }) was updated!')
        current_app.logger.info(f'Package ({ package.package_name }) was updated by user: { current_user.id}')
        return redirect(url_for('packages.list_packages'))

    return render_template('packages/edit_package.html', package=package)
