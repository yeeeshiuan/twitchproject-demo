# project/__init__.py


import os

from flask import Flask
from flask_cors import CORS
from flask_pymongo import PyMongo

# instantiate the extensions
mongo = PyMongo()


def create_app(script_info=None):

    # instantiate the app
    app = Flask(__name__)

    # enable CORS
    CORS(app)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    if not script_info:
        # set up extensions
        mongo.init_app(app)

    # register blueprints
    from project.api.repository import repository_blueprint
    app.register_blueprint(repository_blueprint)

    if not script_info:
        # shell context for flask cli
        @app.shell_context_processor
        def ctx():
            return {'app': app, 'mongo': mongo}

    return app
