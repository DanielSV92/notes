"""Application configuration."""
import os

from nltk.corpus import stopwords


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('SMARTY_SECRET', 'secret-key')
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

    # Survey Security
    SURVEY_KEY = b'-G_y2bQNWT5lPlDpsU9lo4LtgVMC-8bc7aTWpshGfi4='

    # cerebro's email account info
    INTERNAL_MAIL_SERVER = 'smtp.gmail.com'
    INTERNAL_MAIL_PORT = 465
    INTERNAL_MAIL_USE_TLS = False
    INTERNAL_MAIL_USE_SSL = True
    INTERNAL_MAIL_USERNAME = 'cerebro.montreal@gmail.com'
    INTERNAL_MAIL_PASSWORD = 'uywncbqjrcgrdvun'

    # SMTP global variables
    MAIL_SERVER = INTERNAL_MAIL_SERVER
    MAIL_PORT = INTERNAL_MAIL_PORT
    MAIL_USE_TLS = INTERNAL_MAIL_USE_TLS
    MAIL_USE_SSL = INTERNAL_MAIL_USE_SSL
    MAIL_USERNAME = INTERNAL_MAIL_USERNAME
    MAIL_PASSWORD = INTERNAL_MAIL_PASSWORD

    # Prometheus env status check
    PROMETHEUS_ENVS_STATUS = {}
    PROMETHEUS_SCOPES = ['metric', 'service_up', 'deos_user']

    # Swift All-in-One (saio) credential and endpoints
    SAIO_ACCOUNT: str = os.environ.get('SWIFT_ACCOUNT', 'cerebro')
    SAIO_NAME: str = os.environ.get('SWIFT_USER', 'cerebrom')
    SAIO_PASSWORD: str = os.environ.get('SWIFT_PASSWORD', 'changeme')
    SAIO_CONTAINER = "incident_type"
    SAIO_ID_ENDPOINT: str = os.environ.get('SWIFT_HOSTNAME', 'cerebro-swift')
    SAIO_PORT: str = os.environ.get('SWIFT_PORT', '80')
    SWIFT_ENDPOINT: str = f'http://{SAIO_ID_ENDPOINT}:{SAIO_PORT}'
    if SAIO_PORT in ('443', '8443'):
        SWIFT_ENDPOINT: str = f'https://{SAIO_ID_ENDPOINT}'

    # Proctor endpoint
    PROCTOR_HOSTNAME: str = os.environ.get('PROCTOR_HOSTNAME',
                                           'cerebro-proctor')
    PROCTOR_PORT: str = os.environ.get('PROCTOR_PORT', '80')

    # Scheduler endpoint
    SCHEDULER_HOSTNAME: str = os.environ.get(
        'SCHEDULER_HOSTNAME', 'cerebro-scheduler')
    SCHEDULER_PORT: str = os.environ.get('SCHEDULER_PORT', '80')

    SOLVER_HOSTNAME: str = os.environ.get('SOLVER_HOSTNAME', 'cerebro-solver')
    SOLVER_PORT: str = os.environ.get('SOLVER_PORT', '80')

    #  RabbitMQ specifications
    BROKER_URL = os.environ.get('BROKER_URL', 'cerebro-queue')
    CELERY_BROKER_URL = f"pyamqp://guest:guest@{BROKER_URL}:5672//"
    CELERY_RESULT_EXTENDED = True
    CELERY_TASK_LIST = [
        'smarty.celery.celery_datasource_tasks',
        'smarty.celery.celery_incidents_tasks',
        'smarty.celery.celery_proctor_tasks'
    ]

    CELERYD_TIME_LIMIT = 600
    CELERY_RETENTION_DAYS = 5

    # Cerebro marketplace
    CEREBRO_MARKET_URL: str = os.environ.get('CEREBRO_MARKET_URL')

    # SocketIO
    SOCKETIO_SERVER: str = os.environ.get(
        'SOCKETIO_SERVER',
        'https://cerebro.spiderkube.io/cerebro/v1/event/server')

    # Refinement, Mapping
    REFINE_BLOCKED: bool = False
    MAPPING_BLOCKED: bool = False
    CURRENT_MAPPINGS = {}
    CURRENT_REFINEMENTS = []
    AFFECTED_INCIDENT_TYPES = set()

    # Authentication variables
    LOCATION: str = os.environ.get('LOCATION')
    AUTH_ENDPOINT: str = os.environ.get('AUTH_ENDPOINT')
    PASS_ENDPOINT: str = os.environ.get('PASS_ENDPOINT')
    SK_ADMIN_USER: str = os.environ.get('SK_ADMIN_USER')
    SK_ADMIN_PASS: str = os.environ.get('SK_ADMIN_PASS')
    SK_AUTH_HOSTNAME: str = os.environ.get(
        'SK_AUTH_HOSTNAME', 'https://dev.spiderkube.io/spiderkube/v1/auth')

    # Cerebro' Slack API credential
    CLIENT_ID: str = os.environ.get('CLIENT_ID', '8959570291.393663996704')
    CLIENT_SECRET: str = os.environ.get(
        'CLIENT_SECRET', '17e9605cd74e89854c3d58dfe1cf4333')
    
    # Cerebro Microsoft helpdek api credentials
    MS_CLIENT_ID = os.environ.get('CLIENT_ID', '627ee4a9-528f-417a-be9e-ed560b082e77')
    MS_CLIENT_SECRET = os.environ.get('MS_CLIENT_SECRET', 'k1j8Q~DjfkqRhjcDS4L-Ej7jCqqzqrp405jkYcq_')
    MS_AUTHORITY = os.environ.get('MS_AUTHORITY', 'https://login.microsoftonline.com/common')
    MS_CAPABILITY = ['CP1']
    MS_SCOPES = ["Mail.ReadWrite", "Mail.Send", "User.Read"]

    # DeOS
    DEOS_HOST: str = os.environ.get('DEOS_HOST', 'https://yul.appfeine.com')

    # Sorting by options
    SORT_INCIDENT_BY = [
        'occurrence_date', 'created_date', 'name', 'occurrences',
        'number_solutions', 'last_occurrence_date', 'current_severity'
    ]

    SORT_FLAGS_BY = [
        'solution_id', 'flag_author', 'flag_datetime', 'status', 'reviewer'
    ]

    SEVERITIES = {
        'Unknown': 0,
        'Healthy': 1,
        'Low': 2,
        'Medium': 3,
        'High': 4,
        'Critical': 5
    }

    MAIN_STATE = ['open', 'closed', 'all']

    # Cerebro's commands
    CEREBRO_COMMANDS = [
        'set.severity.healthy', 'set.severity.low', 'set.severity.medium',
        'set.severity.high', 'set.severity.critical'
    ]

    # Special DS
    DS_TYPES = ['prometheus', 'healthdesk', 'elastic', 'hayei']
    SPECIAL_DS_TYPES = ['prometheus', 'healthdesk']
    HELP_DESK_UUID = 'fad785d5-e050-4b16-9905-5a7f69760709'
    HELP_DESK_VERSION = 1
    HELP_DESK_EMAIL = 'spiderkube-admin@ormuco.com'
    SUPPORT_EMAIL = 'support@ormuco.com'

    # Default search query
    SEARCH_QUERY = {
        "query": "error*",
        "fields": [
            "log^4",
            "Payload^.1",
            "log_level^4"
        ]
    }

    # Help desk globals in min
    RESPONSE_TIME_DAYS: float = 1.0
    SLA_NEW: int = 15
    RESOLUTION_TIME: dict = {
        'critical': 1 * 60,
        'high': 1 * 60,
        'medium': 48 * 60,
        'low': 120 * 60,
        'healthy': 0,
        'unknown': 15
    }

    ORMUCO_STOP_WORDS = [
        'lissette', 'hernando', 'ormuco', 'samuel', 'queiroz', 'medeiros',
        'andre', 'beeline', 'vas',
    ]
    NEW_STOP_WORDS = [
        'and', 'I', 'A', 'And', 'So', 'arnt', 'This', 'When', 'It', 'many', 'Many', 'so',
        'cant', 'Yes', 'yes', 'No', 'no', 'These', 'these',
        'january', 'february', 'march', 'april', 'may', 'june',
        'july', 'august', 'september', 'october', 'november', 'december',
        'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday',
    ]
    STOP_WORDS = stopwords.words('english')

    # On-call
    DEFAULT_NOTIFICATIONS = [1]

    # Other flags
    SANITATION_IN_PROCESS = set()
    DELETE_IN_PROCESS = set()
    TABLES_BY_DS_UUID = [
        'ElasticSearchStatus',
        'ESHourStatus',
        'ESDayStatus',
        'SSHReaction',
        'APIReaction',
        'CategoryOccurrences',
        'ProctorTrainingData',
        'Reaction',
        'IncidentStateEvent',
        'IncidentOwnershipEvent',
        'IncidentTypeSeverityEvent',
        'IncidentTypeRefinementEvent',
        'IncidentTypeLabelEvent',
        'IncidenttypeHistory',
        'IncidentExternalSolution',
        'IncidentRule',
        'IncidentResponse',
        'Incident',
        'ProctorModel',
        'CerebroAgent',
        'HelpdeskEmail',
        'HelpdeskServer',
    ]

    # DeOS
    NO_APPS = ['POD', 'appflix', 'openbox', 'xvfb', 'pulseaudio']

    # OpenAI
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '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')
    MODEL_ENGINE = "text-davinci-003"
    CHAT_GPT_MODEL = "gpt-3.5-turbo"

    # Twilio
    TWILIO_ACCOUNT_SID = 'AC0ae16da2b2d18d7cb1f6de4dd5496784'
    TWILIO_AUTH_TOKEN = 'e4ecbc3b5ed28c28679043d919c13cd0'
    TWILIO_PHONE_NUMBER = '+17146768940',

    # Microsoft
    MESSAGES_END_POINT = "https://graph.microsoft.com/v1.0/me/messages"
    MAILFOLDERS_END_POINT = "https://graph.microsoft.com/v1.0/me/mailfolders"
    TOKEN_ROOT = 'token_cache' 
    TOKEN_EXTENSION = 'bin' 

    @property
    def db_uri_fragments(self):
        db_uri_fragments = []
        for name in [
                'MYSQL_USERNAME',
                'MYSQL_PASSWORD',
                'MYSQL_HOSTNAME',
                'SMARTY_DBNAME',
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

        return "mysql+pymysql://{0}:{1}@{2}/{3}".format(
            *[e[0] for e in self.db_uri_fragments])

    @property
    def get_celery_backend(self):
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

        return "db+mysql+pymysql://{0}:{1}@{2}/{3}".format(
            *[e[0] for e in self.db_uri_fragments])

    SQLALCHEMY_DATABASE_URI: str = set_sqlalchemy_database_uri
    CELERY_RESULT_BACKEND: str = get_celery_backend


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

    # Bcrypt algorithm hashing rounds (reduced for testing purposes only!)
    BCRYPT_LOG_ROUNDS = 4
    # Enable the TESTING flag to disable the error catching during request handling
    # so that you get better error reports when performing test requests against the application.
    TESTING = True

    # Disable CSRF tokens in the Forms (only valid for testing purposes!)
    WTF_CSRF_ENABLED = False
