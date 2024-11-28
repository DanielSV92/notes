import os
import sys
import sqlalchemy as db
from sqlalchemy_utils import database_exists, create_database

engine = None
POSTGRES_USER = os.environ.get('POSTGRES_USER', None)
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD', None)
POSTGRES_HOSTNAME = os.environ.get('POSTGRES_HOSTNAME', None)
POSTGRES_DB = os.environ.get('POSTGRES_DB', None)

if len(sys.argv) != 1:
    print('usage: python3 check_create_database')
    exit(1)

url = "postgresql+psycopg2://{0}:{1}@{2}/{3}".format(
    POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOSTNAME, POSTGRES_DB)
engine = db.create_engine(url)

if not database_exists(engine.url):
    create_database(engine.url)
    print('Creating notes database')
else:
    print(f'Database notes exist ==> {database_exists(engine.url)}')
