import logging
from functools import wraps
from flask import Blueprint
from flask import jsonify
from flask import request
import smarty.errors as error

from section.auth import controller
from section.auth import utils
from section.domain.models import user_datastore
from section.domain.models import User

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def _get_user_from_token(token) -> User:
    try:
        response = utils.decode_auth_token(token)
        user_id = response.json()['userId']
    except KeyError:
        raise error.Unauthorized()
    except Exception as exc:
        logging.error(exc)
        raise error.ServiceUnavailable('Unknown error while trying to validate token')

    user = user_datastore.get_user(user_id)

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


def _response_to_dict(payload) -> dict:
    login_dict = {
        'authentication_token': payload['auth_token'],
        'id': payload['user'].id,
        'user': {
            'user_id': payload['user'].id,
            'email': payload['user'].email,
            'first_name': payload['user'].first_name,
            'last_name': payload['user'].last_name,
            'phone_number': payload['user'].phone_number
        }
    }

    return login_dict


@blueprint.route('/register', methods=['POST'])
def register():
    body = request.get_json()
    user = controller.register(body=body)

    return jsonify(_response_to_dict(user))


@blueprint.route('/login', methods=['POST'])
def login():
    """
    Returns user information, the data sources available to the user, the roles and permissions, and the authentication token.

    :<json str username: login username (E-Mail address).
    :<json str password: account password.

    :statuscode 200: OK.

    **Example Request**

    .. code-block:: json

        {
          "username": "my-email@domain.com",
          "password": "p4SSw0rd"
        }

    **Example Response**

    .. code-block:: json

       {
          "authentication_token": "token",
          "id": "3bd59550-597d-491b-86c7-bc8c30a44476",
          "user": {
            "email": "my-email@domain.com",
            "first_name": "John",
            "last_name": "Doe",
            "user_id": "3bd59550-597d-491b-86c7-bc8c30a44476"
          }
        }

    .. note:: Every call requires the ``authentication_token`` to be sent via
        the Authorization header. A 401 UNAUTHORIZED status code will be sent back
        if credentials are missing.
    """
    body = request.get_json()
    response = controller.login(body=body)

    return jsonify(_response_to_dict(response))


@blueprint.route('/logout', methods=['POST'])
def logout():
    controller.logout()

    return jsonify({'message': 'success'})

