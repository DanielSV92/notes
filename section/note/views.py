import json
import logging
from functools import wraps

from flask import Blueprint
from flask import Response
from flask import jsonify
from flask import request
import smarty.errors as error

from smarty.agent import controller
from smarty.agent.utils import decode_auth_token
from smarty.auth.views import token_required
from smarty.domain.models import CerebroAgent

blueprint = Blueprint('agent', __name__, url_prefix='/agent')


def _get_agent_from_token(token) -> CerebroAgent:
    agent_uuid = decode_auth_token(token)

    agent = controller.get_agent_by_id(agent_uuid)

    if not agent:
        raise error.BadRequest('Invalid agent uuid.')

    return agent


def agent_token(fun):
    @wraps(fun)
    def decorated(*args, **kwargs):
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            agent = _get_agent_from_token(token)
            return fun(agent, *args, **kwargs)
        raise error.Unauthorized('Token is missing')

    return decorated


@blueprint.route('/<datasource_uuid>/<environment_id>/create_agent',
                 methods=['POST'])
@token_required
def create_agent(current_user, datasource_uuid, environment_id):
    body = request.get_json()
    agent = controller.create_agent(current_user, datasource_uuid,
                                    environment_id, body)
    return jsonify(agent)


@blueprint.route('/<datasource_uuid>/<environment_id>/update_agent',
                 methods=['PATCH'])
@token_required
def update_agent(current_user, datasource_uuid, environment_id):
    body = request.get_json()
    agent = controller.update_agent(current_user, datasource_uuid,
                                    environment_id, body)
    return jsonify(agent)


@blueprint.route('/<datasource_uuid>/<environment_id>/delete_agent',
                 methods=['DELETE'])
@token_required
def delete_agent(current_user, datasource_uuid, environment_id):
    controller.delete_agent(current_user, datasource_uuid, environment_id)

    response = Response(None, status=204)
    response.headers.remove('Content-Type')

    return response


@blueprint.route('/<datasource_uuid>/<environment_id>/get_agent',
                 methods=['GET'])
@token_required
def get_env_agent(current_user, datasource_uuid, environment_id):
    agent = controller.get_env_agent(current_user, datasource_uuid,
                                     environment_id)
    return jsonify(agent)


@blueprint.route('/<datasource_uuid>/get_agents', methods=['GET'])
@token_required
def get_all_agents(current_user, datasource_uuid):
    agent_list = controller.get_all_agents(current_user, datasource_uuid)
    return jsonify(agent_list)


@blueprint.route('/poll_scripts', methods=['GET'])
@agent_token
def get_scripts(current_agent):
    body = request.json
    agent_key = request.headers.get('Agent_key')
    signed_secret = body.get('signed_secret')
    encrypted_secret = body.get('encrypted_secret')
    value, message = controller.check_agent_key(current_agent, agent_key,
                                                bytes(signed_secret),
                                                bytes(encrypted_secret))

    signed_cerebro, encrypted_cerebro = controller.encrypt_secret(
        current_agent, value)
    security = {
        'valid_sign': list(signed_cerebro),
        'valid_encrypt': list(encrypted_cerebro)
    }
    extra_val = json.loads(current_agent.password.decode())
    agent_frequency = extra_val.get('frequency')

    if value != 200:
        security['message'] = message
        return Response(response=json.dumps(security),
                        status=value,
                        headers={'Content-Type': 'application/json'})
    logging.info('Polling scripts for agent %s', current_agent.agent_name)
    agent_list = controller.poll_scripts(current_agent)
    if not agent_list:
        return jsonify(actions=[], security=security, frequency=agent_frequency)

    return jsonify(actions=agent_list,
                   security=security,
                   frequency=agent_frequency)


@blueprint.route('/save_response', methods=['POST'])
@agent_token
def save_agent_result(_):
    body = request.json

    controller.save_agent_result(body)
    response = Response(None, status=204)

    return response
