from notes.app import create_app
from notes.extensions import db
from notes.settings import DevConfig

app = create_app(DevConfig())

ctx = app.test_request_context()
ctx.push()

with app.app_context():
    db.create_all()

ctx.pop()
