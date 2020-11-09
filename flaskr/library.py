from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('library', __name__)

# Right now i'm extracting all the users but we could, for example, extract all books associated with said user.

@bp.route('/')
def index():
    db = get_db()
    users = db.execute(
        'SELECT *'
        'FROM User'
    ).fetchall()
    return render_template('library/index.html', users=users)