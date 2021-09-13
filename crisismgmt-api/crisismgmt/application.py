"""
application.py
- creates a Flask app instance and registers the database object
"""

from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman


def create_app(app_name='CRISISMGMT_API'):
    app = Flask(app_name)
    app.app_context().push()
    CORS(app)
    Talisman(app)
    app.config.from_object('crisismgmt.config.BaseConfig')

    from crisismgmt.api import api
    app.register_blueprint(api, url_prefix="/api")

    from crisismgmt.models import db
    db.init_app(app)

    return app
