from functools import wraps
from flask import session, request, redirect, url_for

def registry_oauth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('registry_token', False):
            session['resume_url'] = request.path
            return redirect(url_for('verify'))
        return f(*args, **kwargs)
    return decorated_function


