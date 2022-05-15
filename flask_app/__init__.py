# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
# from flask_app.movies import routes
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from flask_talisman import Talisman
from werkzeug.utils import secure_filename

# stdlib
from datetime import datetime
import os

# local

db = MongoEngine()
login_manager = LoginManager()
bcrypt = Bcrypt()

from .users.routes import users
from .functions.routes import functions
from .admin.routes import admin
from .calendar.routes import calendar


def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)

    # handle csp
    csp = {
        'default-src': '\'self\'',
        'img-src': ['\'self\'', 'data:'],
        'media-src': '\'self\'',
        'frame-src': 'https://calendar.google.com/',
        # unsafe-inline needed for dynamic modal to work
        'script-src': ['\'self\'', 'https://code.jquery.com/', 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/', 'unsafe-inline'],
        'style-src': ['\'self\'', 'https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/', 'unsafe-inline']
    }

    Talisman(app, content_security_policy=csp, content_security_policy_nonce_in=['script-src'])

    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(functions)
    app.register_blueprint(admin)
    app.register_blueprint(calendar)
    app.register_error_handler(404, page_not_found)

    login_manager.login_view = "users.login"

    return app
