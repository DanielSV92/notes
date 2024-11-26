import datetime
import json

import pytest
import requests
from flexmock import flexmock

from smarty.domain.models import User
from tests.fixtures import integration_test_fixtures as fixtures


@pytest.fixture(autouse=True)
def mockToken():
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())


    flexmock(requests).should_receive('post').and_return(
        fixtures.SlackWebhookResponse())


def test_create_slack_entry(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {'code': 'test_code', 'redirect_uri': 'some.awesome.url'}

    # Assert create slack entry
    response = test_client.post('/incidents/slack',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['channel'] == '#test_slack_path'
    assert response.json['slack_id'] == 2

    # Assert create wrong slack entry
    response = test_client.post('/incidents/slack',
                                json={},
                                headers={'Authorization': token})
    assert response.status_code == 400


def test_get_slack_entries(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    # Assert get slack entries
    response = test_client.get('/incidents/slack',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[1]['channel'] == '#test_slack_path'
    assert response.json[1]['slack_id'] == 2


def test_get_slack_entry(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    slack_id = 2

    # Assert get slack entry
    response = test_client.get(f'/incidents/slack/{slack_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['channel'] == '#test_slack_path'
    assert response.json['slack_id'] == 2

    slack_id = 5
    # Assert get slack entry
    response = test_client.get(f'/incidents/slack/{slack_id}',
                               headers={'Authorization': token})
    assert response.status_code == 500


def test_delete_slack_entry(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    slack_id = 2

    # Assert get slack entry
    response = test_client.delete(f'/incidents/slack/{slack_id}',
                                  headers={'Authorization': token})
    assert response.status_code == 204

    slack_id = 5
    # Assert get slack entry
    response = test_client.delete(f'/incidents/slack/{slack_id}',
                                  headers={'Authorization': token})
    assert response.status_code == 500
