"""The app module, containing the app factory function."""
import logging
import sys
import traceback

from celery import Celery
from celery.signals import setup_logging
from flask import Flask
from flask import Response
from flask import make_response

import smarty.errors as error

from smarty import agent
from smarty import auth
from smarty import celery
from smarty import commands
from smarty import health
from smarty import incidents
from smarty import on_call
from smarty import proctor
from smarty import prometheus
from smarty import neuron
from smarty.alerts import register_alerts_api
from smarty.data_sources import register_data_sources_api
from smarty.domain.models import CerebroSettings
from smarty.domain.models import security
from smarty.domain.models import user_datastore
from smarty.extensions import db
from smarty.extensions import ma
from smarty.extensions import mail
from smarty.extensions import migrate
from smarty.health_desk import register_health_desk_api
from smarty.reactions import register_reactions_api
from smarty.settings import ProdConfig
from smarty.slack import register_slack_api
from smarty.solutions import register_solutions_api


def create_app(config_object=None):
    logger = logging.getLogger()
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    file_handler = logging.FileHandler(filename='smarty.log', mode='w')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.getLogger().setLevel(logging.NOTSET)

    if config_object is None:
        config_object = ProdConfig()
    app = Flask(__name__.split('.')[0])

    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_shellcontext(app)
    register_commands(app)

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
    mail.init_app(app)
    migrate.init_app(app, db)
    security.init_app(app, user_datastore)


def register_blueprints(app):
    """Register Flask blueprints."""
    app.register_blueprint(health.views.blueprint)
    app.register_blueprint(agent.views.blueprint)
    app.register_blueprint(incidents.views.blueprint)
    app.register_blueprint(on_call.views.blueprint)
    app.register_blueprint(proctor.views.blueprint)
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(prometheus.views.blueprint)
    app.register_blueprint(neuron.views.blueprint)
    app.register_blueprint(celery.views.blueprint)
    register_slack_api(app)
    register_alerts_api(app)
    register_reactions_api(app)
    register_solutions_api(app)
    register_data_sources_api(app)
    register_health_desk_api(app)


def register_shellcontext(app):
    """Register shell context objects."""
    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
        }

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.urls)


def create_celery(app=None):
    """
    Create a new Celery object and tie together the Celery config to the app's
    config. Wrap all tasks in the context of the application.

    :param app: Flask app
    :return: Celery app
    """
    app = app or create_app(app.config)

    celery = Celery(app.import_name,
                    broker=app.config['CELERY_BROKER_URL'],
                    include=app.config['CELERY_TASK_LIST'])
    celery.conf.update(app.config)
    task_base = celery.Task

    @setup_logging.connect
    def setup_loggers(*args, **kwargs):
        logger = logging.getLogger(app.import_name).setLevel(logging.ERROR)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s')

        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            logging.error(f'Task {self.name} failed to be completed')

    celery.Task = ContextTask
    return celery

