import logging
import sys

from flask import Flask
from flask.ext.pymongo import PyMongo

from flask import session
from flask.ext.session import Session
from flask.ext.passlib import Passlib

import jinja2

from share_books import settings

DATEFORMAT = '%Y-%m-%d %H:%M:%S'
LOGFORMAT = '%(asctime)s.%(msecs)03d %(levelname)s ' + \
            '[%(thread)x] (%(module)s) %(message)s'
formatter = logging.Formatter(LOGFORMAT, DATEFORMAT)

LOG = logging.getLogger()
LOG.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(formatter)
LOG.addHandler(handler)

app = Flask(__name__, static_folder=settings.STATIC_PATH, static_url_path='')

app.config['DEBUG'] = True
app.config['TESTING'] = False
app.config['PROPAGATE_EXCEPTIONS'] = False

app.config['MONGO_AUTO_START_REQUEST'] = False
app.config['MONGO_DBNAME'] = 'share_books'
app.config['MONGO_USERNAME'] = 'share_books'
app.config['MONGO_PASSWORD'] = 'share_books'
mongo = PyMongo(app)

app.config['SESSION_TYPE'] = 'filesystem'
# app.config['SESSION_FILE_DIR'] = 'flask_session'
# app.config['SESSION_FILE_THRESHOLD'] = 500
# app.config['SESSION_FILE_MODE'] = 0600
Session(app)

passlib = Passlib(app)


jinja_loader = jinja2.ChoiceLoader(
    [jinja2.FileSystemLoader(settings.TEMPLATES_PATH)])
app.jinja_loader = jinja_loader


from share_books.views.login import login
from share_books.views.login import logout
from share_books.views.index import index
from share_books.views.signup import signup
from share_books.views.books import book_list
from share_books.views.books import book_add
from share_books.views.books import book_form
from share_books.views.books import book_edit
