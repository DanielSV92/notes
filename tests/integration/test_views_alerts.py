import pytest
import requests
from flexmock import flexmock

from smarty.alerts import controller
from smarty.domain.models import Incident
from smarty.domain.models import IncidentType
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


def test_get_alert_types(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get types of alerts.
    response = test_client.get('/incidents/get_alerts/types',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['alert_types']) == 2


def test_get_alert_scopes(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get scopes of alert.s
    response = test_client.get('/incidents/get_alerts/scopes',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['alert_scopes']) == 7


def test_get_alert_triggers(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get trigger per scope of alerts.
    scope = 'data_source_type'

    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_alert_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['alert_triggers']) == 1

    scope = 'environment'
    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_alert_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['alert_triggers']) == 5

    scope = 'incident_type'
    # Assert for data source type scope
    response = test_client.get(f'/incidents/get_alert_triggers/{scope}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['alert_triggers']) == 1


def test_create_alert(test_client):
    flexmock(controller).should_receive('validate_email').and_return(True)
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    alert_type = 'email'
    scope = 'incident_type'
    body = {
        'incident_type': 1,
        'payload': ['test@ormuco.com'],
        'triggers': ['new_incident_with_incident_type']
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['incident_type'] == 1
    assert response.json['type'] == 'email'
    assert response.json['scope'] == 'incident_type'

    #  Assert duplicate alert with incident type
    scope = 'incident_type'
    body = {
        'incident_type': 1,
        'payload': ['test@ormuco.com'],
        'triggers': ['new_incident_with_incident_type']
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 403

    #  Assert with incident type 0
    scope = 'incident_type'
    body = {
        'incident_type': 0,
        'payload': ['test@ormuco.com'],
        'triggers': ['new_incident_with_incident_type']
    }

    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    #  Assert with not existing incident type
    scope = 'incident_type'
    body = {
        'incident_type': 40,
        'payload': ['test@ormuco.com'],
        'triggers': ['new_incident_with_incident_type']
    }

    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    scope = 'data_source_type'
    body = {'payload': ['test@ormuco.com'], 'triggers': ['new_incident_type']}

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'email'
    assert response.json['scope'] == 'data_source_type'

    scope = 'environment'
    body = {
        'environment': [1],
        'payload': ['test@ormuco.com'],
        'triggers': ['incident_reopened']
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'email'
    assert response.json['scope'] == 'environment'

    #  Assert update existing environment alert when creating a similar alert
    scope = 'environment'
    body = {
        'environment': [1, 2],
        'payload': ['test@ormuco.com'],
        'triggers': ['incident_reopened', 'new_incident']
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'email'
    assert response.json['scope'] == 'environment'

    #  Assert duplicate alert with environment
    scope = 'environment'
    body = {
        'environment': [1],
        'payload': ['test@ormuco.com'],
        'triggers': ['incident_reopened']
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 403

    #  Assert alert creation with slack alertt type
    alert_type = 'slack'
    scope = 'incident_type'
    body = {
        'incident_type': 1,
        'payload': [{
            'slack_id': 1
        }],
        'triggers': ['new_incident_with_incident_type'],
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['incident_type'] == 1
    assert response.json['type'] == 'slack'
    assert response.json['scope'] == 'incident_type'

    scope = 'data_source_type'
    body = {
        'payload': [{
            'slack_id': 1
        }],
        'triggers': ['new_incident_type'],
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'slack'
    assert response.json['scope'] == 'data_source_type'

    scope = 'environment'
    body = {
        'environment': [1],
        'payload': [{
            'slack_id': 1
        }],
        'triggers': ['incident_reopened'],
    }

    # Assert create alert with incident_type scope
    response = test_client.post(
        f'/incidents/{ds_uuid}/create_alert/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'slack'
    assert response.json['scope'] == 'environment'
    assert response.json['payload']['channel'] == '#dev-cerebro-alerts'


def test_get_alerts(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    alert_type = 'email'
    scope = 'incident_type'
    body = {'incident_type': 1}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['incident_type'] == 1
    assert response.json[0]['type'] == 'email'
    assert response.json[0]['scope'] == 'incident_type'

    scope = 'data_source_type'
    body = {}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'email'
    assert response.json[0]['scope'] == 'data_source_type'

    scope = 'environment'
    body = {'environment': [1]}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'email'
    assert response.json[0]['scope'] == 'environment'

    scope = 'environment'
    body = {'environment': 'all'}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'email'
    assert response.json[0]['scope'] == 'environment'

    #  Assert alert creation with slack alertt type
    alert_type = 'slack'
    scope = 'incident_type'
    body = {'incident_type': 1}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['incident_type'] == 1
    assert response.json[0]['type'] == 'slack'
    assert response.json[0]['scope'] == 'incident_type'

    scope = 'data_source_type'
    body = {}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'slack'
    assert response.json[0]['scope'] == 'data_source_type'

    scope = 'environment'
    body = {'environment': [1]}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'slack'
    assert response.json[0]['scope'] == 'environment'

    scope = 'environment'
    body = {'environment': 'all'}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['active'] is True
    assert response.json[0]['type'] == 'slack'
    assert response.json[0]['scope'] == 'environment'
    assert response.json[0]['payload']['channel'] == '#dev-cerebro-alerts'


def test_create_alert_history(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    trigger = 'incident_reopened'

    alert_type = 'email'
    scope = 'incident_type'
    body = {'incident_type': 1}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    alert = response.json[0]
    incident_id = 1
    incident = Incident.query.get(incident_id)
    incidenttype_id = 1
    body = {'source': incident, 'trigger': trigger, 'scope': 'incident'}
    alert_history_1 = controller.create_alert_history(ds_uuid, alert, body)
    assert alert_history_1['history_id'] == 1
    assert alert_history_1['payload']['email'] == 'test@ormuco.com'

    trigger = 'new_incident'
    body = {'source': incident, 'trigger': trigger}
    alert_history_2 = controller.create_alert_history(ds_uuid, alert, body)
    assert alert_history_2['history_id'] == 2

    trigger = 'new_ticket_with_incident_type'
    body = {'source': incident, 'trigger': trigger}
    alert_history_3 = controller.create_alert_history(ds_uuid, alert, body)
    assert alert_history_3['history_id'] == 3

    incident_type = IncidentType.query.get(incidenttype_id)
    trigger = 'new_incident_type'
    body = {'source': incident_type, 'trigger': trigger}
    alert_history_4 = controller.create_alert_history(ds_uuid, alert, body)
    assert alert_history_4['history_id'] == 4

    alert_type = 'slack'
    scope = 'environment'
    body = {'environment': 'all'}

    # Assert get alert with incident_type scope
    response = test_client.get(
        f'/incidents/{ds_uuid}/get_alerts/{scope}/{alert_type}',
        json=body,
        headers={'Authorization': token})

    alert_two = response.json[0]
    trigger = 'new_ticket_with_incident_type'
    body = {'source': incident, 'trigger': trigger}
    alert_history_1 = controller.create_alert_history(ds_uuid, alert_two, body)
    assert alert_history_1['history_id'] == 5
    assert alert_history_1['payload']['slack'][
        'channel'] == '#dev-cerebro-alerts'


def test_update_alert(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    body = {
        'environment': [1, 2],
        'payload': ['anothertest@ormuco.com'],
        'triggers': [{
            "type": "incident_reopened",
            "description": "A ticket is re-open"
        }, {
            "type": "new_incident",
            "description": "New ticket is open"
        }]
    }
    alert_id = 4

    # Assert update alert by alert id
    response = test_client.patch(
        f'/incidents/{ds_uuid}/update_alert/{alert_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['active'] is True
    assert response.json['type'] == 'slack'
    assert response.json['scope'] == 'incident_type'


def test_get_alert_history(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    alert_id = 1

    response = test_client.get(
        f'incidents/{ds_uuid}/get_alert/{alert_id}/history?scope=incident_type',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 4
    assert response.json[0]['email_sent_to'] == 'test@ormuco.com'

    trigger = 'new_incident'
    response = test_client.get(
        f'incidents/{ds_uuid}/get_alert/{alert_id}/history?alert_trigger={trigger}&scope=incident_type',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    response = test_client.get(
        f'incidents/{ds_uuid}/get_alert/{alert_id}/history?limit=1&offset=0&scope=incident_type',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    sort_by = 'history_datetime'
    response = test_client.get(
        f'incidents/{ds_uuid}/get_alert/{alert_id}/history?sort_by={sort_by}&scope=incident_type',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 4


def test_delete_alert(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    body = {}
    alert_id = 1

    # Assert update alert by alert id
    response = test_client.delete(
        f'/incidents/{ds_uuid}/delete_alert/{alert_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 204

    alert_id = 4

    # Assert update alert by alert id
    response = test_client.delete(
        f'/incidents/{ds_uuid}/delete_alert/{alert_id}',
        json=body,
        headers={'Authorization': token},
    )
    assert response.status_code == 204
