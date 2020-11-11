import functools
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from random import randint

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        u_name = request.form['username']
        u_password = request.form['password']
        u_email = request.form['email']
        userType = request.form['userType']
        school = request.form['school']
        major = request.form['major']
        
        db = get_db()
        error = None
      
        if db.execute(
            'SELECT u_userid FROM User WHERE u_email = ?', (u_email,)
        ).fetchone() is not None:
            error = 'Email {} is already registered.'.format(u_email)

        if error is None:
            db.execute(
                'INSERT INTO User (u_name, u_email, u_password) VALUES (?, ?, ?)',
                (u_name, u_email, generate_password_hash(u_password))
            )

            cur = db.cursor()
            cur.execute('SELECT u_userid FROM User WHERE u_email = ?', (u_email,))
            q = cur.fetchone()

            if userType == "student":
                db.execute(
                'INSERT INTO LibraryUser (lu_userid,lu_major) VALUES (?,?)',
                (q["u_userid"], major))
            if userType == "librarian":
                db.execute(
                'INSERT INTO Librarian (l_userid,l_salary) VALUES (?,?)',
                (q["u_userid"], randint(30000,85000)))

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

