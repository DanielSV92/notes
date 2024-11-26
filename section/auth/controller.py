import uuid

from flask_security.utils import hash_password
from flask_security.utils import login_user
from flask_security.utils import logout_user
from flask_security.utils import verify_password
import section.errors as error
from section.auth import utils
from section.domain.models import User
from section.domain.models import user_datastore
from section.extensions import db

def register(current_user, body: dict) -> dict:
    email = body['email']
    password = hash_password(body['password'])
    first_name = body.get('first_name', None)
    last_name = body.get('last_name', None)
    _uuid = uuid.uuid4()
    user_id = str(_uuid)

    user = User.query.filter(
            User.email == email,
        ).first()

    if user:
        raise error.Conflict(message='User already exists.')
    else:
        user = user_datastore.create_user(id=user_id,
                                          email=email,
                                          password=password,
                                          first_name=first_name,
                                          last_name=last_name)
    db.session.commit()

    auth_token = user.encode_auth_token(user.id)
    body = {
        'auth_token': auth_token,
        'user': utils.user_to_dict(user),
    }

    return body


def login(body: dict):
    email = body['email']
    password = body['password']

    user = User.query.filter(
        User.email == email,
    ).first()

    if not user:
        raise error.NotFound(message='Incorrect email or password')
    
    if not verify_password(password, user.password):
        raise error.Unauthorized(message='Incorrect email or password')

    login_user(user, False, ['email', 'password'])
    user = user_datastore.get_user(user.user_id)
    token = user.encode_auth_token(user.user_id)
    body = {
        'auth_token': token,
        'user': utils.user_to_dict(user),
    }
    
    return body



def logout():
    return logout_user()

