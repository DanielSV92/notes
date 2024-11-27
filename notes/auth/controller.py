import uuid
import base64
import logging
import notes.errors as error
from notes.auth import utils
from notes.domain.models import User
from notes.extensions import db

def register(body: dict) -> dict:
    email = body['email']
    password = base64.b64encode(body['password'].encode('ascii')).decode('ascii')
    first_name = body.get('first_name', None)
    last_name = body.get('last_name', None)
    _uuid = uuid.uuid4()
    user_id = str(_uuid)

    user = User.query.filter(
            User.email == email,
        ).first()

    if user:
        raise error.Conflict(message='User already exists.')

    user = User(id=user_id,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name)
    user.add()
    db.session.commit()

    user_dict = utils.user_to_dict(user)
    token = utils.encode_auth_token(user_dict['id'])
    body = {
        'auth_token': token,
        'user': user_dict
    }

    return body


def login(body: dict):
    email = body.get('email')
    password = body.get('password')

    user = User.query.filter(
        User.email == email,
    ).first()

    if not user:
        raise error.NotFound(message='Incorrect use or password')
    
    if password != base64.b64decode(user.password.encode('ascii')).decode('ascii'):
        raise error.Unauthorized(message='Incorrect something or password')

    user = User.query.filter(User.id == user.id).first()
    user_dict = utils.user_to_dict(user)
    token = utils.encode_auth_token(user_dict['id'])
    body = {
        'auth_token': token,
        'user': user_dict
    }
    
    return body
