# import json
# import uuid
# from os import path

# import flask
# import pytest
# import requests
# from flask import Response
# from flexmock import flexmock

# from smarty.domain.models import User
# from tests.fixtures import integration_test_fixtures as fixtures


# @pytest.fixture(autouse=True)
# def mockToken():
#     flexmock(requests).should_receive('get').and_return(
#         fixtures.SKTokenResponse())

#     # proctor_response = Response(None, status=500)
#     # proctor_response.headers.remove('Content-Type')

#     # flexmock(requests).should_receive('post').and_return(
#     #     proctor_response)


# def test_create_agent(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.post(f'/agent/{ds_uuid}/{env_id}/create_agent',
#                                 json=body,
#                                 headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['agent_name'] == body['agent_name']

#     ds_uuid = "somerandomtext"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.post(f'/agent/{ds_uuid}/{env_id}/create_agent',
#                                 json=body,
#                                 headers={'Authorization': token})
#     assert response.status_code == 400

#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 20
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.post(f'/agent/{ds_uuid}/{env_id}/create_agent',
#                                 json=body,
#                                 headers={'Authorization': token})
#     assert response.status_code == 400

#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.post(f'/agent/{ds_uuid}/{env_id}/create_agent',
#                                 json=body,
#                                 headers={'Authorization': token})
#     assert response.status_code == 400


# def test_update_agent(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent_update'}
#     response = test_client.patch(f'/agent/{ds_uuid}/{env_id}/update_agent',
#                                  json=body,
#                                  headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['agent_name'] == body['agent_name']

#     ds_uuid = "somerandomtext"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.patch(f'/agent/{ds_uuid}/{env_id}/update_agent',
#                                  json=body,
#                                  headers={'Authorization': token})
#     assert response.status_code == 400

#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 20
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.patch(f'/agent/{ds_uuid}/{env_id}/update_agent',
#                                  json=body,
#                                  headers={'Authorization': token})
#     assert response.status_code == 400

#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 2
#     body = {'agent_name': 'my_test_agent'}
#     response = test_client.patch(f'/agent/{ds_uuid}/{env_id}/update_agent',
#                                  json=body,
#                                  headers={'Authorization': token})
#     assert response.status_code == 404


# def test_get_agent(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 1
#     body = {'agent_name': 'my_test_agent_update'}
#     response = test_client.get(f'/agent/{ds_uuid}/{env_id}/get_agent',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['agent_name'] == body['agent_name']

#     ds_uuid = "somerandomtext"
#     env_id = 1

#     response = test_client.get(f'/agent/{ds_uuid}/{env_id}/get_agent',
#                                headers={'Authorization': token})
#     assert response.status_code == 400

#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env_id = 20

#     response = test_client.get(f'/agent/{ds_uuid}/{env_id}/get_agent',
#                                headers={'Authorization': token})
#     assert response.status_code == 400


# def test_get_all_agents(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(f'/agent/{ds_uuid}/get_agents',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 1

#     ds_uuid = "somerandomtext"

#     response = test_client.get(f'/agent/{ds_uuid}/get_agents',
#                                headers={'Authorization': token})
#     assert response.status_code == 400
