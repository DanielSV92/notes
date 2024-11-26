import os
import sys
import datetime
import sqlalchemy as db

engine = None
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', None)
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', None)
MYSQL_HOSTNAME = os.environ.get('MYSQL_HOSTNAME', None)
SMARTY_DBNAME = os.environ.get('SMARTY_DBNAME', None)

if len(sys.argv) != 1:
    print('usage: python3 init_roles_and_permissions')
    exit(1)

url = "mysql+pymysql://{0}:{1}@{2}/{3}".format(MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOSTNAME, SMARTY_DBNAME)
engine = db.create_engine(url)

if engine:
    connection = engine.connect()
    metadata = db.MetaData()

    # role
    role = db.Table('role', metadata, autoload=True, autoload_with=engine)
    query = db.select([role])
    ResultProxy = connection.execute(query)

    if not ResultProxy.first():
        print('Initializing Role Table')
        query = db.insert(role)
        values_list = [
            {'name': 'Administrator', 'description': 'Can do everything'},
            {'name': 'Developer', 'description': 'Support level 2'},
            {'name': 'Support', 'description': 'Support level 1'},
            {'name': 'Guest', 'description': 'Read only'},
            {'name': 'Proctor', 'description': 'A new role that just covers what Proctor does'},
            {'name': 'Visitor', 'description': 'Read only its own data'},
        ]
        ResultProxy = connection.execute(query, values_list)
    else:
        print('Role Table with data')

    # proctor user
    user = db.Table('user', metadata, autoload=True, autoload_with=engine)
    query = db.select([user])
    ResultProxy = connection.execute(query)

    if not [proctor_user for proctor_user in ResultProxy if proctor_user.id == 'proctor']:
        print('Initializing user Table')
        query = db.insert(user)
        values_list = [{
            'id': 'proctor',
            'email': 'proctor@infra',
            'confirmed_at': datetime.datetime.now(),
            'is_root': False
        }]
        ResultProxy = connection.execute(query, values_list)

        query = db.select([role])
        ResultProxy = connection.execute(query)
        query = db.insert(db.Table('roles_users', metadata, autoload=True, autoload_with=engine))
        values_list = [{
            'user_id': 'proctor',
            'role_id': [proctor_role for proctor_role in ResultProxy if proctor_role.name == 'Proctor'][0].id
        }]
        ResultProxy = connection.execute(query, values_list)
    else:
        print('User Table with Proctor User')

    # capability_list
    capability_list = db.Table('capability_list', metadata, autoload=True, autoload_with=engine)
    query = db.select([capability_list])
    ResultProxy = connection.execute(query)

    if not ResultProxy.first():
        print('Initializing Capability List Table')
        query = db.insert(capability_list)
        values_list = [
            {
                "id": "1",
                "role_id": "1",
                "create_account": "1",
                "update_account": "1",
                "delete_account": "1",
                "create_role": "1",
                "delete_role": "1",
                "get_roles": "1",
                "set_permissions": "1",
                "update_billing_info": "1",
                "view_billing_info": "1",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "1",
                "delete_data_source": "1",
                "update_data_source": "1",
                "view_data_source_information": "1",
                "add_a_new_label": "1",
                "merge_by_labelling": "1",
                "modify_label": "1",
                "change_to_closed": "1",
                "modify_severity": "1",
                "set_severity": "1",
                "set_to_open": "1",
                "add_action": "1",
                "add_alert": "1",
                "add_solution": "1",
                "create_new_incident_by_refinement": "1",
                "delete_action": "1",
                "delete_alert": "1",
                "delete_solution": "1",
                "merge_by_refinement": "1",
                "modify_action": "1",
                "modify_alert": "1",
                "modify_solution": "1",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "1"
            },
            {
                "id": "2",
                "role_id": "2",
                "create_account": "0",
                "update_account": "0",
                "delete_account": "0",
                "create_role": "0",
                "delete_role": "0",
                "get_roles": "0",
                "set_permissions": "0",
                "update_billing_info": "0",
                "view_billing_info": "1",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "1",
                "delete_data_source": "0",
                "update_data_source": "1",
                "view_data_source_information": "1",
                "add_a_new_label": "1",
                "merge_by_labelling": "1",
                "modify_label": "1",
                "change_to_closed": "1",
                "modify_severity": "1",
                "set_severity": "1",
                "set_to_open": "1",
                "add_action": "1",
                "add_alert": "1",
                "add_solution": "1",
                "create_new_incident_by_refinement": "1",
                "delete_action": "1",
                "delete_alert": "1",
                "delete_solution": "1",
                "merge_by_refinement": "1",
                "modify_action": "1",
                "modify_alert": "1",
                "modify_solution": "1",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "1"
            },
            {
                "id": "3",
                "role_id": "3",
                "create_account": "0",
                "update_account": "0",
                "delete_account": "0",
                "create_role": "0",
                "delete_role": "0",
                "get_roles": "0",
                "set_permissions": "0",
                "update_billing_info": "0",
                "view_billing_info": "1",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "0",
                "delete_data_source": "0",
                "update_data_source": "0",
                "view_data_source_information": "1",
                "add_a_new_label": "1",
                "merge_by_labelling": "0",
                "modify_label": "0",
                "change_to_closed": "0",
                "modify_severity": "1",
                "set_severity": "1",
                "set_to_open": "1",
                "add_action": "1",
                "add_alert": "1",
                "add_solution": "1",
                "create_new_incident_by_refinement": "0",
                "delete_action": "0",
                "delete_alert": "0",
                "delete_solution": "0",
                "merge_by_refinement": "0",
                "modify_action": "0",
                "modify_alert": "1",
                "modify_solution": "0",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "0"
            },
            {
                "id": "4",
                "role_id": "4",
                "create_account": "0",
                "update_account": "0",
                "delete_account": "0",
                "create_role": "0",
                "delete_role": "0",
                "get_roles": "0",
                "set_permissions": "0",
                "update_billing_info": "0",
                "view_billing_info": "1",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "0",
                "delete_data_source": "0",
                "update_data_source": "0",
                "view_data_source_information": "1",
                "add_a_new_label": "0",
                "merge_by_labelling": "0",
                "modify_label": "0",
                "change_to_closed": "0",
                "modify_severity": "0",
                "set_severity": "0",
                "set_to_open": "0",
                "add_action": "0",
                "add_alert": "0",
                "add_solution": "0",
                "create_new_incident_by_refinement": "0",
                "delete_action": "0",
                "delete_alert": "0",
                "delete_solution": "0",
                "merge_by_refinement": "0",
                "modify_action": "0",
                "modify_alert": "0",
                "modify_solution": "0",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "0"
            },
            {
                "id": "5",
                "role_id": "5",
                "create_account": "0",
                "update_account": "0",
                "delete_account": "0",
                "create_role": "0",
                "delete_role": "0",
                "get_roles": "0",
                "set_permissions": "0",
                "update_billing_info": "0",
                "view_billing_info": "0",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "0",
                "delete_data_source": "0",
                "update_data_source": "1",
                "view_data_source_information": "1",
                "add_a_new_label": "1",
                "merge_by_labelling": "1",
                "modify_label": "1",
                "change_to_closed": "1",
                "modify_severity": "1",
                "set_severity": "1",
                "set_to_open": "1",
                "add_action": "0",
                "add_alert": "0",
                "add_solution": "0",
                "create_new_incident_by_refinement": "1",
                "delete_action": "0",
                "delete_alert": "0",
                "delete_solution": "0",
                "merge_by_refinement": "1",
                "modify_action": "0",
                "modify_alert": "0",
                "modify_solution": "0",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "1"
            },
            {
                "id": "6",
                "role_id": "6",
                "create_account": "0",
                "update_account": "0",
                "delete_account": "0",
                "create_role": "0",
                "delete_role": "0",
                "get_roles": "0",
                "set_permissions": "0",
                "update_billing_info": "0",
                "view_billing_info": "1",
                "reset_password": "1",
                "view_account_info": "1",
                "add_new_data_source": "0",
                "delete_data_source": "0",
                "update_data_source": "0",
                "view_data_source_information": "1",
                "add_a_new_label": "0",
                "merge_by_labelling": "0",
                "modify_label": "0",
                "change_to_closed": "0",
                "modify_severity": "0",
                "set_severity": "0",
                "set_to_open": "0",
                "add_action": "0",
                "add_alert": "0",
                "add_solution": "0",
                "create_new_incident_by_refinement": "0",
                "delete_action": "0",
                "delete_alert": "0",
                "delete_solution": "0",
                "merge_by_refinement": "0",
                "modify_action": "0",
                "modify_alert": "0",
                "modify_solution": "0",
                "view_action": "1",
                "view_alert": "1",
                "view_solution": "1",
                "execute_action": "0"
            }
        ]
        ResultProxy = connection.execute(query, values_list)
    else:
        print('Capability List Table with data')
