"""The app module, containing the app factory function."""
import logging
import sys
import traceback

from flask import Flask
from flask import Response
from flask import make_response

import notes.errors as error

from notes import note
from notes import auth
from notes.extensions import db
from notes.extensions import ma
from notes.extensions import migrate
from notes.settings import ProdConfig


def create_app(config_object=None):
    logger = logging.getLogger()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logging.getLogger().setLevel(logging.NOTSET)

    if config_object is None:
        config_object = ProdConfig()
    app = Flask(__name__.split('.')[0])

    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_shellcontext(app)

    @app.errorhandler(Exception)
    def handle_uncaught_exceptions(e: Exception):
        """
        Handle uncaught exceptions happening in the views. There
        are some special cases for custom exceptions.

        :param e: The Exception being passed. Since we cannot seem
            to be able to extract the stacktrace from the Exception object, we
            rely on sys.exc_info() instead that go fetch the latest error in
            the current thread.

        :return Response: A Flask response with the appropriate message for
            the type of exception.
        """

        if isinstance(e, error.NotFound):
            logging.exception(e.message)
            new_e = error.NotFound(message="Resource not found.")
            return Response(repr(new_e),
                            new_e.code,
                            content_type='application/json')
        if isinstance(e, error.Error):
            logging.exception(e)
            return Response(repr(e), e.code, content_type='application/json')
        else:
            traceback_str = "".join(
                traceback.format_exception(*sys.exc_info()))
            logging.warning(f'unhandled exception occurred \n{traceback_str}')

        return make_response('unhandled exception occurred', 500)

    return app


def register_extensions(app):
    """Register Flask extensions."""
    db.init_app(app)
    ma.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(note.views.blueprint)
    app.register_blueprint(auth.views.blueprint)


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
        }

    app.shell_context_processor(shell_context)
