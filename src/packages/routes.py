from flask import (abort, current_app, flash, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from pydantic import BaseModel, ValidationError, validator

from src import db
from src.models import Book

from . import books_blueprint


# --------------
# Helper Classes
# --------------

class BookModel(BaseModel):
    """Class for parsing new book data from a form."""
    title: str
    author: str
    rating: int

    @validator('rating')
    def book_rating_check(cls, value):
        if value not in range(1, 6):
            raise ValueError('Book rating must be a whole number between 1 and 5')
        return value


# ------
# Routes
# ------

@books_blueprint.route('/')
def index():
    # If the user is already logged in, redirect to the list of books
    if current_user.is_authenticated:
        return redirect(url_for('packages.list_packages'))

    return render_template('packages/index.html')


@books_blueprint.get('/packages/')
@login_required
def list_packages():
    query = db.select(Book).where(Book.user_id == current_user.id).order_by(Book.id)
    books = db.session.execute(query).scalars().all()
    return render_template('packages/package.html', books=books)


@books_blueprint.route('/packages/add', methods=['GET', 'POST'])
@login_required
def add_package():
    if request.method == 'POST':
        try:
            book_data = BookModel(
                title=request.form['package_title'],
                author=request.form['package_author'],
                rating=request.form['package_rating']
            )
            print(book_data)

            # Save the form data to the database
            new_book = Book(book_data.title, book_data.author, book_data.rating, current_user.id)
            db.session.add(new_book)
            db.session.commit()

            flash(f"Added new package ({new_book.title})!")
            current_app.logger.info(f'Package ({new_book.title}) was added for user: {current_user.id}!')
            return redirect(url_for('packages.list_packages'))
        except ValidationError as e:
            flash("Error with package data submitted!")
            print(e)

    return render_template('packages/add_package.html')


@books_blueprint.route('/packages/<id>/delete')
@login_required
def delete_book(id):
    query = db.select(Book).where(Book.id == id)
    book = db.session.execute(query).scalar_one_or_none()

    if book is None:
        abort(404)

    if book.user_id != current_user.id:
        abort(403)

    db.session.delete(book)
    db.session.commit()
    flash(f'Book ({book.title}) was deleted!')
    current_app.logger.info(f'Book ({book.title}) was deleted for user: {current_user.id}!')
    return redirect(url_for('books.list_books'))


@books_blueprint.route('/packages/<id>/edit', methods=['GET', 'POST'])
@login_required
def edit_package(id):
    query = db.select(Book).where(Book.id == id)
    book = db.session.execute(query).scalar_one_or_none()

    if book is None:
        abort(404)

    if book.user_id != current_user.id:
        abort(403)

    if request.method == 'POST':
        # Edit the book data in the database
        book.update(request.form['package_title'],
                    request.form['package_author'],
                    request.form['package_rating'])
        db.session.add(book)
        db.session.commit()

        flash(f'Package ({ book.title }) was updated!')
        current_app.logger.info(f'Package ({ book.title }) was updated by user: { current_user.id}')
        return redirect(url_for('packages.list_packages'))

    return render_template('packages/edit_package.html', book=book)
