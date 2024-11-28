"""Defines fixtures available to all tests."""

import pytest
import base64
from notes.app import create_app
from notes.domain.models import NoteShare
from notes.domain.models import Notes
from notes.domain.models import User
from notes.extensions import db as _db
from notes.settings import TestConfig

@pytest.fixture(scope='session')
def app():
    flask_app = create_app(TestConfig())

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='session')
def test_client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def init_database(app):
    # Create the database and the database table
    _db.app = app
    _db.create_all()

    # Insert user data
    user = User(id=1,
                email='admin@gmail.com',
                password=base64.b64encode("test".encode('ascii')).decode('ascii'),
                first_name="jean",
                last_name="guy")
    user_2 = User(id=2,
                  email='admin2@gmail.com',
                  password=base64.b64encode("test".encode('ascii')).decode('ascii'),
                  first_name="john",
                  last_name="smith")

    _db.session.add(user)
    _db.session.add(user_2)
    _db.session.commit()

    # Insert note data
    note = Notes(note_id=1,
                 owner_id=1,
                 note_description="a very cool note")
    note2 = Notes(note_id=2,
                owner_id=2,
                note_description="an awesome text for note")
    _db.session.add(note)
    _db.session.add(note2)
    _db.session.commit()

    share_note = NoteShare(id=1,
                           note_id=2,
                           user_id=1)
    _db.session.add(share_note)
    _db.session.commit()


    yield _db  # this is where the testing happens!
    
    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(init_database):
    connection = init_database.engine.connect()
    connection.close()
