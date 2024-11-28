import logging
from ratelimit import limits
from functools import wraps
from flask import Blueprint
from flask import jsonify
from flask import request
import notes.errors as error

from notes.auth import controller
from notes.auth import utils
from notes.domain.models import User

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def _get_user_from_token(token) -> User:
    try:
        user_id = utils.decode_auth_token(token)
    except KeyError:
        raise error.Unauthorized()
    except Exception as exc:
        logging.error(exc)
        raise error.ServiceUnavailable('Unknown error while trying to validate token')

    user = User.query.filter(User.id == user_id).first()

    if not user:
        raise error.Unauthorized('Invalid Token')

    return user


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            user = _get_user_from_token(token)
            return f(user, *args, **kwargs)
        raise error.Unauthorized('Token is missing')

    return decorated


@blueprint.route('/sign_up', methods=['POST'])
@limits(calls=15, period=900)
def register():
    body = request.get_json()
    user = controller.register(body=body)

    return jsonify(user)


@blueprint.route('/login', methods=['POST'])
@limits(calls=10, period=900)
def login():
    body = request.get_json()
    response = controller.login(body=body)

    return jsonify(response)

