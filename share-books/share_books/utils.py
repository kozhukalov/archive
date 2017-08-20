import random
import string
from functools import wraps
from flask import session


def gen_id(lenght=41, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(lenght))


def authenticate(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Authentication required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated
