import copy
import io
import os
from unittest import TestCase
from unittest.mock import patch

import mock
from flask_security.utils import hash_password
from flexmock import flexmock
import smarty.errors as error

from PIL import Image
from sqlalchemy.orm.query import Query
from werkzeug.datastructures import FileStorage

from smarty.app import create_app
from smarty.auth import controller
from smarty.auth import utils as auth_utils
from smarty.domain.models import AccountPicture
from smarty.domain.models import User
from smarty.domain.models import user_datastore
from smarty.extensions import db
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestController(TestCase):
    def setup_class(self):
        self.controller = controller

    def test_register(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            body = {
                'email': user.email,
                'password': 'password',
                'role_name': 'role'
            }

            flexmock(controller).\
                should_receive('validate_capability').\
                with_args(user, action='create_account').\
                and_return(True)

            flexmock(controller).\
                should_receive('_is_user').\
                with_args(user.email).\
                and_return(False)

            flexmock(db.session).should_receive('commit')

            flexmock(auth_utils).should_receive('send_email_validation')

            flexmock(controller).should_receive('assign_role').\
                and_return(user)

            should_return = user
            returned_value = self.controller.register(user, body)
            assert returned_value == should_return

    def test_delete_user(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            email = user.email

            flexmock(controller).\
                should_receive('validate_capability').\
                with_args(user, action='delete_account').\
                and_return(True)

            flexmock(user_datastore). \
                should_receive('find_user'). \
                with_args(email=user.email). \
                and_return(user)

            flexmock(user_datastore). \
                should_receive('delete'). \
                with_args(user). \
                and_return(None)

            should_return = None
            returned_value = self.controller.delete_user(user, email)
            assert returned_value == should_return

    def test_create_role(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            role = unit_test_fixtures.role
            body = {'name': role.name, 'description': role.description}

            flexmock(controller).\
                should_receive('validate_capability').\
                with_args(user, action='create_role').\
                and_return(True)

            flexmock(user_datastore). \
                should_receive('create_role'). \
                and_return(role)

            flexmock(user_datastore).should_receive('commit')

            should_return = unit_test_fixtures.role_dict
            returned_value = self.controller.create_role(user, body)
            assert returned_value == should_return

    def test_delete_role(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            role = unit_test_fixtures.role

            flexmock(controller).\
                should_receive('validate_capability').\
                with_args(user, action='delete_role').\
                and_return(True)

            flexmock(user_datastore). \
                should_receive('find_role'). \
                and_return(role)

            flexmock(user_datastore).should_receive('commit')

            should_return = None
            returned_value = self.controller.delete_role(user, role.name)
            assert returned_value == should_return

    def test_get_all_roles_permissions(self):
        with app.app_context():
            role = copy.deepcopy(unit_test_fixtures.role)
            permission = copy.deepcopy(unit_test_fixtures.permission)

            flexmock(Query).\
                should_receive('all').\
                and_return([role])

            flexmock(Query).\
                should_receive('first').\
                and_return(permission)

            should_return = [unit_test_fixtures.permission_dict]
            returned_value = self.controller.get_all_roles_permissions()
            assert returned_value == should_return

    def test_remove_role(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)

            flexmock(controller).\
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

            flexmock(user_datastore). \
                should_receive('remove_role_from_user'). \
                with_args(user, role=role). \
                and_return(True)

            flexmock(user_datastore).should_receive('commit')

            flexmock(controller). \
                should_receive('user_to_dict'). \
                with_args(user). \
                and_return(unit_test_fixtures.user_dict)

            should_return = unit_test_fixtures.user_dict
            returned_value = self.controller.remove_role(user, body)
            assert returned_value == should_return

    @patch('requests.get')
    @patch('requests.post')
    def test_login(self, mock_post, mocked_get):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            body = {'email': user.email, 'password': user.password}
            token = 'token'
            data_sources = unit_test_fixtures.data_source_dict

            mock_post.return_value = mock.Mock(status_code=200)
            mock_post.return_value.json.return_value = {
                'user': {
                    'id': user.id,
                    'is_org_admin': True
                },
                'token': token
            }
            mocked_get.return_value = mock.Mock(status_code=200)
            mocked_get.return_value.json.return_value = [{'name': 'Admin'}]

            flexmock(user_datastore). \
                should_receive('get_user'). \
                with_args(user.id). \
                and_return(user)

            flexmock(controller).should_receive('login_user')

            flexmock(controller). \
                should_receive('get_all_data_sources'). \
                with_args(user). \
                and_return(data_sources)

            flexmock(Query).should_receive('all').and_return([])

            flexmock(controller).\
                should_receive('create_user_role').\
                and_return(user)

            returned_value = self.controller.login(body)

            mock_post.assert_called_with(
                'https://dev.spiderkube.io/spiderkube/v1/auth/login', {
                    'username': user.email,
                    'password': user.password,
                    'get_os': False
                })

    def test_get_status(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)

            flexmock(controller). \
                should_receive('validate_capability'). \
                with_args(user, action='view_account_info'). \
                and_return(True)

            should_return = {
                'status': 'success',
                'data': {
                    'user_id': user.id,
                    'email': user.email
                }
            }
            returned_value = self.controller.get_status(user)
            assert returned_value == should_return

    def test_logout(self):
        flexmock(controller).should_receive('logout_user')
        should_return = None
        returned_value = self.controller.logout()
        assert returned_value == should_return

    def test_get_user_by_id(self):
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(unit_test_fixtures.user)

        flexmock(user_datastore).should_receive('get_user').with_args(
            returned_user.id).and_return(returned_user)
        flexmock(user_datastore).should_receive('get_user').with_args(
            3).and_return(None)

        returned = controller.get_user_by_id(returned_user.id)
        assert returned == base_user
        assert returned.id == base_user.id
        assert returned.first_name == base_user.first_name
        assert returned.last_name == base_user.last_name
        assert returned.phone_number == base_user.phone_number

        self.assertRaises(error.NotFound, controller.get_user_by_id, 3)

    def test_get_users(self):
        user = copy.deepcopy(unit_test_fixtures.user)
        role = copy.deepcopy(unit_test_fixtures.role)
        body = {'role_name': 'Administrator', 'search': 'juan'}

        flexmock(controller). \
            should_receive('validate_capability'). \
            with_args(user, action='view_account_info'). \
            and_return(True)

        # User
        flexmock(Query). \
            should_receive('all'). \
            and_return([])

        flexmock(controller). \
            should_receive('get_roles'). \
            with_args(user). \
            and_return([body['role_name']])

        # Role
        flexmock(Query). \
            should_receive('first'). \
            and_return(role)

        should_return = []
        returned_value = self.controller.get_users(user, body)
        assert returned_value == should_return

    def test_update_user_by_email(self):
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(unit_test_fixtures.user_dict_updated)
        user = unit_test_fixtures.user

        new_first_name = 'new_first_name'
        new_last_name = 'new_last_name'
        new_phone_number = 'new_phone_number'

        body = {
            'email': base_user.email,
            'first_name': new_first_name,
            'last_name': new_last_name,
            'phone_number': new_phone_number
        }

        flexmock(db.session).should_receive('commit')

        flexmock(controller).\
            should_receive('validate_capability').\
            with_args(user, action='update_account').\
            and_return(True)

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(controller).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        # all args
        returned = controller.update_user_by_email(user, body=body)

        assert returned.get('first_name') == new_first_name
        assert returned.get('last_name') == new_last_name
        assert returned.get('phone_number') == new_phone_number

        # each args individually
        # only first_name
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(
            unit_test_fixtures.user_dict_updated_first_name)
        body = {
            'email': base_user.email,
            'first_name': new_first_name,
        }

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(controller).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        returned = controller.update_user_by_email(user, body=body)

        assert returned.get('first_name') == new_first_name
        assert returned.get('last_name') == base_user.last_name
        assert returned.get('phone_number') == base_user.phone_number

        # only last_name
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(
            unit_test_fixtures.user_dict_updated_last_name)
        body = {
            'email': base_user.email,
            'last_name': new_last_name,
        }

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(controller).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        returned = controller.update_user_by_email(user, body=body)

        assert returned.get('first_name') == base_user.first_name
        assert returned.get('last_name') == new_last_name
        assert returned.get('phone_number') == base_user.phone_number

        # only phone_number
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(
            unit_test_fixtures.user_dict_updated_phone)
        body = {
            'email': base_user.email,
            'phone_number': new_phone_number,
        }

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(controller).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        returned = controller.update_user_by_email(user, body=body)

        assert returned.get('first_name') == base_user.first_name
        assert returned.get('last_name') == base_user.last_name
        assert returned.get('phone_number') == new_phone_number

        # no args
        base_user = copy.deepcopy(unit_test_fixtures.user)
        returned_user = copy.deepcopy(unit_test_fixtures.user_dict)
        body = {'email': base_user.email}

        flexmock(user_datastore).\
            should_receive('find_user').\
            with_args(email=base_user.email).\
            and_return(base_user)

        flexmock(controller).\
            should_receive('user_to_dict').\
            with_args(base_user).\
            and_return(returned_user)

        returned = controller.update_user_by_email(user, body=body)

        assert returned.get('first_name') == base_user.first_name
        assert returned.get('last_name') == base_user.last_name
        assert returned.get('phone_number') == base_user.phone_number

    def test__is_user(self):
        with app.app_context():
            user = unit_test_fixtures.user
            user.password = hash_password(user.password)

            flexmock(user_datastore). \
                should_receive('find_user'). \
                with_args(email=user.email). \
                and_return(user)

            should_return = True
            returned_value = self.controller._is_user(user.email)
            assert returned_value == should_return

            flexmock(user_datastore). \
                should_receive('find_user'). \
                with_args(email=user.email). \
                and_return(None)

            should_return = False
            returned_value = self.controller._is_user(user.email)
            assert returned_value == should_return

    def test_confirm_account(self):
        with app.app_context():
            user = unit_test_fixtures.user
            user.password = hash_password(user.password)
            user.confirmed_at = False
            token = 'token'

            flexmock(User). \
                should_receive('decode_auth_token'). \
                with_args(token). \
                and_return(user.id)

            flexmock(controller). \
                should_receive('get_user_by_id'). \
                with_args(user.id). \
                and_return(user)

            flexmock(user_datastore).should_receive('commit')

            should_return = None
            returned_value = self.controller.confirm_account(token)
            assert returned_value == should_return

    def test_upload_account_picture(self):
        with app.app_context():
            user = unit_test_fixtures.user
            body = {}
            body['email'] = user.email
            body['img_filename'] = "smth"

            flexmock(AccountPicture)
            ap = AccountPicture()

            flexmock(FileStorage)
            fs = FileStorage()
            fs.filename = 'test.png'

            jif = flexmock()
            jif.size = [100, 100]

            flexmock(user_datastore).\
                    should_receive('find_user').\
                    with_args(email=user.email).\
                    and_return(user)

            flexmock(Query).\
                should_receive('filter.first').\
                and_return(ap)

            flexmock(AccountPicture).should_receive('delete')
            flexmock(AccountPicture).should_receive('add')

            flexmock(db.session).should_receive('commit')

            flexmock(io).should_receive('BytesIO.getvalue').and_return(b'')

            flexmock(Image).should_receive('open').and_return(jif)

            returned = controller.upload_account_picture(body, fs)
            assert returned['img_filename'] == body['img_filename']
            assert returned['img_src'] == 'data:image/png;base64,'
            assert returned['privacy_level'] == 'private'

            flexmock(FileStorage)
            fs = FileStorage()
            fs.filename = 'test.jpg'

            returned = controller.upload_account_picture(body, fs)
            assert returned['img_filename'] == body['img_filename']
            assert returned['img_src'] == 'data:image/jpeg;base64,'
            assert returned['privacy_level'] == 'private'

            flexmock(FileStorage)
            fs = FileStorage()
            fs.filename = 'test.smth'

            self.assertRaises(error.Forbidden,
                              controller.upload_account_picture, body, fs)

            flexmock(FileStorage)
            fs = FileStorage()
            fs.filename = 'test.png'

            jif = flexmock()
            jif.size = [100, 50]
            flexmock(Image).should_receive('open').and_return(jif)

            self.assertRaises(error.Forbidden,
                              controller.upload_account_picture, body, fs)

    def test_get_account_picture(self):
        with app.app_context():
            user = unit_test_fixtures.user
            body = {}
            body['email'] = user.email

            flexmock(AccountPicture)
            ap = AccountPicture()
            ap.id = 1
            ap.img_filename = "filename"
            ap.img_src = 'data'
            ap.privacy_level = 'private'

            flexmock(Query).\
                should_receive('filter.first').\
                and_return(user).\
                and_return(ap)

            returned = controller.get_account_picture(body)
            assert returned['img_filename'] == "filename"
            assert returned['img_src'] == 'data'
            assert returned['privacy_level'] == 'private'

            flexmock(Query).\
                should_receive('filter.first').\
                and_return(user).\
                and_return([])

            should_return = None
            returned = controller.get_account_picture(body)
            assert returned == should_return

    def test_patch_default_account_picture(self):
        with app.app_context():
            user = unit_test_fixtures.user
            account_pic = copy.deepcopy(unit_test_fixtures.account_pic)
            account_pic_dict = unit_test_fixtures.account_pic_dict
            body = {'email': user.email, 'img_src': account_pic.img_src}

            flexmock(Query).\
                should_receive('first').\
                and_return(user).\
                and_return(account_pic)

            flexmock(user_datastore). \
                should_receive('find_user'). \
                with_args(email=user.email). \
                and_return(user)

            flexmock(controller). \
                should_receive('account_pic_to_dict'). \
                and_return(account_pic_dict)

            should_return = account_pic_dict
            returned = controller.patch_default_account_picture(body)
            assert returned == should_return

    def test_update_password(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            user.password = hash_password(user.password)
            user_dict = unit_test_fixtures.user_dict

            flexmock(controller). \
                should_receive('validate_capability'). \
                with_args(user, action='update_account'). \
                and_return(True)

            body = {}
            body['email'] = user.email
            body['old_password'] = 'notsecurepassword'
            body['new_password'] = 'supersecurepassword'
            body['reset_pass'] = True

            flexmock(controller).\
                should_receive('hash_password').\
                with_args(body['new_password']). \
                and_return(hash_password(body['new_password']))

            flexmock(db.session).should_receive('commit')

            flexmock(controller).\
                should_receive('user_to_dict').\
                with_args(user). \
                and_return(user_dict)

            should_return = user_dict
            returned_value = controller.update_password(user, body)
            assert returned_value == should_return
