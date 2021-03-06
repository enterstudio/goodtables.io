import os
from urllib.parse import urlparse
import logging

import sqlalchemy
from flask import Flask
from raven.contrib.flask import Sentry

from goodtablesio import settings
from goodtablesio.auth import oauth, login_manager
from goodtablesio.blueprints.api import api
from goodtablesio.blueprints.site import site
from goodtablesio.blueprints.user import user
from goodtablesio.integrations.github.blueprint import github
from goodtablesio.integrations.s3.blueprint import s3
from goodtablesio.utils.frontend import render_component
from goodtablesio.services import database
log = logging.getLogger(__name__)


# Module API

# Create instance
app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'public'),
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'public')
)
app.secret_key = settings.FLASK_SECRET_KEY

url_parts = urlparse(settings.BASE_URL)
app.config['SERVER_NAME'] = url_parts.netloc
app.config['JSONIFY_MIMETYPE'] = 'application/json; charset=utf-8'

# Register Flask integrations
oauth.init_app(app)
login_manager.init_app(app)
if settings.SENTRY_DSN:
    Sentry(app, dsn=settings.SENTRY_DSN)

# Register blueprints
app.register_blueprint(api)
app.register_blueprint(site)
app.register_blueprint(user)

# Register integrations
app.register_blueprint(github)
app.register_blueprint(s3)


# Set error handlers

@app.errorhandler(404)
def not_found_error(err):
    return (render_component('Error404'), 404)


@app.errorhandler(500)
def server_error(err):
    return (render_component('Error500'), 500)


@app.errorhandler(sqlalchemy.exc.SQLAlchemyError)
def error_handler(err):
    # To prevent session from break because of unhandled error with no rollback
    # https://github.com/frictionlessdata/goodtables.io/issues/97
    log.info('Database session rollback by server error handler')
    database['session'].rollback()
    raise err
