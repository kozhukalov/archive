from flask import session
from flask import render_template
from flask import request
from flask import url_for
from flask import redirect

from share_books.app import app
from share_books.objects.book import Book
from share_books.utils import authenticate

@app.route('/book_list', methods=['GET'])
def book_list():
    return render_template('book_list.html', books=Book.get_all())

@app.route('/book_add', methods=['POST'])
@authenticate
def book_add():
    title = request.form.get('title')
    author = request.form.get('author')
    description = request.form.get('description')
    deposit = request.form.get('deposit')
    rent_per_day = request.form.get('rent_per_day')
    book = Book.new(
        user_id=session['user_id'],
        title=title,
        author=author,
        description=description,
        deposit=deposit,
        rent_per_day=rent_per_day)
    book.save()
    return redirect(url_for('book_list'))

@app.route('/book_edit/<book_id>', methods=['GET', 'POST'])
@authenticate
def book_edit(book_id):
    book = Book.get_by_id(book_id)
    if book.user_id != session['user_id']:
        return render_template('403.html')
    if request.method == 'GET':
        return render_template('book_form.html', book=book)
    else:
        title = request.form.get('title')
        author = request.form.get('author')
        description = request.form.get('description')
        deposit = request.form.get('deposit')
        rent_per_day = request.form.get('rent_per_day')
        book.update(
            title=title,
            author=author,
            description=description,
            deposit=deposit,
            rent_per_day=rent_per_day)
        book.save()
    return redirect(url_for('book_list'))

@app.route('/book_form', methods=['GET'])
@authenticate
def book_form():
    return render_template('book_form.html')

@app.route('/book_delete/<book_id>', methods=['GET'])
@authenticate
def book_delete(book_id):
    book = Book.get_by_id(book_id)
    if not book:
        return render_template('404.html')
    if book.user_id != session['user_id']:
        return render_template('403.html')
    Book.delete_by_id(book_id)
    return redirect(url_for('book_list'))
