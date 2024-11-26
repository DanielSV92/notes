import datetime
import json

import pytest
import requests
from flask import Response
from flexmock import flexmock

from smarty.domain.models import IncidentEvent
from smarty.domain.models import User
from smarty.proctor import utils as proctor_utils
from tests.fixtures import integration_test_fixtures as fixtures


@pytest.fixture(autouse=True)
def mockToken():
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())

    flexmock(requests).should_receive('post').and_return(fixtures.ProctorResponse())

    flexmock(proctor_utils).should_receive('get_openai_details').and_return(None)
    flexmock(proctor_utils).should_receive('get_openai_solution').and_return(None)
    flexmock(proctor_utils).should_receive('get_openai_reaction').and_return(None)


def test_create_proctor_model(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Create test model.
    test_model = {'data': 'some_data'}
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(f'/proctor/{ds_uuid}/models',
                                json=test_model,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'proctormodel_id' in response.json
    assert 'data' not in response.json


def test_get_proctor_model(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    # Create a test model.
    test_model = {'data': 'some_data', 'datasource_uuid': ds_uuid}

    response = test_client.post(f'/proctor/{ds_uuid}/models',
                                json=test_model,
                                headers={'Authorization': token})
    model_id = response.json['proctormodel_id']
    datasource_uuid = response.json['datasource_uuid']
    assert model_id == 6
    assert datasource_uuid == ds_uuid

    # Retrieve the newly created model.
    response = test_client.get(f'/proctor/{ds_uuid}/models/{model_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['data'] == test_model['data']


def test_get_non_existent_proctor_model(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    model_id = 1234
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    response = test_client.get(f'/proctor/{ds_uuid}/models/{model_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == {}


def test_create_training_datum(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    raw_logs = [{
        'Hostname': 'controller003',
        'Logger': 'openstack.nova',
        'Pid': '7',
        'programname': 'nova-compute',
        'Payload': 'This is the payload is looking for',
        '@timestamp': '2019-10-03T12:20:47.112000000+00:00',
        'log_level': 'ERROR',
        'logcategory_id': 2,
        'environment': 1,
        'tid': 'error',
    }]

    # Create training data.
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 2,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'proctortrainingdata_id' in response.json
    assert 'proctormodel_id' not in response.json
    assert 'cluster_id' not in response.json
    assert 'open_incident' in response.json
    assert 'predicted_label' in response.json
    assert 'end_date' in response.json
    assert 'incident_id' in response.json
    # BLOBs
    assert 'data' not in response.json
    assert 'input_df' not in response.json
    assert 'label_prediction' not in response.json

    # Assert that an incident type and an incident were created.
    incident_id = response.json['incident_id']
    response = test_client.get(f'/incidents/{datasource_uuid}/{incident_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200

    type_id = response.json['incidenttype_id']
    response = test_client.get(f'/incidents/{datasource_uuid}/types/{type_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200

    # Create a new training datum with the same model/cluster IDs, and
    # assert that we re-use the same open incident and previously
    # created incident type.
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 2,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200

    # Resolve the existing incident.
    payload = {'current_state': 'RESOLVED'}
    response = test_client.patch(f'/incidents/{datasource_uuid}/{incident_id}',
                                 json=payload,
                                 headers={'Authorization': token})
    assert response.status_code == 200

    # Create a new training datum with the same model/cluster IDs, and
    # assert that we re-use the previously created incident type, but
    # create a new incident given that the old one was closed.
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 2,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incident_id'] != incident_id

    response = test_client.get(f'/incidents/{datasource_uuid}/{incident_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidenttype_id'] == type_id

    # Create a new training datum with the same two known types, and
    # assert that only one incident gets created
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 6,
        'predicted_label': 'neutron',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 8,
        'predicted_label': 'neutron',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200

    # make sure only one incident was created and two incident types were created
    # for that label
    response = test_client.get(
        f'/incidents/{datasource_uuid}?current_label=neutron',
        headers={'Authorization': token})
    assert response.status_code == 200

    response = test_client.get(
        f'/incidents/{datasource_uuid}/types?label=neutron',
        headers={'Authorization': token})
    assert response.status_code == 200
    type_first_model = 0
    type_second_model = 0
    for type in response.json:
        if (type['proctormodel_id'] == 1):
            type_first_model = type_first_model + 1
        if (type['proctormodel_id'] == 2):
            type_second_model = type_second_model + 1
    if (type_first_model):
        assert type_first_model == 2
    if (type_second_model):
        assert type_second_model == 2

    # Create a new training datum with unknown label and same cluster/model id
    # , and assert that no new incident gets created, occurrences increase
    test_datum = {
        'data': json.dumps(raw_logs),
        'proctormodel_id': 1,
        'cluster_id': 5,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1570105247112,
        'occurrence_date': 1570105247112,
        'incident_name': 'incident_name',
        'env': 1,
        'data_source': 'smarty',
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200
    incident_id = response.json['incident_id']
    response = test_client.get(f'/incidents/{datasource_uuid}/{incident_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['occurrences'] == 4
    response = test_client.get(
        f'/incidents/{datasource_uuid}?current_label=Unknown',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_get_training_data(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    # Create test model.
    test_model = {'data': 'some_data'}
    response = test_client.post(f'/proctor/{datasource_uuid}/models',
                                json=test_model,
                                headers={'Authorization': token})
    proctormodel_id_1 = response.json['proctormodel_id']

    logs = [{
        'Hostname': 'controller003',
        'Logger': 'openstack.nova',
        'Pid': '7',
        'programname': 'nova-compute',
        'Payload': 'This is the payload is looking for',
        '@timestamp': '2019-10-18T12:20:47.112000000+00:00',
        'log_level': 'ERROR',
        'logcategory_id': 1,
        'environment': 1,
        'tid': 'error',
    }]

    # Create a new training data entry.
    test_datum = {
        'data': json.dumps(logs),
        'proctormodel_id': 1,
        'cluster_id': 4,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([1]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1571401247112,
        'occurrence_date': 1571401247112,
        'incident_name': 'incident_name',
        'env': 1,
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }

    # Assert that all created training data entries are listed.
    response = test_client.get(f'/proctor/{datasource_uuid}/training_data',
                               headers={'Authorization': token})
    assert len(response.json) != []
    first_lenght = len(response.json)

    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200

    # Assert that all created training data entries are listed.
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?proctormodel_id={proctormodel_id_1}',
        headers={'Authorization': token})

    # Assert that listed training data have IDs and such but no binary
    # data in their payload.
    for response_datum in response.json:
        assert 'proctortrainingdata_id' in response_datum
        assert 'predicted_label' in response_datum
        assert 'end_date' in response_datum
        assert 'incident_id' in response_datum
        assert 'open_incident' in response_datum
        # BLOBs
        assert 'data' not in response_datum
        assert 'input_df' not in response_datum
        assert 'label_prediction' not in response_datum

    # Assert that all created training data entries are listed
    # with expand=true.
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?expand={True}',
        headers={'Authorization': token})
    assert len(response.json) == first_lenght + 1
    second_lenght = len(response.json)

    # Assert that listed training data have IDs and such but no binary
    # data in their payload.
    for response_datum in response.json:
        assert 'proctortrainingdata_id' in response_datum
        assert 'predicted_label' in response_datum
        assert 'end_date' in response_datum
        assert 'incident_id' in response_datum
        # BLOBs
        assert 'data' in response_datum
        assert 'input_df' in response_datum

    #  use compress = 1 to get factor > 1
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?compress=1&expand={True}',
        headers={'Authorization': token})
    assert len(response.json) == first_lenght + 1

    #  Asser the list of training data has valid elements
    for response_datum in response.json:
        assert response_datum is not None
    # Test queries by time range.

    # Start date before all end dates should return all models.
    start_date = 1287145247112
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?start_date={start_date}',
        headers={'Authorization': token})
    assert len(response.json) == second_lenght

    # Start date after all end dates should return nothing.
    start_date = 2233916447112
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?start_date={start_date}',
        headers={'Authorization': token})
    assert response.json == []

    # End date after all end_dates should return all models.
    end_date = 2233916447112
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?end_date={end_date}',
        headers={'Authorization': token})
    assert len(response.json) == second_lenght

    # End date before all end_dates should return nothing
    end_date = 1287145247112
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?end_date={end_date}',
        headers={'Authorization': token})
    assert response.json == []

    # Retrieve a single model with a narrow time range.
    start_date = 1571314847112
    end_date = 1571487647112
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?start_date={start_date}&end_date={end_date}',
        headers={'Authorization': token})
    assert len(response.json) == 1

    # Inverting start and end dates returns nothing.
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?start_date={end_date}&end_date={start_date}',
        headers={'Authorization': token})
    assert response.json == []

    # Garbage start date returns 400.
    start_date = 'potato'
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?start_date={start_date}',
        headers={'Authorization': token})
    assert response.status_code == 500

    # Garbage end date returns 00.
    end_date = 'tomato'
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?end_date={end_date}',
        headers={'Authorization': token})
    assert response.status_code == 500

    # test limit and offset - ok
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?offset=0&limit=2',
        headers={'Authorization': token})
    assert len(response.json) == 2

    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?last=1&expand=true',
        headers={'Authorization': token})

    for response_datum in response.json:
        assert 'data' in response_datum
        assert 'end_date' in response_datum
        assert 'incident_id' in response_datum
        assert 'input_df' in response_datum
        assert 'label_prediction' in response_datum
        assert 'predicted_label' in response_datum
        assert 'proctortrainingdata_id' in response_datum

    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?last=1',
        headers={'Authorization': token})

    for response_datum in response.json:
        assert 'data' not in response_datum
        assert 'end_date' in response_datum
        assert 'incident_id' in response_datum
        assert 'input_df' not in response_datum
        assert 'label_prediction' not in response_datum
        assert 'predicted_label' in response_datum
        assert 'proctormodel_id' not in response_datum
        assert 'proctortrainingdata_id' in response_datum

    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?last=1&sequence=1&expand=true',
        headers={'Authorization': token})

    for response_datum in response.json:
        assert 'end_date' in response_datum
        assert 'env' in response_datum
        assert 'incident_id' in response_datum
        assert 'input_df' in response_datum
        assert 'label_prediction' in response_datum
        assert 'predicted_label' in response_datum
        assert 'proctortrainingdata_id' in response_datum

    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data?last=1&sequence=1',
        headers={'Authorization': token})

    for response_datum in response.json:
        assert 'env' in response_datum
        assert 'incident_id' in response_datum
        assert 'input_df' in response_datum
        assert 'proctortrainingdata_id' in response_datum

    # get_category_occurrences to known incident_id
    incident_id = response.json[0].get('incident_id')
    response = test_client.get(
        f'/proctor/{datasource_uuid}/category_occurrences?incident_id={incident_id}',
        headers={'Authorization': token})
    assert response.status_code == 200

    # get_category_occurrences to known incident_id and most_recent
    response = test_client.get(
        f'/proctor/{datasource_uuid}/category_occurrences?incident_id={incident_id}&most_recent=0',
        headers={'Authorization': token})
    assert response.status_code == 200

    # get_category_occurrences to known incident_id and aggregate
    response = test_client.get(
        f'/proctor/{datasource_uuid}/category_occurrences?incident_id={incident_id}&aggregate=0',
        headers={'Authorization': token})
    assert response.status_code == 200

    # get_category_occurrences to unknown incident_id --> 123
    incident_id = 123
    response = test_client.get(
        f'/proctor/{datasource_uuid}/category_occurrences?incident_id={incident_id}',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_get_training_datum(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    trainingdata_id = 2
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    logs = [{
        'Hostname': 'controller003',
        'Logger': 'openstack.nova',
        'Pid': '7',
        'programname': 'nova-compute',
        'Payload': 'This is the payload is looking for',
        '@timestamp': '2019-10-15T12:20:47.112000000+00:00',
        'log_level': 'ERROR',
        'logcategory_id': 3,
        'environment': 1,
        'tid': 'error',
    }]

    test_datum = {
        'data': json.dumps(logs),
        'proctormodel_id': 5,
        'cluster_id': 8,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([3]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1571142047112,
        'occurrence_date': 1571142047112,
        'incident_name': 'incident_name',
        'env': 1,
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['predicted_label'] == test_datum['predicted_label']

    trainingdata_id = response.json['proctortrainingdata_id']
    # Retrieve the new created entry.
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert 'proctortrainingdata_id' in response.json
    assert 'predicted_label' in response.json
    assert 'end_date' in response.json
    assert 'incident_id' in response.json
    # BLOBs
    assert 'data' in response.json
    assert 'input_df' in response.json
    assert 'label_prediction' in response.json

    # Retrieve the sequence of the newly created entry
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}?sequence=1',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert 'proctortrainingdata_id' in response.json
    assert 'proctormodel_id' not in response.json
    assert 'cluster_id' not in response.json
    assert 'predicted_label' not in response.json
    assert 'end_date' not in response.json
    assert 'env' in response.json
    assert 'incident_id' in response.json
    # BLOBs
    assert 'data' not in response.json
    assert 'input_df' in response.json
    assert 'label_prediction' not in response.json


def test_get_non_existent_training_datum(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    trainingdata_id = 1234

    response = test_client.get(f'/proctor/training_data/{trainingdata_id}',
                               headers={'Authorization': token})
    assert response.status_code == 500


def test_log_categories(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    test_categories = [{
        'logcategory_id': 1,
        'log_archetype': "No compute node record for host",
        'logger': "openstack.nova",
        'signature': {
            'count': 4,
            'position_offset': 1
        }
    }, {
        'logcategory_id': 2,
        'log_archetype': "this is a test",
        'logger': "logger",
        'signature': {
            'count': 2,
            'position_offset': 2
        }
    }, {
        'logcategory_id': 3,
        'log_archetype': "this is probably not a test",
        'logger': "logger",
        'signature': {
            'count': 3,
            'position_offset': 4
        }
    }]

    # test get all
    response = test_client.get(f'/proctor/{datasource_uuid}/log_category',
                               headers={'Authorization': token})
    assert len(response.json) == len(test_categories) + 4
    first_lenght = len(response.json)

    # switch to proctor user
    proctor = User.query.get('proctor')
    token = proctor.encode_auth_token(proctor.id)

    # test creation
    for category in test_categories:
        response = test_client.post(
            f'/proctor/{datasource_uuid}/log_category',
            json=category,
            headers={'SMARTY-REQUEST-SOURCE': 'internal'})
        assert response.status_code == 200
        assert 'logger' in response.json
        assert 'logcategory_id' in response.json
        assert 'log_archetype' in response.json

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # test get all
    response = test_client.get(f'/proctor/{datasource_uuid}/log_category',
                               headers={'Authorization': token})
    assert len(response.json) == first_lenght + 2

    # test get one
    test_category_index = 0
    test_log_id = test_categories[test_category_index]["logcategory_id"]
    response = test_client.get(
        f'/proctor/{datasource_uuid}/log_category/{test_log_id}',
        headers={'Authorization': token})
    assert response.json['logcategory_id'] == test_categories[
        test_category_index]['logcategory_id']
    assert response.json['log_archetype'] == test_categories[
        test_category_index]['log_archetype']
    assert response.json['logger'] == test_categories[test_category_index][
        'logger']

    # test get a no-existing one --> 123
    test_log_id = 123
    response = test_client.get(
        f'/proctor/{datasource_uuid}/log_category/{test_log_id}',
        headers={'Authorization': token})
    assert response.status_code == 500


def test_update_training_data(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    trainingdata_id = 2
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        headers={
            'Authorization': token
        })
    assert response.status_code == 200
    assert response.json is not None

    training_data = response.json

    logs = [{
        '@timestamp': '2019-10-18T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'log_level': 'ERROR',
        'logcategory_id': 2,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }]

    test_datum = {
        'data': json.dumps(logs),
        'proctormodel_id': 1,
        'cluster_id': 2,
        'predicted_label': 'Unknown',
        'input_df': json.dumps([2]),
        'label_prediction': json.dumps(['another_list']),
        'end_date': 1571401247112,
        'occurrence_date': 1571401247112,
        'incident_name': 'incident_name',
        'env': 1,
        'host': json.dumps(['host']),
        'logger': json.dumps(['logger']),
        'category_occurrences': {
            '1': '1'
        }
    }

    # update no-existing data
    trainingdata_id = 1234
    training_data['predicted_label'] = 'test'
    response = test_client.patch(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        json=training_data,
        headers={'Authorization': token})

    response = test_client.post(f'/proctor/{datasource_uuid}/training_data',
                                json=test_datum,
                                headers={'Authorization': token})
    assert response.status_code == 200

    # update predicted_label and get sequence
    trainingdata_id = response.json['proctortrainingdata_id']
    training_data['predicted_label'] = 'test'
    training_data['input_df'] = json.dumps([2])
    training_data['data'] = json.dumps(logs)
    response = test_client.patch(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}?sequence=1',
        json=training_data,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert 'proctortrainingdata_id' in response.json
    assert 'input_df' in response.json
    assert 'incident_id' in response.json
    assert 'env' in response.json
    # removed
    assert 'proctormodel_id' not in response.json
    assert 'cluster_id' not in response.json
    assert 'predicted_label' not in response.json
    assert 'end_date' not in response.json
    assert 'label_prediction' not in response.json

    # split logs --> incorrect index size [1, 1]
    training_data['index'] = json.dumps([1, 1])
    training_data['input_df'] = json.dumps([2])
    training_data['data'] = json.dumps(logs)
    response = test_client.patch(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        json=training_data,
        headers={'Authorization': token})
    training_data.pop('index')
    assert response.status_code == 200

    # split logs --> correct index size [1, 1, 1], not split
    training_data['index'] = json.dumps([1, 1, 1])
    training_data['input_df'] = json.dumps([2])
    training_data['data'] = json.dumps(logs)
    response = test_client.patch(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        json=training_data,
        headers={'Authorization': token})

    training_data.pop('index')
    assert response.status_code == 200

    # split logs --> correct index size [1, 1, 0]
    training_data['index'] = json.dumps([1, 1, 0])
    response = test_client.patch(
        f'/proctor/{datasource_uuid}/training_data/{trainingdata_id}',
        json=training_data,
        headers={'Authorization': token})
    assert response.status_code == 200


def test_get_category_occurrences(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    incident_id = 2
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    url = '/proctor/{}/category_occurrences?incident_id={}&most_recent=0'.format(
        datasource_uuid, incident_id)
    response = test_client.get(url, headers={'Authorization': token})

    category_occurrences = {
        '2': {
            'id': 2,
            'log': 'No compute node record for host',
            'occurrences': 1
            },
        '5': {'id': 5,
              'log': 'No compute node record for host',
              'occurrences': 1
              },
        '6': {
            'id': 6,
            'log': 'Error during ShareManager',
            'occurrences': 1
            }
        }
    assert response.status_code == 200
    assert category_occurrences == response.json


def test_get_category_occurrences_most_recent(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    incident_id = 2
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    url = '/proctor/{}/category_occurrences?incident_id={}'.format(
        datasource_uuid, incident_id)
    response = test_client.get(url, headers={'Authorization': token})
    category_occurrences = {
        '2': {
            'id': 2,
            'log': 'No compute node record for host',
            'occurrences': 1
            },
        '5': {'id': 5,
              'log': 'No compute node record for host',
              'occurrences': 1
              },
        '6': {
            'id': 6,
            'log': 'Error during ShareManager',
            'occurrences': 1
            }
        }

    assert response.status_code == 200
    assert category_occurrences == response.json


def test_get_incident_rules(test_client):
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    response = test_client.get(f'/proctor/{datasource_uuid}/rules',
                               headers={'Authorization': token})
    assert response.status_code == 200

    body = {
        'rule_id': 1,
        'rule': "logger_series['Logger'] == 'openstack.ceilometer'",
        'active': False
    }
    response = test_client.get(f'/proctor/{datasource_uuid}/rules',
                               json=body,
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[0]['rule_id'] == 1


def test_create_incident_rule(test_client):
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # create malformed rule --> rule':
    # "logger_series['Logger'] == 'openstack.octavia'"
    test_rule = {
        "rule": "this is a test rule",
        "operand_2": "openstack.octavia",
        "opcode": "and"
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 405

    # create a simple rule --> rule':
    # "logger_series['Logger'] == 'openstack.octavia'"
    test_rule = {
        'operand_1': 'Logger',
        'operand_2': 'openstack.octavia',
        'opcode': '=='
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json

    # create another simple rule --> rule': "logger_series['Logger'] == 'openstack.octavia'"
    test_rule = {
        'operand_1': 'Logger',
        'operand_2': 'openstack.octavia',
        'opcode': '=='
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json

    # create a complex rule --> rule': "rule_id[1] & 'rule_id[2]'"
    test_rule = {'operand_1': '1', 'operand_2': '2', 'opcode': '&'}

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json


def test_get_incident_rule(test_client):
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_rule_id = 1

    response = test_client.get(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json
    assert 'rule' in response.json


def test_get_occurrences_days(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    incident_id = 2
    as_calendar = True
    response = test_client.get(
        f'/proctor/{datasource_uuid}/training_data/occurrences_days?incident_id={incident_id}&&as_calendar={as_calendar}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incident_id'] == incident_id
    assert len(response.json['occurrences_days']) != 0


# def test_delete_training_data(test_client):
#     from smarty.celery import celery_proctor_tasks

#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     # delete training datums with end date
#     end_date = 1333462210000
#     payload = {'end_date': end_date}
#     flexmock(celery_proctor_tasks.delete_training_data).should_receive(
#         'delay').replace_with(
#             celery_proctor_tasks.delete_training_data(users[0].id, payload,
#                                                       datasource_uuid))

#     response = test_client.delete(
#         f'/proctor/{datasource_uuid}/training_data?end_date={end_date}',
#         headers={'Authorization': token})
#     assert response.status_code == 204


def test_update_incident_rule(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    # create a simple rule --> rule':
    # "logger_series['Logger'] != 'openstack.octavia'"
    test_rule = {
        'operand_1': 'Logger',
        'operand_2': 'openstack.octavia',
        'opcode': '!='
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json
    test_rule_id_1 = response.json['rule_id']

    # create another simple rule --> rule':
    # "logger_series['Logger'] == 'openstack.octavia'"
    test_rule = {
        'operand_1': 'Logger',
        'operand_2': 'openstack.octavia',
        'opcode': '=='
    }

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json
    test_rule_id_2 = response.json['rule_id']

    # create a complex rule --> rule': "rule_id[1] & 'rule_id[2]'"
    test_rule = {'operand_1': '1', 'operand_2': '2', 'opcode': '&'}

    response = test_client.post(f'/proctor/{datasource_uuid}/rules',
                                json=test_rule,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert 'rule_id' in response.json

    # patch rule #1 --> rule': "logger_series['Logger'] == 'openstack.octavia'"
    test_rule = {
        'operand_1': 'Logger',
        'operand_2': 'openstack.octavia',
        'opcode': '=='
    }

    response = test_client.patch(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id_1}',
        json=test_rule,
        headers={'Authorization': token})
    assert response.status_code == 200
    test_rule_id_3 = response.json['rule_id']

    # patch with a malformed rule --> rule':
    # "logger_series['Logger'] and 'openstack.octavia'"
    test_rule = {
        "operand_1": "Logger",
        "operand_2": "openstack.octavia",
        "opcode": "and"
    }

    response = test_client.patch(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id_3}',
        json=test_rule,
        headers={'Authorization': token})
    assert response.status_code == 405

    # patch with a no-exist complex rule --> rule': "rule_id[1] & 'rule_id[6]'"
    test_rule = {'operand_1': '1', 'operand_2': '10', 'opcode': '&'}

    response = test_client.patch(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id_3}',
        json=test_rule,
        headers={'Authorization': token})
    assert response.status_code == 500

    # patch with a no-exist complex rule --> rule': "rule_id[6] & 'rule_id[1]'"
    test_rule = {'operand_1': '10', 'operand_2': '1', 'opcode': '&'}

    response = test_client.patch(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id_3}',
        json=test_rule,
        headers={'Authorization': token})
    assert response.status_code == 500

    # patch a complex rule --> rule': "rule_id[1] ^ 'rule_id[2]'"
    test_rule = {'operand_1': '1', 'operand_2': '2', 'opcode': '^'}

    response = test_client.patch(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id_3}',
        json=test_rule,
        headers={'Authorization': token})
    assert response.status_code == 200

    # try to patch a no-exist complex rule (1234) --> rule':
    # "rule_id[1] ^ 'rule_id[2]'"
    test_rule = {'operand_1': '1', 'operand_2': '2', 'opcode': '^'}

    response = test_client.patch(f'/proctor/{datasource_uuid}/rules/1234',
                                 json=test_rule,
                                 headers={'Authorization': token})
    assert response.status_code == 500


def test_extract_rule(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    #  extra rule with loggers in database table
    body = {
        'loggers_a': ['openstack.octavia', 'openstack.ceilometer'],
        'loggers_b': ['openstack.glance']
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/rules/extract',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None

    # extract rule with unused loggers
    body = {
        'loggers_a': ['openstack.mock-daniel'],
        'loggers_b': ['openstack.mock-logger']
    }
    response = test_client.post(f'/proctor/{datasource_uuid}/rules/extract',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200

    response = test_client.post(f'/proctor/{datasource_uuid}/rules/extract',
                                json={},
                                headers={'Authorization': token})
    assert response.status_code == 204


def test_check_rule(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    body = {'loggers': ['openstack.octavia', 'openstack.glance']}
    response = test_client.post(f'/proctor/{datasource_uuid}/rules/check_rule',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200


def test_enable_user_rules(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(
        f'/proctor/{datasource_uuid}/rules/enable_user_rules',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_disable_user_rules(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(
        f'/proctor/{datasource_uuid}/rules/disable_user_rules',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_delete_incident_rule(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    test_rule_id = 1

    # delete previous rule
    response = test_client.delete(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    # delete previous rule, again

    response = test_client.delete(
        f'/proctor/{datasource_uuid}/rules/{test_rule_id}',
        headers={'Authorization': token})
    assert response.status_code == 500


# def test_mapping(test_client):
#     # using proctor user
#     user = User.query.get('proctor')
#     token = user.encode_auth_token(user.id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

#     response = test_client.post(f'/proctor/{datasource_uuid}/mapping',
#                                 headers={'SMARTY-REQUEST-SOURCE': 'internal'})
#     assert response.status_code == 424


def test_get_signatures(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    # Assert all signatures are fetch
    response = test_client.get('/proctor/signature',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 4


def test_get_signature(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    signature_id = 1

    #  Assert an existing signature is fetched
    response = test_client.get(f'/proctor/signature/{signature_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['count'] == {}

    no_signature_id = 6
    # Assert a non existing signature is fetch
    response = test_client.get(f'/proctor/signature/{no_signature_id}',
                               headers={'Authorization': token})
    assert response.status_code == 500


def test_get_fingerprint(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    #  Assert all existing fingerprints
    response = test_client.get('/proctor/fingerprint',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2

    #  Assert email fingerprint type
    response = test_client.get('/proctor/fingerprint?fingerprint_type=email',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['fingerprint_type'] == 'email'

    #  Assert ip fingerprint type
    response = test_client.get('/proctor/fingerprint?fingerprint_type=ip',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['fingerprint_type'] == 'ip'

    #  Assert non existing fingerprint
    response = test_client.get(
        '/proctor/fingerprint?fingerprint_type=something',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_create_fingerprint(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {
        'fingerprint_type': 'url',
        'regex':
        '(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})',
        'generic_template': 'X//X.X'
    }

    #  Assert url fingerprint creation
    response = test_client.post('/proctor/fingerprint',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['fingerprint_type'] == 'url'

    body = {
        'fingerprint_type': 'uuid',
        'regex':
        '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|[0-9a-fA-F]{12}4[0-9a-fA-F]{3}[89abAB][0-9a-fA-F]{15}',
        'generic_template': 'X//X.X'
    }

    #  Assert uuid fingeprint creation
    response = test_client.post('/proctor/fingerprint',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['fingerprint_type'] == 'uuid'


def test_patch_fingerprint(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {
        'generic_template': 'XX-X-X-X-XXX',
        'variant': {},
        'variant_lookup': {}
    }
    #  Assert all existing fingerprints
    response = test_client.patch('/proctor/fingerprint?fingerprint_type=uuid',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['generic_template'] == 'XX-X-X-X-XXX'


def test_get_only_inter_relations(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(
        f'/proctor/{datasource_uuid}/rules/only_inter_relations',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) != 0


def test_get_inter_relations(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(
        f'/proctor/{datasource_uuid}/rules/inter_relations',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) != 0


def test_mapping_snooze(test_client):
    # using proctor user
    user = User.query.get('proctor')
    token = user.encode_auth_token(user.id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(f'/proctor/{datasource_uuid}/mapping/snooze',
                                json={},
                                headers={'SMARTY-REQUEST-SOURCE': 'internal'})
    assert response.status_code == 200
    assert response.json['Status'] == 'Could not snooze data source mapping'


def test_datasource_offline(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(f'/proctor/{datasource_uuid}/create_status',
                                headers={'Authorization': token})
    assert response.status_code == 200


def test_environment_offline(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    environment = 1

    response = test_client.post(
        f'/proctor/{datasource_uuid}/{environment}/create_status',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_create_status_check(test_client):
    from smarty.celery import celery_proctor_tasks

    # using proctor user
    user = User.query.get('proctor')
    token = user.encode_auth_token(user.id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    dt = datetime.datetime.utcnow()
    round_date = dt - datetime.timedelta(
        minutes=dt.minute, seconds=dt.second, microseconds=dt.microsecond)
    body = {
        'connected': True,
        'environment': 1,
        'polling_timestamp': str(round_date),
        'errors_received': 100,
        'logs_statistics': {
            "ormuco001": {
                "openstack.mesh": 4
            },
            "ormuco002": {
                "openstack.mesh": 4
            },
            "controller002": {
                "openstack.nova": 1
            },
            "ormuco003": {
                "openstack.mesh": 4
            },
            "controller003": {
                "openstack.nova": 1
            }
        }
    }
    flexmock(celery_proctor_tasks.create_status_check).\
        should_receive('delay').replace_with(
        celery_proctor_tasks.create_status_check(user.id, datasource_uuid, body))

    response = test_client.post(f'/proctor/{datasource_uuid}/status',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 204


def test_get_status(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    environment = 1

    #  Assert pagination limit
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?limit=1',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    #  Assert pagination offset
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?offset=0',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    #  Assert pagination group by day
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?group_by=day',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    #  Assert pagination group by hour
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?group_by=hour',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    #  Assert pagination sort by polling timestamp
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?sort_by=polling_timestamp',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1

    #  Assert pagination sort direction asc
    response = test_client.get(
        f'/proctor/{datasource_uuid}/status/{environment}?sort_direction=asc',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1


# def test_delete_old_es_status_entries(test_client):
#     users = User.query.all()
#     token = users[0].encode_auth_token(users[0].id)
#     datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
#     dt = datetime.datetime.utcnow()
#     dt_millis = int(dt.timestamp() * 1000)

#     #  Assert pagination limit
#     response = test_client.delete(f'/proctor/{datasource_uuid}/status',
#                                   headers={'Authorization': token})
#     assert response.status_code == 401

#     #  Assert pagination limit
#     response = test_client.delete(
#         f'/proctor/{datasource_uuid}/status?end_date={dt_millis}',
#         headers={'Authorization': token})
#     assert response.status_code == 204
