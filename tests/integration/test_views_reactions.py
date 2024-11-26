import datetime
import json

import pytest
import requests
from flexmock import flexmock

from smarty.domain.models import User
from smarty.proctor import utils as proctor_utils
from tests.fixtures import integration_test_fixtures as fixtures


@pytest.fixture(autouse=True)
def mockToken():
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())

    flexmock(proctor_utils).should_receive('get_openai_details').and_return(None)
    flexmock(proctor_utils).should_receive('get_openai_solution').and_return(None)
    flexmock(proctor_utils).should_receive('get_openai_reaction').and_return(None)


def test_create_reaction(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    scope = 'incident_type'
    reaction_type = 'api'

    # Assert reaction creation with api type
    body = {
        'payload': 'curl https://www.boredapi.com/api/activity',
        'incident_type': 1
    }
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['agent_id'] == 'incident_type_api'
    assert response.json['type'] == 'api'
    assert response.json['reaction_id'] == 1

    # Assert wrong command for api reaction creation
    body = {
        'payload': 'ssh https://www.boredapi.com/api/activity',
        'incident_type': 1
    }
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    #  Assert reaction creation with ssh type
    reaction_type = 'ssh'
    body = {'payload': 'ssh yo@some.example', 'incident_type': 1}
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['agent_id'] == 'incident_type_ssh'
    assert response.json['type'] == 'ssh'
    assert response.json['reaction_id'] == 2

    #  Assert no host
    scope = 'ssh'
    body = {'payload': 'ssh yo@', 'incident_type': 1}
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    #  Assert no user
    scope = 'ssh'
    body = {'payload': 'ssh @some.example', 'incident_type': 1}
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    # Assert wrong command for ssh reaction creation
    scope = 'ssh'
    body = {'payload': 'curl @some.example', 'incident_type': 1}
    response = test_client.post(
        f'/incidents/{datasource_uuid}/create_reaction/{scope}/{reaction_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400


def test_get_reaction_scopes(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get scopes of alert.s
    response = test_client.get('/incidents/get_reactions/scopes',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['reaction_scopes']) == 1


def test_get_reaction_types(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get scopes of alert.s
    response = test_client.get('/incidents/get_reactions/types',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['reaction_types']) == 2


def test_get_reaction_triggers(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get trigger per scope of alerts.
    scope = 'data_source_type'

    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_reaction_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['reaction_triggers']) == 1

    scope = 'environment'
    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_reaction_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['reaction_triggers']) == 2

    scope = 'incident_type'
    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_reaction_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['reaction_triggers']) == 1


def test_get_reactions(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    scope = 'incident_type'
    reaction_type = 'api'
    agent_id = 'incident_type_api'
    incident_type = 1
    active = 1
    # Assert get reactions with api type
    response = test_client.get(
        f'/incidents/{datasource_uuid}/get_reactions/{scope}/{reaction_type}?incident_type={incident_type}&active={active}&agent_id={agent_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['agent_id'] == 'incident_type_api'
    assert response.json[0]['type'] == 'api'
    assert response.json[0]['reaction_id'] == 1

    reaction_type = 'ssh'
    agent_id = 'incident_type_ssh'
    # Assert get reactions with ssh type
    response = test_client.get(
        f'/incidents/{datasource_uuid}/get_reactions/{scope}/{reaction_type}?incident_type={incident_type}&active={active}&agent_id={agent_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['agent_id'] == 'incident_type_ssh'
    assert response.json[0]['type'] == 'ssh'
    assert response.json[0]['reaction_id'] == 2


def test_update_reaction(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    reaction_id = 2

    body = {'payload': 'ssh -o StrictHostKeyChecking=no yo@some.other.example'}
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/update_reaction/{reaction_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['agent_id'] == 'incident_type_ssh'
    assert response.json['type'] == 'ssh'
    assert response.json['reaction_id'] == 2


def test_execute_reaction(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    reaction_id = 1

    #  Assert execute api reaction
    response = test_client.get(
        f'/incidents/{datasource_uuid}/execute_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['response']['reaction_id'] == 1
    assert response.json['response']['message'] == 'OK'
    assert response.json['response']['id'] == 1

    #  Assert execute ssh reaction
    reaction_id = 2
    response = test_client.get(
        f'/incidents/{datasource_uuid}/execute_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['response']['reaction_id'] == 2
    assert response.json['response']['success'] is False
    assert response.json['response']['id'] == 1

    #  Assert execute non existing reacion
    reaction_id = 8
    response = test_client.get(
        f'/incidents/{datasource_uuid}/execute_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 500


def test_get_reaction_records(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    reaction_id = 1
    scope = 'incident_type'
    reaction_type = 'api'

    #  Assert get api reaction records
    response = test_client.get(
        f'/incidents/{datasource_uuid}/get_reaction_records/{scope}/{reaction_type}/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['reaction_id'] == 1
    assert response.json[0]['message'] == 'OK'

    #  Assert get ssh reaction records
    reaction_id = 2
    reaction_type = 'ssh'
    response = test_client.get(
        f'/incidents/{datasource_uuid}/get_reaction_records/{scope}/{reaction_type}/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['reaction_id'] == 2
    assert response.json[0]['success'] is False


def test_delete_api_record(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    api_record_id = 1

    #  Assert delete api reaction record by id
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_api_records/{api_record_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    api_record_id = 5
    #  Assert delete not existing api reaction record
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_api_records/{api_record_id}',
        headers={'Authorization': token})
    assert response.status_code == 404

    reaction_id = 1
    #  Create a new api reaction record
    response = test_client.get(
        f'/incidents/{datasource_uuid}/execute_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['response']['reaction_id'] == 1
    assert response.json['response']['message'] == 'OK'


def test_delete_ssh_record(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    ssh_record_id = 1
    #  Assert delete ssh reaction record by id
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_ssh_records/{ssh_record_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    ssh_record_id = 5
    #  Assert delete not existing api reaction record
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_ssh_records/{ssh_record_id}',
        headers={'Authorization': token})
    assert response.status_code == 404

    #  Create a new ssh reaction record
    reaction_id = 2
    response = test_client.get(
        f'/incidents/{datasource_uuid}/execute_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['response']['reaction_id'] == 2
    assert response.json['response']['success'] is False


def test_delete_reaction(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    reaction_id = 1
    #  Assert delete reaction by reaction id
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    reaction_id = 2
    #  Assert delete reaction by reaction id
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    reaction_id = 10
    #  Assert delete non existent reaction by reaction id
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/delete_reaction/{reaction_id}',
        headers={'Authorization': token})
    assert response.status_code == 500
