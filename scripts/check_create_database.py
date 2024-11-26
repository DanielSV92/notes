import os
import sys
import sqlalchemy as db
from sqlalchemy_utils import database_exists, create_database

engine = None
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', None)
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', None)
MYSQL_HOSTNAME = os.environ.get('MYSQL_HOSTNAME', None)
SMARTY_DBNAME = os.environ.get('SMARTY_DBNAME', None)

if len(sys.argv) != 1:
    print('usage: python3 check_create_database')
    exit(1)

url = "mysql+pymysql://{0}:{1}@{2}/{3}".format(
    MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOSTNAME, SMARTY_DBNAME)
engine = db.create_engine(url)

if not database_exists(engine.url):
    create_database(engine.url)
    print('Creating smarty database')
else:
    print(f'Database smarty exist ==> {database_exists(engine.url)}')
