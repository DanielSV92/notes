import copy
import os
import base64
from unittest import TestCase

from flexmock import flexmock
from sqlalchemy.orm.query import Query

from notes.app import create_app
from notes.auth import controller
from notes.auth import utils as auth_utils
from tests.fixtures import unit_test_fixtures

os.environ["POSTGRES_USER"] = 'postgres'
os.environ["POSTGRES_PASSWORD"] = 'postgres'
os.environ["POSTGRES_HOSTNAME"] = '120.0.1.1:5432'
os.environ["POSTGRES_DB"] = 'notes'

app = create_app()
app.app_context().push()


class TestController(TestCase):
    def setup_class(self):
        self.controller = controller
        self.utils = auth_utils

    def test_login(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            body = {
                'email': user.email,
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'password': user.password
            }
            token = 'token'
            user.password = base64.b64encode(user.password.encode('ascii')).decode('ascii')
            # User
            flexmock(Query). \
                should_receive('first'). \
                and_return(user)

            flexmock(auth_utils). \
                should_receive('encode_auth_token'). \
                with_args(user.id). \
                and_return(token)

            response = {
                'auth_token': token,
                'user': body
            }
            
            returned_value = self.controller.login(body)
            assert returned_value['auth_token'] == response['auth_token']
