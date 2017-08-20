from flask import session
from flask import render_template
from share_books.app import app

@app.route('/')
def index():
    return render_template('index.html')
