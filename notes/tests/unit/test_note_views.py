import copy
import os
import flask
from flexmock import flexmock
from unittest import TestCase
from notes.app import create_app
from notes.note import views
from tests.fixtures import unit_test_fixtures

os.environ["POSTGRES_USER"] = 'postgres'
os.environ["POSTGRES_PASSWORD"] = 'postgres'
os.environ["POSTGRES_HOSTNAME"] = 'postgres'
os.environ["POSTGRES_DB"] = 'notes'

app = create_app()
app.app_context().push()

class TestViews(TestCase):
    def setup_class(self):
        self.views = views

    def test_get_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_id': note.note_id,
                'note_description': note.note_description
            }

            flexmock(views.controller).\
                should_receive('get_note').\
                with_args(user, note.note_id).\
                and_return(body)
            
            flexmock(self.views).\
                should_receive('get_note').\
                and_return(body)
 
            returned_value = self.views.get_note(note)
            assert returned_value == body

    def test_get_all_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_id': note.note_id,
                'note_description': note.note_description
            }
            response = {
                'my_notes': [
                    body
                ],
                'shared_notes': []
            }

            flexmock(views.controller).\
                should_receive('get_all_notes').\
                with_args(user).\
                and_return(response)
            
            flexmock(self.views).\
                should_receive('get_all_notes').\
                and_return(response)
 
            returned_value = self.views.get_all_notes(user)
            assert returned_value['my_notes'][0] == body


    def test_share_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            user2 = copy.deepcopy(unit_test_fixtures.user2)
            body = {
                'note_id': note.note_id,
                'note_description': note.note_description
            }
            response = {
                'my_notes': [
                    body
                ],
                'shared_notes': []
            }

            flexmock(views.controller).\
                should_receive('share_note').\
                with_args(user, note.note_id, user2.id).\
                and_return(response)
            
            flexmock(self.views).\
                should_receive('share_note').\
                and_return(body)
 
            returned_value = self.views.share_note(user, note.note_id, user2.id)
            assert returned_value == body