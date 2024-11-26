import datetime

import jwt
from flask_security import Security
from flask_security import SQLAlchemyUserDatastore
from flask_security import UserMixin
from smarty.domain.base import BaseModel
from smarty.extensions import db

class User(BaseModel, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.String(511), primary_key=True, nullable=False)
    email = db.Column(db.String(255), unique=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(100))
    current_login_ip = db.Column(db.String(100))
    login_count = db.Column(db.Integer)

    @staticmethod
    def encode_auth_token(user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp':
                datetime.datetime.utcnow() +
                datetime.timedelta(days=0, seconds=3600),
                'iat':
                datetime.datetime.utcnow(),
                'sub':
                user_id,
            }
            return jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Decodes the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, 'SECRET_KEY')
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'

class NoteShare(BaseModel):
    __tablename__ = 'note_share'

    id: int = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column('source_id', db.Integer(),
                          db.ForeignKey('notes.note_id', ondelete="CASCADE"))
    user_id = db.Column(db.ForeignKey('user.id', ondelete="CASCADE"),
                        nullable=False)

class Notes(BaseModel):
    __tablename__ = 'notes'

    note_id: int = db.Column(
            db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.ForeignKey('user.id', ondelete="CASCADE"),
                        nullable=False)
    note_description: str = db.Column(db.String(512), nullable=False)



# Setup Flask-Security
user_datastore = SQLAlchemyUserDatastore(db, User)
security = Security(datastore=user_datastore)
