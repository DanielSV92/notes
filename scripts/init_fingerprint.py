import os
import sys
import sqlalchemy as db

engine = None
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', None)
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', None)
MYSQL_HOSTNAME = os.environ.get('MYSQL_HOSTNAME', None)
SMARTY_DBNAME = os.environ.get('SMARTY_DBNAME', None)

if len(sys.argv) != 1:
	print('usage: python3 init_fingerprint')
	exit(1)

url = "mysql+pymysql://{0}:{1}@{2}/{3}".format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOSTNAME, SMARTY_DBNAME)
engine = db.create_engine(url)

if engine:
	connection = engine.connect()
	metadata = db.MetaData()

	fingerprint = db.Table('fingerprint', metadata, autoload=True, autoload_with=engine)
	query = db.select([fingerprint])
	ResultProxy = connection.execute(query)

	if not ResultProxy.first():
		print('Initializing Fingerprint Table')
		query = db.insert(fingerprint)
		values_list = [
			{'fingerprint_type': 'camel', 'regex': r'[A-Z]([A-Z0-9]*[a-z][a-z0-9]*[A-Z]|[a-z0-9]*[A-Z][A-Z0-9]*[a-z])[A-Za-z0-9]*', 'generic_template': 'XxxXxx'},
			{'fingerprint_type': 'email', 'regex': r'[\w\.-]+@[\w\.-]+\.\w+', 'generic_template': 'X@X.X'},
			{'fingerprint_type': 'ip', 'regex': r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', 'generic_template': 'X.X.X.X'},
			{'fingerprint_type': 'url', 'regex': r'(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})', 'generic_template': 'X//X.X'},
			{'fingerprint_type': 'uuid', 'regex': r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}', 'generic_template': 'XX-X-X-X-XXX'}
		]
		ResultProxy = connection.execute(query, values_list)
	else:
		print('Fingerprint Table with data')
