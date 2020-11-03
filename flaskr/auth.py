import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

#Route in which users can register and be added to the 'User' table.
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        u_name = request.form['username']
        u_password = request.form['password']
        u_email = request.form['email']
        db = get_db()
        error = None
        if not u_name:
            error = 'Username is required.'
        elif not u_email:
            error = 'Email is required.'
        elif not u_password:
            error = 'Password is required.'
        
        elif db.execute(
            'SELECT u_userid FROM User WHERE u_email = ?', (u_email,)
        ).fetchone() is not None:
            error = 'Email {} is already registered.'.format(u_email)

        if error is None:
            db.execute(
                'INSERT INTO User (u_name, u_email, u_password) VALUES (?, ?, ?)',
                (u_name, u_email, generate_password_hash(u_password))
            )
            db.commit()
            return redirect(url_for('auth.login'))

        flash(error)

    return render_template('auth/register.html')

#Route in which users can login.
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        u_email = request.form['email']
        u_password = request.form['password']
        db = get_db()
        error = None
        User = db.execute(
            'SELECT * FROM User WHERE u_email = ?', (u_email, )
        ).fetchone()

        if User is None:
            error = 'Incorrect Email.'
        elif not check_password_hash(User['u_password'], u_password):
            error = 'Incorrect Password.'

        if error is None:
            session.clear()
            session['u_userid'] = User['u_userid']
            return redirect(url_for('index'))
        flash(error)
    return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('u_userid')
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM User WHERE u_userid = ?', (user_id, )
        ).fetchone()

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)

    return wrapped_view

#Route in which users can logout.
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

