#File where application is created.

import os
from flask import Flask

def create_app(test_config=None):
    #Create and configure the app
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='CSE111',
        DATABASE=os.path.join(app.instance_path, 'data.sqlite'),
    )
    
    #Importing db.py
    from . import db
    db.init_app(app)

    #Importing auth.py
    from . import auth
    app.register_blueprint(auth.bp)

    return app