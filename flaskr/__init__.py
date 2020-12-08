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

    from . import library
    app.register_blueprint(library.bp)
    app.add_url_rule('/', endpoint='index')


    from . import checkout
    app.register_blueprint(checkout.bp)
    app.add_url_rule('/book', endpoint='book')
    app.add_url_rule('/book/description', endpoint='book.description')

    from . import user_profile
    app.register_blueprint(user_profile.bp)

    
    print(app.url_map)

    return app