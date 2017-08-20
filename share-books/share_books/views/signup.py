import logging

from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

from share_books.app import app
from share_books.objects.user import User


@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup():
    errors = []
    email = request.form.get('email')
    if not email:
        errors.append('Email address must be given.')
    password = request.form.get('password')
    if not password:
        errors.append('Password must be given')

    confirm_password = request.form.get('confirm_password')
    if not confirm_password:
        errors.append('Password confirmation not given.')
    if password != confirm_password:
        errors.append('Password confirmation failed. Try again.')

    if User.get_by_email(email):
        errors.append('User with such email already exists.')

    if errors:
        return render_template('signup.html', errors=errors, email=email)

    # TODO(kozhukalov): Email confirmation procedure.
    user = User.new(email=email, password=password)
    user.save()
    session['logged_in'] = True
    session['email'] = email
    return redirect(url_for('index'))
