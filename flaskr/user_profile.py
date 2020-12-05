from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from sqlite3 import Error

from flaskr.auth import login_required
from flaskr.db import get_db

import datetime

bp = Blueprint('profile', __name__, url_prefix='/profile/')


@bp.route('/', methods=('GET', 'POST'))
def account():


    return render_template('users/useraccount.html')