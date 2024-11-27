import copy
import os

from unittest import TestCase
from notes.app import create_app
from notes.note import utils
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

    def test_note_to_dict(self):
        with app.app_context():
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_id': note.note_id,
                'note_description': note.note_description
            }
 
            returned_value = self.utils.note_to_dict(note)
            assert returned_value == body