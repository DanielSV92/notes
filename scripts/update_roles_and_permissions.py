import json
import sys 
import sqlalchemy as db

engine = None

if len(sys.argv) != 2:
	print('usage: python3 update_roles_and_permissions <destination>')
	print('<destination>: local, remote')

	exit(1)

if sys.argv[1] == 'local':
	engine = db.create_engine('mysql+pymysql://whatever:changeme@127.0.0.1:3307/smarty')
elif sys.argv[1] == 'remote':
	engine = db.create_engine('mysql+pymysql://whatever:changeme@127.0.1.1:3307/smarty')
else:
	print('usage: python3 update_roles_and_permissions <destination>')
	print('<destination>: local, remote')

if engine:
	connection = engine.connect()
	metadata = db.MetaData()

	capability_list = db.Table('capability_list', metadata, autoload=True, autoload_with=engine)
	query = db.select([capability_list])
	ResultProxy = connection.execute(query)

	if ResultProxy:
		print('Updating Capability List')
		admin = db.update(capability_list).where(capability_list.columns.role_id <= 2).values(execute_action = 1)
		ResultProxy = connection.execute(admin)
	else:
		print('There is not such Table')
