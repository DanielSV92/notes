import logging
from functools import wraps

import requests
from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import redirect
from flask import request
from werkzeug.wrappers import response
import smarty.errors as error

from smarty.auth import controller
from smarty.auth import utils
from smarty.auth.utils import get_role_and_permissions
from smarty.domain.models import User
from smarty.settings import Config

blueprint = Blueprint('auth', __name__, url_prefix='/auth')


def _get_user_from_token(token) -> User:
    try:
        response = requests.get(f'{Config.SK_AUTH_HOSTNAME}/validate/login',
                                headers={'Authorization': f'Bearer {token}'})
        response.raise_for_status()
        user_id = response.json()['userId']
    except KeyError:
        raise error.Unauthorized()
    except requests.HTTPError as exc:
        cerebro_command = '[set.severity.healthy]'
        logging.error(f'{cerebro_command} {exc}')
        raise error.Unauthorized('Invalid token!')
    except Exception as exc:
        logging.error(exc)
        raise error.ServiceUnavailable('Unknown error while trying to validate token')

    user = controller.get_user_by_id(user_id)

    if not user.confirmed_at:
        raise error.Unauthorized('Account not validated')

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


def sk_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            sk_user = utils.get_sk_user(token)
            return f(sk_user, *args, **kwargs)
        raise error.Unauthorized('Token is missing')

    return decorated


def token_or_internal(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            user = _get_user_from_token(token)
            return f(user, *args, **kwargs)
        if request.headers.get('SMARTY-REQUEST-SOURCE') != 'External':
            return f(controller.get_user_by_id('proctor'), *args, **kwargs)
        raise error.Unauthorized('Token is missing')

    return decorated


def _role_to_dict(role):
    return {'id': role.id, 'name': role.name, 'description': role.description}


def _response_to_dict(payload) -> dict:
    roles = payload['user'].roles
    roles_list = []
    for rol in roles:
        roles_list.append(_role_to_dict(rol))

    role_and_permissions = get_role_and_permissions(roles_list[0]),
    login_dict = {
        'authentication_token': payload['auth_token'],
        'status': payload['status'],
        'message': payload['message'],
        'id': payload['user'].id,
        'is_root': payload['user'].is_root,
        'role_and_permissions': role_and_permissions,
        'user': {
            'user_id': payload['user'].id,
            'email': payload['user'].email,
            'first_name': payload['user'].first_name,
            'last_name': payload['user'].last_name,
            'phone_number': payload['user'].phone_number
        }
    }

    data_sources = payload.get('data_sources', False)
    if data_sources:
        login_dict['data_sources'] = data_sources

    return login_dict


def _token_to_dict(payload):
    return {
        'email': payload['data']['email'],
        'status': payload['status'],
    }


def get_valid_user(body):
    token = body.get('token')
    appflix_user = body.get('user')
    try:
        response = requests.get(f'{Config.SK_AUTH_HOSTNAME}/validate/login',
                                headers={'Authorization': f'Bearer {token}'})
        response.raise_for_status()
    except requests.HTTPError as exc:
        logging.error(exc)
        raise error.Unauthorized('Invalid token!')
    
    return controller.check_token_user(appflix_user, token)


@blueprint.route('/validate', methods=['GET'])
@token_required
def validate_token(_):
    return 'Token OK', 200


@blueprint.route('/create_admin', methods=['POST'])
def create_admin():
    body = request.get_json()
    controller.create_admin(body=body)

    return jsonify()


@blueprint.route('/token_user', methods=['POST'])
def token_user():
    body = request.get_json()
    response = get_valid_user(body)

    return jsonify(_response_to_dict(response))


@blueprint.route('/create_proctor', methods=['POST'])
def create_proctor():
    body = request.get_json()
    controller.create_proctor(body=body)

    return jsonify()


@blueprint.route('/register', methods=['POST'])
@token_required
def register(current_user):
    body = request.get_json()
    user = controller.register(current_user, body=body)

    return jsonify(user)


@blueprint.route('/delete_user', methods=['POST'])
@token_required
def delete_user(current_user):
    body = request.get_json()
    controller.delete_user(current_user, email=body['email'])

    response = Response(None, status=204)
    response.headers.remove('Content-Type')

    return response


@blueprint.route('/create_role', methods=['POST'])
@token_required
def create_role(current_user):
    body = request.get_json()
    role = controller.create_role(current_user, body=body)

    return jsonify(role)


@blueprint.route('/delete_role', methods=['POST'])
@token_required
def delete_role(current_user):
    body = request.get_json()
    controller.delete_role(current_user, role_name=body['role_name'])

    response = Response(None, status=204)
    response.headers.remove('Content-Type')

    return response


@blueprint.route('/get_roles', methods=['GET'])
@token_required
def get_roles(current_user):
    """
    Returns all the permission per role.

    :statuscode 200: OK.

    **Example Response**

    .. code-block:: json

        {
          "Administrator": {
            "description": "Can do everything",
            "id": 1,
            "name": "Administrator",
            "permissions": {
              "account": {
                "create_account": true,
                "delete_account": true,
                "get_roles": true,
                "reset_password": true,
                "set_permissions": true,
                "update_account": true,
                "update_billing_info": true,
                "view_account_info": true,
                "view_billing_info": true
              },
              "actions": {
                "add_action": true,
                "delete_action": true,
                "modify_action": true,
                "view_action": true
              },
              "alerts": {
                "add_alert": true,
                "delete_alert": true,
                "modify_alert": true
              },
              "data_sources": {
                "add_new_data_source": true,
                "delete_data_source": true,
                "update_data_source": true,
                "view_data_source_information": true
              },
              "labelling": {
                "add_a_new_label": true,
                "merge_by_labelling": true,
                "modify_label": true
              },
              "refinement": {
                "create_new_incident_by_refinement": true,
                "merge_by_refinement": true
              },
              "severity": {
                "modify_severity": true,
                "set_severity": true
              },
              "solutions": {
                "add_solution": true,
                "delete_solution": true,
                "modify_solution": true,
                "view_solution": true
              },
              "status": {
                "change_to_closed": true,
                "set_to_open": true
              }
            }
          },
          "Developer": {
            "description": "Support level 2",
            "id": 2,
            "name": "Developer",
            "permissions": {
              "account": {
                "create_account": false,
                "delete_account": false,
                "get_roles": false,
                "reset_password": true,
                "set_permissions": false,
                "update_account": false,
                "update_billing_info": false,
                "view_account_info": true,
                "view_billing_info": true
              },
              "actions": {
                "add_action": true,
                "delete_action": true,
                "modify_action": true,
                "view_action": true
              },
              "alerts": {
                "add_alert": true,
                "delete_alert": true,
                "modify_alert": true
              },
              "data_sources": {
                "add_new_data_source": true,
                "delete_data_source": false,
                "update_data_source": true,
                "view_data_source_information": true
              },
              "labelling": {
                "add_a_new_label": true,
                "merge_by_labelling": true,
                "modify_label": true
              },
              "refinement": {
                "create_new_incident_by_refinement": true,
                "merge_by_refinement": true
              },
              "severity": {
                "modify_severity": true,
                "set_severity": true
              },
              "solutions": {
                "add_solution": true,
                "delete_solution": true,
                "modify_solution": true,
                "view_solution": true
              },
              "status": {
                "change_to_closed": true,
                "set_to_open": true
              }
            }
          },
          "Guest": {
            "description": "Read only",
            "id": 4,
            "name": "Guest",
            "permissions": {
              "account": {
                "create_account": false,
                "delete_account": false,
                "get_roles": false,
                "reset_password": true,
                "set_permissions": false,
                "update_account": false,
                "update_billing_info": false,
                "view_account_info": true,
                "view_billing_info": true
              },
              "actions": {
                "add_action": false,
                "delete_action": false,
                "modify_action": false,
                "view_action": true
              },
              "alerts": {
                "add_alert": false,
                "delete_alert": false,
                "modify_alert": false
              },
              "data_sources": {
                "add_new_data_source": false,
                "delete_data_source": false,
                "update_data_source": false,
                "view_data_source_information": true
              },
              "labelling": {
                "add_a_new_label": false,
                "merge_by_labelling": false,
                "modify_label": false
              },
              "refinement": {
                "create_new_incident_by_refinement": false,
                "merge_by_refinement": false
              },
              "severity": {
                "modify_severity": false,
                "set_severity": false
              },
              "solutions": {
                "add_solution": false,
                "delete_solution": false,
                "modify_solution": false,
                "view_solution": true
              },
              "status": {
                "change_to_closed": false,
                "set_to_open": false
              }
            }
          },
          "Support": {
            "description": "Support level 1",
            "id": 3,
            "name": "Support",
            "permissions": {
              "account": {
                "create_account": false,
                "delete_account": false,
                "get_roles": false,
                "reset_password": true,
                "set_permissions": false,
                "update_account": false,
                "update_billing_info": false,
                "view_account_info": true,
                "view_billing_info": true
              },
              "actions": {
                "add_action": true,
                "delete_action": false,
                "modify_action": false,
                "view_action": true
              },
              "alerts": {
                "add_alert": true,
                "delete_alert": false,
                "modify_alert": true
              },
              "data_sources": {
                "add_new_data_source": false,
                "delete_data_source": false,
                "update_data_source": false,
                "view_data_source_information": true
              },
              "labelling": {
                "add_a_new_label": true,
                "merge_by_labelling": false,
                "modify_label": false
              },
              "refinement": {
                "create_new_incident_by_refinement": false,
                "merge_by_refinement": false
              },
              "severity": {
                "modify_severity": true,
                "set_severity": true
              },
              "solutions": {
                "add_solution": true,
                "delete_solution": false,
                "modify_solution": false,
                "view_solution": true
              },
              "status": {
                "change_to_closed": false,
                "set_to_open": true
              }
            }
          },
          "Visitor": {
            "description": "Read only its own data",
            "id": 6,
            "name": "Visitor",
            "permissions": {
              "account": {
                "create_account": false,
                "delete_account": false,
                "get_roles": false,
                "reset_password": true,
                "set_permissions": false,
                "update_account": false,
                "update_billing_info": false,
                "view_account_info": true,
                "view_billing_info": true
              },
              "actions": {
                "add_action": false,
                "delete_action": false,
                "modify_action": false,
                "view_action": true
              },
              "alerts": {
                "add_alert": false,
                "delete_alert": false,
                "modify_alert": false
              },
              "data_sources": {
                "add_new_data_source": false,
                "delete_data_source": false,
                "update_data_source": false,
                "view_data_source_information": true
              },
              "labelling": {
                "add_a_new_label": false,
                "merge_by_labelling": false,
                "modify_label": false
              },
              "refinement": {
                "create_new_incident_by_refinement": false,
                "merge_by_refinement": false
              },
              "severity": {
                "modify_severity": false,
                "set_severity": false
              },
              "solutions": {
                "add_solution": false,
                "delete_solution": false,
                "modify_solution": false,
                "view_solution": true
              },
              "status": {
                "change_to_closed": false,
                "set_to_open": false
              }
            }
          }
        }
    """
    roles = controller.get_roles(current_user, True)

    return jsonify(roles)


@blueprint.route('/get_all_roles_permissions', methods=['GET'])
@token_required
def get_all_roles_permissions(current_user):
    role_permissions = controller.get_all_roles_permissions()

    return jsonify(role_permissions)


@blueprint.route('/assign_role', methods=['POST'])
@token_required
def assign_role(current_user):
    body = request.get_json()
    user = controller.assign_role(current_user, body=body)

    return jsonify(user)


@blueprint.route('/remove_role', methods=['POST'])
@token_required
def remove_role(current_user):
    body = request.get_json()
    user = controller.remove_role(current_user, body=body)

    return jsonify(user)


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
          "data_sources": {
            "disabled_notifications": [],
            "private": {},
            "public": {},
            "shared_with_me": {
              "4fef9aed-9d74-4766-af35-4c764e912efe": {
                "display_name": "Ormuco Help Desk",
                "environments": {
                  "745": {
                    "datasource_type_id": 67,
                    "datasource_uuid": "4fef9aed-9d74-4766-af35-4c764e912efe",
                    "debug_mode": false,
                    "end_epoch": 0,
                    "env_display_name": "Help Desk",
                    "env_webhook": null,
                    "environment_id": 745,
                    "environment_status": "offline",
                    "features": [
                      "Incidents"
                    ],
                    "index_name": "no-needed",
                    "payload": {
                      "polling_time": 10
                    },
                    "total_tickets": 71
                  }
                },
                "id": 67,
                "loggers": [],
                "role_and_permissions": {
                  "permissions": {
                    "data_sources": {
                      "add_new_data_source": true                    }
                  },
                  "role_description": "Support level 2",
                  "role_id": 2,
                  "role_name": "Developer"
                },
                "scope": "shared_with_me",
                "source_type": "healthdesk",
                "status": "offline",
                "uuid": "4fef9aed-9d74-4766-af35-4c764e912efe"
              }
            }
          },
          "id": "3bd59550-597d-491b-86c7-bc8c30a44476",
          "is_root": false,
          "message": "Successfully logged in.",
          "role_and_permissions": [
            {
              "permissions": {
                "account": {
                  "create_account": true
                },
                "actions": {
                  "add_action": true
                },
                "alerts": {
                  "add_alert": true
                },
                "data_sources": {
                  "add_new_data_source": true
                },
                "labelling": {
                  "add_a_new_label": true
                },
                "refinement": {
                  "create_new_incident_by_refinement": true
                },
                "severity": {
                  "modify_severity": true
                },
                "solutions": {
                  "add_solution": true
                },
                "status": {
                  "change_to_closed": true
                }
              },
              "role_description": "Can do everything",
              "role_id": 1,
              "role_name": "Administrator"
            }
          ],
          "status": "success",
          "user": {
            "email": "my-email@domain.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone_number": "+1 800 400 900 7",
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


@blueprint.route('/set_admin_account', methods=['POST'])
def set_admin_account():
    body = request.get_json()
    response = controller.set_admin_account(body=body)
    return jsonify(_response_to_dict(response))


@blueprint.route('/user', methods=['GET'])
@token_required
def get_user(current_user):
    email = request.args.get('email', None)
    user = utils.get_user_by_email(current_user, email=email)

    return jsonify(user)


@blueprint.route('/user', methods=['PATCH'])
@token_required
def update_user(current_user):
    body = request.get_json()
    user = controller.update_user_by_email(current_user, body=body)

    return jsonify(user)


@blueprint.route('/users', methods=['GET'])
@token_required
def get_users(current_user):
    """
    Returns a list of all users, their status, roles and permissions.

    :query str search: Get users that match a partern,
    :query str role_name: Get all the users with a specific role in the data source.

    :statuscode 200: OK.

    **Example Response**

    .. code-block:: json

        [
          {
            "active": true,
            "confirmed": true,
            "email": null,
            "first_name": null,
            "id": "john.doe@email.com",
            "img_src": null,
            "last_name": null,
            "phone_number": null,
            "role_and_permissions": {
              "permissions": {
                "account": {
                  "create_account": false,
                  "delete_account": false,
                  "get_roles": false,
                  "reset_password": true,
                  "set_permissions": false,
                  "update_account": false,
                  "update_billing_info": false,
                  "view_account_info": true,
                  "view_billing_info": true
                },
                "actions": {
                  "add_action": false,
                  "delete_action": false,
                  "modify_action": false,
                  "view_action": true
                },
                "alerts": {
                  "add_alert": false,
                  "delete_alert": false,
                  "modify_alert": false
                },
                "data_sources": {
                  "add_new_data_source": false,
                  "delete_data_source": false,
                  "update_data_source": false,
                  "view_data_source_information": true
                },
                "labelling": {
                  "add_a_new_label": false,
                  "merge_by_labelling": false,
                  "modify_label": false
                },
                "refinement": {
                  "create_new_incident_by_refinement": false,
                  "merge_by_refinement": false
                },
                "severity": {
                  "modify_severity": false,
                  "set_severity": false
                },
                "solutions": {
                  "add_solution": false,
                  "delete_solution": false,
                  "modify_solution": false,
                  "view_solution": true
                },
                "status": {
                  "change_to_closed": false,
                  "set_to_open": false
                }
              },
              "role_description": "Read only",
              "role_id": 4,
              "role_name": "Guest"
            },
            "roles": [
              {
                "description": "Read only",
                "id": 4,
                "name": "Guest"
              }
            ]
          }
        ]
    """
    body = request.args.to_dict()
    user = controller.get_users(current_user, body, True)

    return jsonify(user)


@blueprint.route('/users/<datasource_uuid>', methods=['GET'])
@token_required
def get_users_by_ds(current_user, datasource_uuid):
    """
    Returns the users that have access to a data source.

    :param datasource_uuid: Data source UUID.

    :statuscode 200: OK.

    **Example Response**

    .. code-block:: json

        [
          {
            "active": true,
            "confirmed": true,
            "email": "email@server.com",
            "first_name": null,
            "id": "bfb3e323-7d44-4671-a937-23c92bf8ee17",
            "last_name": null,
            "phone_number": null
          }
        ]
    """
    user = controller.get_users_by_ds(current_user, datasource_uuid)

    return jsonify(user)


@blueprint.route('/status', methods=['GET'])
@token_required
def get_status(current_user):
    auth_token = request.headers.get('Authorization')
    if auth_token:
        response = controller.get_status(current_user)
    else:
        raise error.NotFound("Invalid token. Please log in again.")

    return jsonify(response)


@blueprint.route('/logout', methods=['POST'])
def logout():
    controller.logout()

    return jsonify({'message': 'success'})


@blueprint.route('/confirm_account/<token>', methods=['GET'])
def confirm_account(token):
    try:
        controller.confirm_account(token)
    except:
        return redirect(f'{Config.LOCATION}/error_validation')
    else:
        return redirect(f'{Config.LOCATION}/login')


@blueprint.route('/confirm_account', methods=['POST'])
def reconfirm_account():
    body = request.get_json()
    if controller.reconfirm_account(body):
        return jsonify({'message': 'Sending email success.'}, 200)
    else:
        return jsonify({'message': 'Fail to send email.'}, 500)


@blueprint.route('/reset_password/<token>', methods=['GET'])
def reset_password(token):
    try:
        controller.reset_password(token)
    except Exception:
        return redirect(f'{Config.LOCATION}/error_reset')
    else:
        return redirect(f'{Config.LOCATION}/reset_password/{token}')


@blueprint.route('/forgot_password', methods=['PUT'])
def forgot_password():
    body = request.get_json()
    user = controller.forgot_password(body)

    return jsonify(user)


@blueprint.route('/change_password', methods=['PATCH'])
@token_required
def update_password(current_user):
    body = request.get_json()
    user = controller.update_password(current_user, body=body)

    return jsonify(user)


@blueprint.route('/account_picture', methods=['PATCH'])
@token_required
def patch_account_picture(current_user):
    body = request.get_json()
    img_dict = controller.patch_default_account_picture(body)

    if not img_dict:
        return jsonify({'message': 'Default account picture missing.'}, 401)

    return jsonify(img_dict)


@blueprint.route('/account_picture', methods=['POST'])
@token_required
def post_account_picture(current_user):
    body = request.form

    if len(request.files) == 0:
        raise error.NotFound("No file uploaded")

    img = request.files['image']

    img_dict = controller.upload_account_picture(body, img)
    return jsonify(img_dict)


@blueprint.route('/account_picture', methods=['GET'])
@token_required
def get_account_picture(_):
    email = request.args.get('email', None)
    if not email:
        jsonify({'message': 'Email is missing'}, 400)
    img_dict = controller.get_account_picture(email)

    if not img_dict:
        return jsonify({'message': 'Account has no picture.'}, 200)

    return jsonify(img_dict)


@blueprint.route('/validate_email', methods=['POST'])
@sk_token_required
def validate_email(sk_user):
    user_email = request.get_json().get('user_email', None)
    if not user_email:
        jsonify({'message': 'Email is missing'}, 400)

    member = utils.validate_email(sk_user, user_email)
    return jsonify(member)
