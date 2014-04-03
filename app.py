import os
import logging
import logging.handlers

from flask import Flask

import classes

def create_app(config=None):
    # init flask app
    app = Flask(__name__)
    app.register_blueprint(classes.bp, url_prefix = '/classes')
    return app

