import os
import logging
import logging.handlers

from flask import Flask

import classes
from database import db

def create_app(config=None):
    # init flask app
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg', silent=True)
    if config is not None:
        app.config.from_pyfile(config, silent=True)
    db.init_app(app)
    app.register_blueprint(classes.bp, url_prefix = '/classes')
    return app

