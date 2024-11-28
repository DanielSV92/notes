import copy
import os

from unittest import TestCase
from notes.app import create_app
from notes.auth import utils
from tests.fixtures import unit_test_fixtures

os.environ["POSTGRES_USER"] = 'postgres'
os.environ["POSTGRES_PASSWORD"] = 'postgres'
os.environ["POSTGRES_HOSTNAME"] = 'postgres'
os.environ["POSTGRES_DB"] = 'notes'

app = create_app()
app.app_context().push()


class TestUtils(TestCase):
    def setup_class(self):
        self.utils = utils

    def test_util_user_to_dict(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            body = unit_test_fixtures.user_dict
 
            returned_value = self.utils.user_to_dict(user)
            assert returned_value == body
