from smarty.app import create_app
from smarty.extensions import db
from smarty.settings import DevConfig

app = create_app(DevConfig())

ctx = app.test_request_context()
ctx.push()

with app.app_context():
    db.create_all()

ctx.pop()
