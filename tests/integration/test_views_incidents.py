# import ast
# import datetime
# import json
# import logging

# import pytest
# import requests
# from flexmock import flexmock
# from flask import Response

# from smarty import utils
# from smarty.domain.models import User
# from smarty.incidents import controller
# from smarty.proctor import utils as proctor_utils
# from tests.fixtures import integration_test_fixtures as fixtures


# def test_login(test_client):
#     flexmock(requests).should_receive('post').and_return(
#         fixtures.SKLoginResponse())
#     flexmock(requests).should_receive('get').and_return(
#         fixtures.SKUserGroups())
#     test_user = {'email': 'admin@gmail.com', 'password': 'test'}
#     response = test_client.post('/auth/login', json=test_user)
#     assert response.status_code == 200


# @pytest.fixture(autouse=True)
# def mockToken():
#     flexmock(requests).should_receive('get').and_return(
#         fixtures.SKTokenResponse())

#     flexmock(requests).should_receive('post').and_return(fixtures.SKResponseBase())

#     flexmock(proctor_utils).should_receive('get_openai_details').and_return(None)
#     flexmock(proctor_utils).should_receive('get_openai_solution').and_return(None)
#     flexmock(proctor_utils).should_receive('get_openai_reaction').and_return(None)


# def test_get_incident_type(test_client):
#     incidenttype_id = 1
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': 'dummy token'})
#     assert response.status_code == 200
#     assert b"cluster_id" in response.data
#     assert b"incidenttype_id" in response.data
#     assert b"label" in response.data
#     assert b"severity" in response.data


# def test_get_incident_types(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     response = test_client.get(f'/incidents/{datasource_uuid}/types',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert b"cluster_id" in response.data
#     assert b"incidenttype_id" in response.data
#     assert b"label" in response.data
#     assert b"logcategories" in response.data
#     assert b"severity" in response.data

#     # Assert that we can filter on cluster_id alone.
#     cluster_id = 1
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types?cluster_id={cluster_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     response_dict = ast.literal_eval(response.data.decode('utf-8'))
#     assert len(response_dict) == 2
#     for incident_type in response_dict:
#         assert incident_type["cluster_id"] == cluster_id

#     # Assert that we can filter on proctormodel_id:
#     model_id = 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types?proctormodel_id={model_id}',
#         headers={'Authorization': token})
#     print("response", response.data)
#     assert response.status_code == 200
#     response_dict = ast.literal_eval(response.data.decode('utf-8'))
#     assert len(response_dict) == 2

#     # Assert that we can filter on both proctormodel_id and cluster_id together.
#     cluster_id = 1
#     model_id = 1
#     # actually this acts more as an or, the cluster id filtering code in controller probably needs to be revisited
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types?proctormodel_id={model_id}&cluster_id={cluster_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     response_dict = ast.literal_eval(response.data.decode('utf-8'))
#     for incident_type in response_dict:
#         assert incident_type['cluster_id'] == cluster_id

#     # Assert that unknown model ID returns empty results.
#     model_id = 1234
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types?proctormodel_id={model_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert ast.literal_eval(response.data.decode('utf-8')) == []

#     # Assert that known model ID but unknown cluster ID returns empty
#     # results.
#     model_id = 987
#     cluster_id = 1234
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types?proctormodel_id={model_id}&cluster_id={cluster_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert ast.literal_eval(response.data.decode('utf-8')) == []


# def test_delete_non_existent_incident_type(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     # Some non-existent ID
#     incidenttype_id = 1234

#     response = test_client.delete(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 404


# def test_get_severities(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     response = test_client.get('/incidents/severities',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert b"severities" in response.data


# def test_get_states(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     states = test_client.get('/incidents/states',
#                              headers={'Authorization': token})
#     assert states.status_code == 200
#     assert b"states" in states.data


# def test_get_labels(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     pattern = 'Unknown'
#     labels = test_client.get(
#         f'/incidents/{datasource_uuid}/labels?pattern={pattern}',
#         headers={'Authorization': token})
#     assert labels.status_code == 200
#     json_data = json.loads(labels.data)
#     assert json_data["labels"] == ['Unknown']


# def test_get_incidents(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     response = test_client.get(f'/incidents/{datasource_uuid}',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 7

#     # Assert that we can filter incidents by type ID.
#     type_id = 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}?incidenttype_id={type_id}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 1
#     assert json_data[0]["incidenttype_id"] == 2

#     # Assert that we can filter incidents by env.
#     env = 1
#     response = test_client.get(f'/incidents/{datasource_uuid}?env={env}',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 5
#     assert json_data[0]['environment'] == env

#     # Assert that we can get the last incident.
#     response = test_client.get(f'/incidents/{datasource_uuid}?last=1',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 1

#     # Assert that filtering by unknown type ID returns empty results.
#     type_id = 1234
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}?incidenttype_id={type_id}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 0

#     # Update state of one incident.
#     incident_id = 1
#     state = 'RESOLVED'
#     payload = {'current_state': state}
#     response = test_client.patch(f'/incidents/{datasource_uuid}/{incident_id}',
#                                  json=payload,
#                                  headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     print("response", json_data)
#     assert response.status_code == 200
#     assert json_data['current_state'] == 'RESOLVED'

#     # Assert that we can filter by incident state.
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}?current_state={state}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 1
#     assert json_data[0]['current_state'] == 'RESOLVED'

#     # Assert that filtering by unknown state returns empty results.
#     state = 'potato'
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}?current_state={state}',
#         headers={'Authorization': token})
#     assert response.status_code == 400

#     # Assert that we can combine incident type and state filters.
#     state = 'DISCOVERED'
#     type_id = 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}?incidenttype_id={type_id}&current_state={state}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data[0]['current_state'] == 'DISCOVERED'
#     assert json_data[0]['incidenttype_id'] == type_id

#     # Assert that we can filter by is_open state.
#     is_open_options = [0, 1]
#     for is_open in is_open_options:
#         response = test_client.get(
#             f'/incidents/{datasource_uuid}?is_open={is_open}',
#             headers={'Authorization': token})
#         assert response.status_code == 200
#         json_data = json.loads(response.data)
#         for incident in json_data:
#             assert incident['is_open'] == is_open


# def test_update_non_existent_incident(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incident_id = 1234
#     payload = {}
#     response = test_client.patch(f'/incidents/{datasource_uuid}/{incident_id}',
#                                  json=payload,
#                                  headers={'Authorization': token})
#     assert response.status_code == 500


# def test_update_incident(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     # Then try and update it.
#     payload = {'is_read': True}
#     incident_id = 1
#     response = test_client.patch(f'/incidents/{datasource_uuid}/{incident_id}',
#                                  json=payload,
#                                  headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data['is_read'] == True

#     # Make sure the changes are persisted to the next API call.
#     get_response = test_client.get(
#         f'/incidents/{datasource_uuid}/{incident_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data['is_read'] == True

#     # Reset to False
#     payload = {'is_read': False}
#     response = test_client.patch(f'/incidents/{datasource_uuid}/{incident_id}',
#                                  json=payload,
#                                  headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data['is_read'] == False


# def test_get_incident(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incident_id = 1
#     response = test_client.get(f'/incidents/{datasource_uuid}/{incident_id}',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert b"incident_id" in response.data
#     assert b"incidenttype_id" in response.data
#     assert b"current_state" in response.data
#     assert b"occurrence_date" in response.data
#     assert b"occurrences" in response.data
#     assert b"number_solutions" in response.data


# def test_update_non_existent_incident_type(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incidenttype_id = 1234
#     payload = {}

#     response = test_client.patch(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         json=payload,
#         headers={'Authorization': token})
#     assert response.status_code == 404


# def test_delete_incident_type(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incidenttype_id = 6

#     # Delete incident type
#     response = test_client.delete(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 204

#     # Make sure trying to retrieve the incident type after deletion
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 404


# def test_delete_incident(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incident_id = 1
#     response = test_client.delete(
#         f'/incidents/{datasource_uuid}/{incident_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 204

#     # Make sure trying to retrieve the incident type after deletion
#     response = test_client.get(f'/incidents/{datasource_uuid}/{incident_id}',
#                                headers={'Authorization': token})
#     assert response.status_code == 404

#     # Making sure can't delete same incident
#     response = test_client.delete(
#         f'/incidents/{datasource_uuid}/{incident_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 404


# def test_delete_non_existent_incident(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incident_id = 1234

#     response = test_client.delete(
#         f'/incidents/{datasource_uuid}/{incident_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 404


# def test_get_incident_events(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(f'/incidents/{datasource_uuid}/events',
#                                headers={'Authorization': token})
#     print("response", response.data)
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     for event in json_data:
#         print("event", event)
#         assert 'id_field' in event
#         assert 'created_date' in event
#         assert 'field' in event

#         field_name = event['field']
#         assert field_name in event

#         id_field_name = event['id_field']
#         assert id_field_name in event

#     # Query only events of a certain field.
#     fields = ['label', 'state', 'severity']
#     for field in fields:
#         response = test_client.get(f'/incidents/{datasource_uuid}/events?field={field}',
#                                    headers={'Authorization': token})
#         assert response.status_code == 200
#         assert response.data
#         json_data = json.loads(response.data)
#         for event in json_data:
#             assert event['field'] == field

#     # Check that multiple field values are `OR`ed together as filters.
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/events?field={fields[0]}&field={fields[1]}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json
#     json_data = json.loads(response.data)
#     assert any([event['field'] == fields[0] for event in json_data])

#     # Query only events of a certain field.
#     fields = ['Unknown']
#     for field in fields:
#         response = test_client.get(
#             f'/incidents/{datasource_uuid}/events?field={field}',
#             headers={'Authorization': token})
#         assert response.status_code == 200
#         json_data = json.loads(response.data)
#         for event in json_data:
#             assert event['field'] == field

#     # Check that bogus field returns empty events list.
#     field = 'patate'
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/events?field={field}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data == []

#     def datetime_to_epoch_micros(dt):
#         return int(dt.timestamp() * 1000000)

#     now = datetime.datetime.utcnow()
#     ten_minutes = datetime.timedelta(minutes=10)

#     # Check that start_date in the past returns all events.
#     start_date = datetime_to_epoch_micros(now - ten_minutes)
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/events?start_date={start_date}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.data

#     # Check that start_date in the future returns no events.
#     start_date = datetime_to_epoch_micros(now + ten_minutes)
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/events?start_date={start_date}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data == []

#     # Garbage start date returns 400.
#     start_date = 'potato'
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/events?start_date={start_date}',
#         headers={'Authorization': token})
#     assert response.status_code == 400


# def test_sanitation(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(f'/incidents/{datasource_uuid}/sanitation',
#                                headers={'Authorization': token})
#     assert response.status_code == 200


# def test_merge_incidents(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     incident_three_id = 3
#     incident_four_id = 4
#     incident_three_label = "somethingwrong"
#     # verify current incidents
#     response = test_client.get(f'/incidents/{datasource_uuid}',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert len(json_data) == 5
#     assert json_data[1]["name"] == "test-ticket-3"
#     assert json_data[2]["name"] == "test-ticket-4"
#     assert response.status_code == 200

#     # merge incident type three into type four
#     response = test_client.patch(
#         f'/incidents/{datasource_uuid}/merge/{incident_three_id}/{incident_four_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert len(json_data) == 1
#     assert json_data[0]["name"] == "test-ticket-3"

#     # Verify incident four no longer exists
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{incident_four_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 404

#     # Verify incident three still exists
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{incident_three_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200

#     # Verify that both incident types have the same label
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incident_three_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data['label'] == incident_three_label

#     response_type_two = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incident_four_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data['label'] == incident_three_label

#     # verify only four incident left
#     response = test_client.get(f'/incidents/{datasource_uuid}',
#                                headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert len(json_data) == 4
#     assert json_data[1]["name"] == "test-ticket-3"
#     assert response.status_code == 200


# def test_label_incident_type(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incidenttype_id = 1
#     # Check and get an incident type from the database
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert 'cluster_id' in response.json
#     assert 'incidenttype_id' in response.json
#     assert 'label' in response.json
#     assert 'logcategories' in response.json
#     assert 'severity' in response.json

#     #  Change label on incident type
#     new_label = {'label': 'test label'}
#     response = test_client.patch(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         json=new_label,
#         headers={'Authorization': token})
#     assert response.status_code == 200

#     #  Check incident type was labeled
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert 'cluster_id' in response.json
#     assert 'incidenttype_id' in response.json
#     assert 'label' in response.json
#     assert 'logcategories' in response.json
#     assert 'severity' in response.json
#     assert response.json['label'] == new_label['label']

#     incidenttype_id = 2

#     new_label = {'label': 'another label'}
#     response = test_client.patch(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         json=new_label,
#         headers={'Authorization': token})
#     assert response.status_code == 200

#     #  Check incident type was labeled
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert 'cluster_id' in response.json
#     assert 'incidenttype_id' in response.json
#     assert 'label' in response.json
#     assert 'logcategories' in response.json
#     assert 'severity' in response.json
#     assert response.json['label'] == new_label['label']


# def test_get_current_labels(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     label = 'My label'

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/current_labels?pattern={label}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['labels'] == ['My label']
#     assert len(response.json['labels']) == 1


# def test_get_names(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     name = 'test-ticket-5'

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/names?pattern={name}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 1


# def test_get_labeled_incident_types(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/labeled_incidents_type',
#         json={'logcategories': [5]},
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['5']['label'] == 'My label'
#     assert len(response.json) == 1


# def test_get_type_history(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     incidenttype_id_one = 1
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     # Assert with one type history record
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_one}',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert len(response.json) == 1

#     # Assert with more than one history record
#     incidenttype_id_five = 5
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_five}',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert len(response.json) == 2

#     # Assert with limit of 1 record
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_five}?limit=1',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert len(response.json) == 1

#     # Assert with sort by
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_five}?sort_by=history_datetime',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert len(response.json) == 2

#     # Assert without type history record for an incident type
#     incidenttype_id_six = 6
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_six}',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert response.json == []


# def test_get_incidents_dashboard(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     environment = 1
#     main_state = 'open'

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 3

#     # Assert that we can filter incidents by type ID.
#     type_id = 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?incidenttype_id={type_id}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 1
#     assert json_data[0]["incidenttype_id"] == 2

#     # Assert that we can filter incidents by env.
#     env = 1
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?env={env}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 3
#     assert json_data[0]['environment'] == env

#     # Assert that we can get the last incident.
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?last=1',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 1

#     # Assert that filtering by unknown type ID returns empty results.
#     type_id = 1234
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?incidenttype_id={type_id}',
#         headers={'Authorization': token})
#     json_data = json.loads(response.data)
#     assert response.status_code == 200
#     assert len(json_data) == 0

#     # Assert that filtering by unknown state returns empty results.
#     state = 'potato'
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?current_state={state}',
#         headers={'Authorization': token})
#     assert response.status_code == 400

#     # Assert that we can combine incident type and state filters.
#     state = 'DISCOVERED'
#     type_id = 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?incidenttype_id={type_id}&current_state={state}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     json_data = json.loads(response.data)
#     assert json_data[0]['current_state'] == 'DISCOVERED'
#     assert json_data[0]['incidenttype_id'] == type_id

#     # Assert that we can filter by is_open state.
#     is_open_options = [0, 1]
#     for is_open in is_open_options:
#         response = test_client.get(
#             f'/incidents/{datasource_uuid}/{environment}/tickets/{main_state}?is_open={is_open}',
#             headers={'Authorization': token})
#         assert response.status_code == 200
#         json_data = json.loads(response.data)
#         for incident in json_data:
#             assert incident['is_open'] is True


# def test_merge_incident_type(test_client):
#     from smarty.celery import celery_incidents_tasks
#     from smarty.celery import celery_datasource_tasks

#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     incidenttype_id_two = 2
#     new_label = {'label': 'another label'}
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     proctor_response = Response(None, status=200)
#     proctor_response.headers.remove('Content-Type')

#     flexmock(celery_datasource_tasks.trigger_proctor_update)\
#         .should_receive('delay').and_return(proctor_response)

#     # Check and get a labeled incident type from the database
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id_two}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert 'cluster_id' in response.json
#     assert 'incidenttype_id' in response.json
#     assert 'label' in response.json
#     assert 'logcategories' in response.json
#     assert 'severity' in response.json
#     assert response.json['label'] == new_label['label']

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/5',
#         headers={'Authorization': token})
#     assert response.status_code == 200

#     incidenttype_id_five = 5
#     flexmock(celery_incidents_tasks.update_incident_type_proxy).should_receive(
#         'delay').replace_with(
#             controller.update_incident_type(
#                 users[0], incidenttype_id_five, new_label, datasource_uuid))

#     # Check incident type got merged by searching it
#     # which will produce an error
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id_five}',
#         headers={'Authorization': token})
#     assert response.status_code == 404

#     # check incident with type 2 is still there
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id_two}',
#         headers={'Authorization': token})
#     assert response.status_code == 200

#     # Check type history from incident type 5 was merged to type history on incident type 2
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/type_history/{incidenttype_id_two}',
#         headers={'Authorization': token})

#     assert response.status_code == 200
#     assert len(response.json) == 1


# def test_refine_incident(test_client):
#     from smarty.celery import celery_incidents_tasks

#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     # Get incident types length
#     response = test_client.get(f'incidents/{datasource_uuid}/types',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json != []
#     first_length = len(response.json)

#     # Get incidents length
#     response = test_client.get(f'incidents/{datasource_uuid}',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json != []

#     incidenttype_id = 2

#     # Check and get a labeled incident type from the database
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert 'logcategories' in response.json
#     assert response.json['logcategories'] == [2, 4, 5, 6]

#     payload = {
#         'label':
#         'this is a test',
#         'logs': [{
#             'key': 4,
#             'logcategory_id': 4,
#             'logger': 'openstack.daniel',
#             'datasource_uuid': datasource_uuid
#         }]
#     }
#     # This will take log 4 from incident type 4
#     #  and place it in a new incident type
#     flexmock(celery_incidents_tasks.refine_incident).should_receive(
#         'delay').replace_with(
#             celery_incidents_tasks.refine_incident(users[0].id,
#                                                    incidenttype_id, payload,
#                                                    datasource_uuid))
#     response = test_client.post(
#         f'incidents/{datasource_uuid}/refine_incident/{incidenttype_id}',
#         json=payload,
#         headers={'Authorization': token})
#     assert response.status_code == 403

#     # Check if a new incident type was created
#     response = test_client.get(f'incidents/{datasource_uuid}/types',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == first_length + 1

#     new_incidenttype = response.json[first_length]
#     assert new_incidenttype['label'] == payload['label']
#     assert new_incidenttype['logcategories'] == [4]
#     new_incidenttype_id = new_incidenttype['incidenttype_id']

#     # Check in log type is not in previous incident type
#     response = test_client.get(
#         f'incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['logcategories'] == [2, 5, 6]
#     assert len(response.json['logcategories']) == 3

#     # CASE WHERE IT SHOULD CREATE A NEW INCIDENT BY LOG TYPE
#     # CAUSES A CONNEXION ERROR DUE TO PROCTOR COMPONENT REQUEST
#     # # check new ticket was created by getting incident list
#     # response = test_client.get('incidents', headers={'Authorization': token})
#     # assert response.status_code == 200
#     # assert len(response.json) == incident_lenght + 1

#     # response = test_client.get(
#     #     f'incidents/{incident_lenght}', headers={'Authorization': token})
#     # assert response.status_code == 200
#     # assert response.json['incidenttype_id'] == new_incidenttype_id
#     # assert response.json['current_label'] == payload['label']

#     # Check refinement by merging
#     incidenttype_id = 1
#     payload = {
#         'label': 'this is a test',
#         'logs': [{
#             'key': 5,
#             'logcategory_id': 5,
#             'logger': 'openstack.mesh'
#         }]
#     }
#     flexmock(celery_incidents_tasks.refine_incident).should_receive(
#         'delay').replace_with(
#             celery_incidents_tasks.refine_incident(users[0].id,
#                                                    incidenttype_id, payload,
#                                                    datasource_uuid))
#     # Incident type one has 2 log types and I will merge 1 to new incident
#     # created just a above, the new incident type should have 2 log types
#     response = test_client.post(
#         f'/incidents/{datasource_uuid}/refine_incident/{incidenttype_id}',
#         json=payload,
#         headers={'Authorization': token})
#     assert response.status_code == 403
#     # Check parent/previous incident type lost a log type
#     response = test_client.get(
#         f'incidents/{datasource_uuid}/types/{incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['incidenttype_id'] == 1
#     assert response.json['logcategories'] == [1]
#     assert len(response.json['logcategories']) == 1

#     # Check new incident type with 2 log types
#     response = test_client.get(
#         f'incidents/{datasource_uuid}/types/{new_incidenttype_id}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['incidenttype_id'] == new_incidenttype_id
#     assert response.json['label'] == payload['label']
#     assert len(response.json['logcategories']) == 2
#     assert response.json['logcategories'] == [4, 5]


# def test_get_incident_info(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     incidenttype_id = 1
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     environment = 1

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment}/info',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 3

#     environment_zero = 0
#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/{environment_zero}/info',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 3


# def test_get_user_states(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)

#     response = test_client.get('/incidents/user_states/elastic',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert len(response.json) == 2

#     open_states = response.json['open']
#     closed_states = response.json['close']

#     assert len(open_states) == 6
#     assert len(closed_states) == 3


# def test_get_utc_time(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)

#     response = test_client.get('/incidents/utc',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json is not None


# def test_get_loggers(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(f'/incidents/{datasource_uuid}/loggers',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json is not None
#     assert response.json['loggers'] != 0


# def test_get_hosts(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.get(f'/incidents/{datasource_uuid}/hosts',
#                                headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json is not None
#     assert response.json['hosts'] != 0


# def test_set_incident_is_read(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     incident_id = 2
#     response = test_client.patch(
#         f'/incidents/{datasource_uuid}/{incident_id}/is_read',
#         json={'is_read': 1},
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json is not None
#     assert response.json['is_read'] is True


# def test_get_filters_templates(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     env = 1

#     response = test_client.get(
#         f'/incidents/{datasource_uuid}/filters_template?env={env}',
#         headers={'Authorization': token})
#     assert response.status_code == 200
#     assert response.json['host']['label'] == 'Host'
#     assert response.json['logger']['label'] == 'Logger'


# # # TESTS BELOW ARE TESTS FOR OBJECT STORAGE FILE UPLOAD TODO AND CODE SEEMS BROKEN AS WELL NOT JUST TESTS

# # # def test_get_incident_solution_saio(testapp):
# # #     # Get auth token
# # #     authentication = authenticate_saio().json()
# # #     token = authentication["X-Auth-Token"]
# # #     storage_url = authentication["X-Storage-Url"]
# # #
# # #     # Create Object Storage
# # #     create_object_storage_saio(token, storage_url, '1')
# # #
# # #     # Assert empty response
# # #     objects = list_files_saio(token, storage_url, '1')
# # #     assert objects == []
# # #
# # #     # Create file and upload
# # #     from werkzeug.test import EnvironBuilder
# # #     from io import BytesIO
# # #     builder = EnvironBuilder(
# # #         method='POST',
# # #         data={
# # #             'foo': 'this is some text',
# # #             'file': (BytesIO(b'my file contents'), 'test.txt')
# # #         })
# # #     env = builder.get_environ()
# # #     from werkzeug.wrappers import Request
# # #     request = Request(env)
# # #     file = request.files['file']
# # #     add_file_saio(token, storage_url, '1', file)
# # #
# # #     # Create user for auth purposes
# # #     test_user = {'email': 'cerebro-test@test.com', 'password': 'testtest'}
# # #     response = testapp.post_json('/auth/register', test_user)
# # #
# # #     # Login
# # #     response = testapp.post_json('/auth/login', test_user)
# # #     auth_token = response.json['authentication_token']
# # #
# # #     incident_solution = testapp.get(
# # #         f'/incidents/solutions/1', headers={'Authorization': auth_token})
# # #     assert incident_solution.status_int == 200
# # #
# # #     # Get the file
# # #     objects = list_files_saio(token, storage_url, '1')
# # #     assert 'test.txt' in objects[0]['name']
# # #
# # #     # Delete file and container
# # #     delete_file_saio(token, storage_url, '1', 'test.txt')
# # #     delete_container_saio(token, storage_url, '1')
# # #
# # #
# # # def test_add_file_saio(testapp):
# # #     # Create user for auth purposes
# # #     test_user = {'email': 'cerebro-test@test.com', 'password': 'testtest'}
# # #     response = testapp.post_json('/auth/register', test_user)
# # #
# # #     # Login
# # #     response = testapp.post_json('/auth/login', test_user)
# # #     auth_token = response.json['authentication_token']
# # #
# # #     # Assert add file request without file
# # #     incident_solution = testapp.post_json(
# # #         '/incidents/solutions',
# # #         headers={'Authorization': auth_token},
# # #         status=400)
# # #     assert incident_solution.status_int == 400
# # #
# # #
# # # def test_delete_file_saio(testapp):
# # #     # Get auth token
# # #     authentication = authenticate_saio().json()
# # #     token = authentication["X-Auth-Token"]
# # #     storage_url = authentication["X-Storage-Url"]
# # #
# # #     # Create Object Storage
# # #     create_object_storage_saio(token, storage_url, '1')
# # #
# # #     # Create file and upload
# # #     from werkzeug.test import EnvironBuilder
# # #     from io import BytesIO
# # #     builder = EnvironBuilder(
# # #         method='POST',
# # #         data={
# # #             'foo': 'this is some text',
# # #             'file': (BytesIO(b'my file contents'), 'test.txt')
# # #         })
# # #     env = builder.get_environ()
# # #     from werkzeug.wrappers import Request
# # #     request = Request(env)
# # #     file = request.files['file']
# # #     add_file_saio(token, storage_url, '1', file)
# # #
# # #     # Get the file
# # #     objects = list_files_saio(token, storage_url, '1')
# # #     assert 'test.txt' in objects[0]['name']
# # #
# # #     # Create user for auth purposes
# # #     test_user = {'email': 'cerebro-test@test.com', 'password': 'testtest'}
# # #     response = testapp.post_json('/auth/register', test_user)
# # #
# # #     # Login
# # #     response = testapp.post_json('/auth/login', test_user)
# # #     auth_token = response.json['authentication_token']
# # #
# # #     # Create a model.
# # #     model_data = {'data': 'some_data'}
# # #     model = testapp.post_json('/proctor/models', model_data).json
# # #
# # #     # Create an incident type.
# # #     incident_type_data = {
# # #         'proctormodel_id': model['proctormodel_id'],
# # #         'cluster_id': 1,
# # #         'input_df': 'some_list',
# # #         'label_prediction': 'another_list',
# # #     }
# # #     incident_type_1 = testapp.post_json(
# # #         '/incidents/types',
# # #         incident_type_data,
# # #         headers={
# # #             'Authorization': auth_token
# # #         }).json
# # #
# # #     # Delete file --> test.txt
# # #     incident_solution = testapp.delete(
# # #         '/incidents/solutions/1/test.txt',
# # #         headers={'Authorization': auth_token})
# # #     assert incident_solution.status_int == 200
# # #     assert 'test.txt' not in incident_solution
# # #
# # #     # Delete container
# # #     delete_container_saio(token, storage_url, '1')
# # #
# # #
# # # def test_delete_container_saio(testapp):
# # #     # Get auth token
# # #     authentication = authenticate_saio().json()
# # #     token = authentication["X-Auth-Token"]
# # #     storage_url = authentication["X-Storage-Url"]
# # #
# # #     # Create Object Storage
# # #     create_object_storage_saio(token, storage_url, '1')
# # #
# # #     objects = list_object_storage_saio(token, storage_url)
# # #     assert '1' not in objects
# # #
# # #     # Create user for auth purposes
# # #     test_user = {'email': 'cerebro-test@test.com', 'password': 'testtest'}
# # #     response = testapp.post_json('/auth/register', test_user)
# # #
# # #     # Login
# # #     response = testapp.post_json('/auth/login', test_user)
# # #     auth_token = response.json['authentication_token']
# # #
# # #     # Delete file --> test.txt
# # #     incident_solution = testapp.delete(
# # #         '/incidents/solutions/1', headers={'Authorization': auth_token})
# # #     assert incident_solution.status_int == 200
# # #     assert '1' not in incident_solution
# # #
# # #     # Delete container
# # #     delete_container_saio(token, storage_url, '1')
