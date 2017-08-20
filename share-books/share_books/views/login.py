from flask import request
from flask import render_template
from flask import redirect
from flask import url_for
from flask import session
from flask import flash

from share_books.objects.user import User
from share_books.app import app

@app.route('/login', methods=['GET'])
def login_form():
    return render_template("login_form.html")


@app.route('/login', methods=['POST'])
def login():
    errors = []
    email = request.form.get('email')
    password = request.form.get('password')
    user = User.get_by_email(email)
    if not user or not user.authenticate(password):
        flash('Authentication error.')
        return redirect(url_for('index'))
    session['logged_in'] = True
    session['email'] = email
    session['user_id'] = user._id
    return redirect(url_for('book_list'))


@app.route('/logout')
def logout():
    if session['logged_in']:
        session['logged_in'] = False
        del session['email']
        del session['user_id']
    return redirect(url_for('index'))
