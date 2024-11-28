"""Application configuration."""
import os

class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('NOTES_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ENV = None
    TESTING = False

    # Flask Security settings
    WTF_CSRF_ENABLED = False
    SECURITY_USER_IDENTITY_ATTRIBUTES = 'id'
    SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
    SECURITY_TRACKABLE = True
    SECURITY_PASSWORD_SALT = 'something_super_secret_change_in_production'
    SECURITY_TOKEN_MAX_AGE = 3600


    @property
    def db_uri_fragments(self):
        POSTGRES_USER = os.environ.get('POSTGRES_USER', None)
        POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', None)
        POSTGRES_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', None)
        POSTGRES_DB = os.environ.get('POSTGRES_DB', None)
        db_uri_fragments = []
        for name in [
            POSTGRES_USER,
            POSTGRES_PASSWORD,
            POSTGRES_HOSTNAME,
            POSTGRES_DB,
        ]:
            var = os.environ.get(name, None)
            db_uri_fragments.append((var, name))

        return db_uri_fragments

    def check_db_uri_fragments(self):
        """Raise an Exception if any
        db fragments are unset.
        """
        for frag, var_name in self.db_uri_fragments:
            if frag is None:
                raise Exception(
                    "Missing environment variable '{0}'".format(var_name))

    @property
    def set_sqlalchemy_database_uri(self):
        try:
            self.check_db_uri_fragments()
        except Exception as e:
            if self.ENV == 'test':
                # Default to in-memory SQLite for testing environments
                # if we don't have MySQL connection information.
                return 'sqlite:///'
            elif self.ENV == 'dev':
                # Default to file-backed SQLite for dev environments
                # if we don't have MySQL connection information.
                db_path = os.path.join(self.PROJECT_ROOT, 'dev.db')
                return f'sqlite:///{db_path}'
            else:
                raise e

        return "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
            *[e[0] for e in self.db_uri_fragments])
    SQLALCHEMY_DATABASE_URI: str = set_sqlalchemy_database_uri

class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False
    SQLALCHEMY_POOL_SIZE: int = 50
    SQLALCHEMY_MAX_OVERFLOW: int = 70


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True
    SQLALCHEMY_POOL_SIZE: int = 50
    SQLALCHEMY_MAX_OVERFLOW: int = 70


class TestConfig(Config):
    """Test configuration."""
    ENV = 'test'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Bcrypt algorithm hashing rounds (reduced for testing purposes only!)
    BCRYPT_LOG_ROUNDS = 4
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True

    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False
