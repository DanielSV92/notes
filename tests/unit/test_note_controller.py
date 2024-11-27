import copy
import os
import logging
from flexmock import flexmock
from unittest import TestCase
from sqlalchemy.orm.query import Query
from notes.app import create_app
from notes.note import controller
from notes.domain.models import Notes
from notes.domain.models import NoteShare
from notes.extensions import db
from tests.fixtures import unit_test_fixtures

os.environ["POSTGRES_USER"] = 'postgres'
os.environ["POSTGRES_PASSWORD"] = 'postgres'
os.environ["POSTGRES_HOSTNAME"] = 'postgres'
os.environ["POSTGRES_DB"] = 'notes'

app = create_app()
app.app_context().push()


class TestController(TestCase):
    def setup_class(self):
        self.controller = controller

    def test_create_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_description': note.note_description
            }

            flexmock(Notes).should_receive('add').and_return(note)

            flexmock(db.session). \
                should_receive('commit')

            returned_value = self.controller.create_note(user, body)
            assert returned_value['note_description'] == body['note_description']

    def test_get_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_description': note.note_description
            }

            flexmock(Query). \
                should_receive('first').\
                and_return(note)

            returned_value = self.controller.get_note(user, note.note_id)
            assert returned_value['note_description'] == body['note_description']

    def test_get_all_notes(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            note_list = [{}]
            note_list[0] = note
            flexmock(Notes). \
                should_receive('query.filter.all').\
                and_return(note_list)
            
            flexmock(NoteShare). \
                should_receive('query.filter.all').\
                and_return([])

            returned_value = self.controller.get_all_notes(user)
            logging.info(returned_value)
            assert returned_value['my_notes'][0]['note_id'] == note.note_id

    def test_delete_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            flexmock(Query). \
                should_receive('first').\
                and_return(note)
            
            flexmock(Notes).should_receive('delete')
            flexmock(db.session). \
                should_receive('commit')


            self.controller.delete_note(user, note.note_id)

    def test_update_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_description': 'some new cool text'
            }

            flexmock(Query). \
                should_receive('first').\
                and_return(note)
            
            flexmock(db.session). \
                should_receive('commit')

            returned_value = self.controller.update_note(user, note.note_id, body)
            assert returned_value['note_description'] == body['note_description']

    def test_search_notes(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            note = copy.deepcopy(unit_test_fixtures.note)
            note_list = [{}]
            note_list[0] = note
            body = {
                'query': 'cool'
            }
            flexmock(Notes). \
                should_receive('query.filter.all').\
                and_return(note_list)
            
            flexmock(NoteShare). \
                should_receive('query.filter.all').\
                and_return([])

            returned_value = self.controller.search_note(user, body)
            assert returned_value['my_notes'][0]['note_id'] == note.note_id


    def test_share_note(self):
        with app.app_context():
            user = copy.deepcopy(unit_test_fixtures.user)
            user2 = copy.deepcopy(unit_test_fixtures.user2)
            note = copy.deepcopy(unit_test_fixtures.note)
            body = {
                'note_description': note.note_description
            }

            flexmock(Query). \
                should_receive('first').\
                and_return(user2)
            
            flexmock(Query). \
                should_receive('first').\
                and_return(note)
            
            flexmock(NoteShare).should_receive('add').and_return(note)

            flexmock(db.session). \
                should_receive('commit')

            returned_value = self.controller.share_note(user, note.note_id, user2.id)
            assert returned_value['note_description'] == body['note_description']