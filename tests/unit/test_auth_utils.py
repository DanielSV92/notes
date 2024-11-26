import copy
import os
from unittest import TestCase
from unittest.mock import patch

import mock
from flexmock import flexmock
import smarty.errors as error

from sqlalchemy.orm.query import Query

from smarty.app import create_app
from smarty.auth import utils
from smarty.domain.models import user_datastore
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestUtils(TestCase):
    def setup_class(self):
        self.utils = utils

    def test_role_to_dict(self):
        role = copy.deepcopy(unit_test_fixtures.role)
        should_return = copy.deepcopy(unit_test_fixtures.role_dict)
        returned = utils.role_to_dict(role)
        assert returned == should_return

    def test_roles_to_dict(self):
        roles = [copy.deepcopy(unit_test_fixtures.role)]
        permissions = copy.deepcopy(unit_test_fixtures.permission_dict)
        role_dict = copy.deepcopy(unit_test_fixtures.role_dict)
        roles_dict = copy.deepcopy(unit_test_fixtures.roles_dict)
        roles_dict['Administrator']['permissions'] = permissions.get(
            'permissions')

        flexmock(utils)\
            .should_receive('role_to_dict')\
            .and_return(role_dict)

        flexmock(utils)\
            .should_receive('get_role_and_permissions')\
            .and_return(permissions)

        should_return = roles_dict
        returned = utils.roles_to_dict(roles)
        assert returned == should_return

    def test_account_pic_to_dict(self):
        account_pic = copy.deepcopy(unit_test_fixtures.account_pic)
        should_return = copy.deepcopy(unit_test_fixtures.account_pic_dict)
        returned = utils.account_pic_to_dict(account_pic)
        assert returned == should_return

    def test_permission_to_dict(self):
        permission = copy.deepcopy(unit_test_fixtures.permission)
        role_dict = copy.deepcopy(unit_test_fixtures.role_dict)
        should_return = copy.deepcopy(unit_test_fixtures.permission_dict)
        returned = utils.permission_to_dict(permission, role_dict)
        assert returned == should_return

    def test_get_user_by_email(self):
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(unit_test_fixtures.user_dict)
        token = 'token'

        flexmock(utils).\
            should_receive('validate_capability').\
            with_args(base_user, action='view_account_info').\
            and_return(False)

        self.assertRaises(error.Forbidden, utils.get_user_by_email, base_user,
                          'smth@ormuco.com')

        flexmock(utils).\
            should_receive('validate_capability').\
            with_args(token, action='view_account_info').\
            and_return(True)

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email='smth@ormuco.com').\
            and_return(None)

        flexmock(utils).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        returned = utils.get_user_by_email(token, base_user.email)
        assert returned == returned_user

        self.assertRaises(error.NotFound, utils.get_user_by_email, token,
                          'smth@ormuco.com')

    def test_get_role_and_permissions(self):
        role_dict = copy.deepcopy(unit_test_fixtures.role_dict)
        permission = copy.deepcopy(unit_test_fixtures.permission)

        # CapabilityList
        flexmock(Query). \
            should_receive('first'). \
            and_return(permission)

        should_return = copy.deepcopy(unit_test_fixtures.permission_dict)
        returned = utils.get_role_and_permissions(role_dict)
        assert returned == should_return

    def test_get_roles(self):
        user = copy.deepcopy(unit_test_fixtures.user)
        roles = [copy.deepcopy(unit_test_fixtures.role)]
        permissions = copy.deepcopy(unit_test_fixtures.permission_dict)
        roles_dict = copy.deepcopy(unit_test_fixtures.roles_dict)
        roles_dict['Administrator']['permissions'] = permissions.get(
            'permissions')

        flexmock(utils).\
            should_receive('validate_capability').\
            with_args(user, action='get_roles').\
            and_return(True)

        # Role
        flexmock(Query). \
            should_receive('all'). \
            and_return(roles)

        flexmock(utils).\
            should_receive('roles_to_dict').\
            and_return(roles_dict)

        should_return = roles_dict
        returned = utils.get_roles(user)
        assert returned == should_return

        flexmock(utils).\
            should_receive('validate_capability').\
            with_args(user, action='get_roles').\
            and_return(False)

        self.assertRaises(error.Forbidden, utils.get_roles, user)

    @patch('requests.post')
    def test_check_user_pass(self, mock_post):
        user = copy.deepcopy(unit_test_fixtures.user)
        token = 'token'

        mock_post.return_value = mock.Mock(status_code=200)
        mock_post.return_value.json.return_value = {
            'userId': user.id,
            'token': token
        }

        returned_value = self.utils.check_user_pass(user.email, user.password)

        mock_post.assert_called_with(
            'https://dev.spiderkube.io/spiderkube/v1/auth/validate/credentials',
            {
                'username': user.email,
                'password': user.password
            })

    def test_assign_role(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)

            flexmock(utils).\
                should_receive('validate_capability').\
                with_args(user, action='set_permissions').\
                and_return(True)

            body = {'email': user.email, 'role_name': 'Administrator'}
            role = unit_test_fixtures.role

            flexmock(user_datastore). \
                should_receive('find_user'). \
                with_args(email=body['email']). \
                and_return(user)

            flexmock(user_datastore). \
                should_receive('find_role'). \
                with_args(body['role_name']). \
                and_return(role)

            flexmock(user_datastore). \
                should_receive('add_role_to_user'). \
                with_args(user, role=role). \
                and_return(True)

            flexmock(user_datastore).should_receive('commit')

            flexmock(utils). \
                should_receive('user_to_dict'). \
                with_args(user). \
                and_return(unit_test_fixtures.user_dict)

            should_return = unit_test_fixtures.user_dict
            returned_value = self.utils.assign_role(user, body)
            assert returned_value == should_return
