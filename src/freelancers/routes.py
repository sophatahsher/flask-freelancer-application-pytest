import os

import sqlalchemy as sqla
from flask import (current_app, flash, redirect, render_template, request,url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy.exc import IntegrityError

from src import db
from src.models import Freelancer

from . import freelancers_blueprint
from .forms import LoginForm, RegisterForm


@freelancers_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    return render_template('freelancers/profile.html')


@freelancers_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    # If the User is already logged in, don't allow them to try to register
    if current_user.is_authenticated:
        flash('Already logged in!  Redirecting to your User Profile page...')
        return redirect(url_for('profile'))

    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        try:
            new_user = Freelancer('Freelancer Name', form.email.data, form.password.data)
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)
            flash(f'Thank you for registering, {new_user.email}!')
            return redirect(url_for('packages.index'))
        except IntegrityError:
            db.session.rollback()
            flash(f'ERROR! Email ({new_user.email}) already exists in the database.')
    return render_template('register.html', form=form)


@freelancers_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    # If the User is already logged in, don't allow them to try to log in again
    if current_user.is_authenticated:
        flash('Already logged in!  Redirecting to your User Profile page...')
        return redirect(url_for('freelancers.profile'))

    form = LoginForm()

    if request.method == 'POST':
        if form.validate_on_submit():
            print(form.email.data)
            print(form.password.data)
            user = Freelancer.query.filter_by(email=form.email.data).first()
            print(user)
            if user and user.is_password_correct(form.password.data):
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=form.remember_me.data)
                flash('Thank you for logging in, {}!'.format(current_user.email))
                return redirect(url_for('packages.index'))

        flash('ERROR! Incorrect login credentials.')
    return render_template('login.html', form=form)


@freelancers_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Goodbye!')
    return redirect(url_for('packages.index'))


@freelancers_blueprint.route('/status')
def status():
    # Check if the database needs to be initialized
    engine = sqla.create_engine(current_app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sqla.inspect(engine)
    users_table_created = inspector.has_table("freelancers")
    books_table_created = inspector.has_table("packages")
    database_created = users_table_created and books_table_created

    return render_template(
        'freelancers/status.html',
        config_type=os.getenv('CONFIG_TYPE'),
        database_status=database_created,
        database_users_table_status=users_table_created,
        database_books_table_status=books_table_created
    )
