import datetime
import json
from os import path

import pytest
import requests
from flask import Response
from flexmock import flexmock

from smarty.data_sources import controller
from smarty.domain.models import User
from smarty.solutions import controller as solutions_controller
from tests.fixtures import integration_test_fixtures as fixtures


@pytest.fixture(autouse=True)
def mockToken():
    from smarty.celery import celery_datasource_tasks

    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())

    proctor_response = Response(None, status=200)
    proctor_response.headers.remove('Content-Type')

    flexmock(celery_datasource_tasks.trigger_proctor_update).should_receive(
        'delay').and_return(proctor_response)

    flexmock(requests).should_receive('post').and_return(
        fixtures.SKLoginResponse())


@pytest.fixture
def mock_index_search():
    index_list = [
        'kolla_logging:flog-*',
        'veon_logging:flog-*',
        'team_cluster:flog-*',
    ]
    flexmock(controller).should_receive('datasource_index_search').and_return(
        index_list)


def test_create_datasource(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    form_params = {
        'display_name': 'Test datasource',
        'es_port': 9201,
        'es_host': '200.04.83.147',
        'es_schema': 'http',
        'owner': users[0].id,
        'es_user': 'cerebro',
        'es_password': '0rmuco1313!',
        'index_name': 'uat_cluster:flog-*',
        'env_display_name': 'Test env',
        'uuid': test_uuid,
        'source_type': 'elastic'
    }

    flexmock(celery_datasource_tasks.create_data_source).should_receive(
        'delay').and_return(
            celery_datasource_tasks.create_data_source(users[0].id,
                                                       form_params, None))
    #  Assert datasource created
    response = test_client.post(f'/proctor/data_sources',
                                data=form_params,
                                headers={'Authorization': token})
    assert response.status_code == 200


def test_get_datasource(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    #  Assert get newly created data source
    response = test_client.get(f'/proctor/data_sources/{test_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['display_name'] == 'Test datasource'
    assert response.json['owner'] == users[0].id
    assert response.json['source_id'] == 2


def test_get_environments(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    env_id = 1

    #  Assert get env
    response = test_client.get(f'/proctor/data_sources/environments/{ds_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2
    assert response.json[0]['env_display_name'] == 'mtl Ormuco'
    assert response.json[0]['environment_id'] == env_id
    assert response.json[0]['datasource_uuid'] == ds_uuid


def test_get_environment(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    env_id = 1

    #  Assert get env with data source
    response = test_client.get(
        f'/proctor/data_sources/environments/{ds_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['env_display_name'] == 'mtl Ormuco'
    assert response.json['environment_id'] == env_id
    assert response.json['datasource_uuid'] == ds_uuid

    env_id = 4
    #  Assert get non existing env
    response = test_client.get(
        f'/proctor/data_sources/environments/{ds_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_create_env(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    body = {
        'es_port': '9201',
        'es_host': '200.94.83.147',
        'es_schema': 'http',
        'es_user': 'cerebro',
        'es_password': '0rmuco1313!',
        'index_name': 'veon_cluster:flog-*',
        'env_display_name': 'Test other env',
    }

    flexmock(celery_datasource_tasks.create_environment).should_receive(
        'delay').and_return(
            celery_datasource_tasks.create_environment(users[0].id, test_uuid,
                                                       body))
    #  Assert env witn index already created
    response = test_client.post(
        f'/proctor/data_sources/environments/{test_uuid}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    env_id = 3
    #  Assert get env was created
    response = test_client.get(
        f'/proctor/data_sources/environments/{test_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['env_display_name'] == 'Test other env'
    assert response.json['environment_id'] == env_id
    assert response.json['datasource_uuid'] == test_uuid
    assert response.json['index_name'] == 'veon_cluster:flog-*'


def test_get_all_data_sources(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Assert that no rules are present at beginning of test.
    response = test_client.get('/proctor/data_sources',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 3


def test_check_env_connection(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    body = {'index_name': 'uat_cluster:flog-*'}
    # Assert that no rules are present at beginning of test.
    response = test_client.post(
        f'/proctor/data_sources/environments/{ds_uuid}/check_connection',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200


def test_update_env(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'
    env_id = 3

    body = {
        'index_name': 'team_cluster:flog-*',
        'env_display_name': 'Test updated env',
        'features': "['Incidents']"
    }

    flexmock(celery_datasource_tasks.update_environment).should_receive(
        'delay').and_return(
            celery_datasource_tasks.update_environment(users[0].id, test_uuid,
                                                       env_id, body))
    #  Assert env witn index already created
    response = test_client.patch(
        f'/proctor/data_sources/environments/{test_uuid}/{env_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200

    #  Assert get env was created
    response = test_client.get(
        f'/proctor/data_sources/environments/{test_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['env_display_name'] == 'Test updated env'
    assert response.json['environment_id'] == env_id
    assert response.json['datasource_uuid'] == test_uuid
    assert response.json['index_name'] == 'team_cluster:flog-*'


def test_update_datasource(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    form_params = {
        'display_name': 'Test updated datasource',
        'es_port': 9201,
        'es_host': '200.04.83.147',
        'es_schema': 'http',
        'es_user': 'cerebro',
        'es_password': '0rmuco1313!'
    }

    flexmock(celery_datasource_tasks.update_data_source).should_receive(
        'delay').and_return(
            celery_datasource_tasks.update_data_source(users[0].id, None,
                                                       test_uuid, form_params, token))
    #  Assert datasource created
    response = test_client.patch(f'/proctor/data_sources/{test_uuid}',
                                 data=form_params,
                                 headers={'Authorization': token})
    assert response.status_code == 200

    response = test_client.get(f'/proctor/data_sources/{test_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['display_name'] == 'Test updated datasource'
    assert response.json['owner'] == users[0].id
    assert response.json['source_id'] == 2


def test_get_hosts_by_environment(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    env_id = 2

    response = test_client.get(
        f'/proctor/data_sources/hosts/{ds_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == ['myTesthost']

    env_id = 3
    response = test_client.get(
        f'/proctor/data_sources/hosts/{ds_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_get_loggers_by_host(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    env_id = 2
    host = 'myTesthost'

    response = test_client.get(
        f'/proctor/data_sources/loggers/{ds_uuid}/{env_id}/{host}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == ['openstack.swift']

    host = 'someotherhost'
    response = test_client.get(
        f'/proctor/data_sources/loggers/{ds_uuid}/{env_id}/{host}',
        headers={'Authorization': token})
    assert response.status_code == 400

    env_id = 3
    host = 'someotherhost'
    response = test_client.get(
        f'/proctor/data_sources/loggers/{ds_uuid}/{env_id}/{host}',
        headers={'Authorization': token})
    assert response.status_code == 400


def test_get_logs_by_logger(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    env_id = 2
    host = 'myTesthost'
    logger = 'openstack.swift'

    response = test_client.get(
        f'/proctor/data_sources/logs/{ds_uuid}/{env_id}/{host}/{logger}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == [7]

    logger = 'someother.logger'
    response = test_client.get(
        f'/proctor/data_sources/logs/{ds_uuid}/{env_id}/{host}/{logger}',
        headers={'Authorization': token})
    assert response.status_code == 400

    logger = 'openstack.swift'
    host = 'someotherhost'
    response = test_client.get(
        f'/proctor/data_sources/logs/{ds_uuid}/{env_id}/{host}/{logger}',
        headers={'Authorization': token})
    assert response.status_code == 400

    env_id = 3
    host = 'someotherhost'
    response = test_client.get(
        f'/proctor/data_sources/logs/{ds_uuid}/{env_id}/{host}/{logger}',
        headers={'Authorization': token})
    assert response.status_code == 400


def test_get_datasource_relations(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/proctor/data_sources/relations',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None


def test_get_data_source_quick_view(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/proctor/{ds_uuid}/data_sources/quick_view',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None


def test_get_extended_data_source(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    response = test_client.get(f'/proctor/data_sources/extended/{test_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['display_name'] == 'Test updated datasource'
    assert response.json['es_port'] == 9201
    assert response.json['es_schema'] == 'http'


def test_data_source_share_with(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    body = {
        'role_name': 'Administrator',
        'user_email': users[1].email
    }

    response = test_client.post(f'/proctor/data_sources/share/{ds_uuid}',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[f'{users[1].email}'] is not None

    response = test_client.post(f'/proctor/data_sources/share/{ds_uuid}',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 400


def test_get_data_source_share(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/proctor/data_sources/share/{ds_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[f'{users[1].email}'] is not None


def test_update_data_source_share_with(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    body = {'role': 'Administrator', 'user': users[1].email}

    response = test_client.patch(f'/proctor/data_sources/share/{ds_uuid}',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 400

    body = {'role': 'Proctor', 'user': users[1].email}

    response = test_client.patch(f'/proctor/data_sources/share/{ds_uuid}',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[f'{users[1].email}'] is not None


def test_get_all_env_features(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(
        f'/proctor/data_sources/environments/env_features',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2


def test_get_cerebro_settings(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/proctor/cerebro_settings',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['cerebro_id'] == 1
    assert response.json['package_type'] == 'standard'
    assert response.json['max_ds'] == 10


def test_set_cerebro_settings(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.post(f'/proctor/cerebro_settings/premium',
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['cerebro_id'] == 1
    assert response.json['package_type'] == 'premium'
    assert response.json['max_ds'] == 50

    response = test_client.post(f'/proctor/cerebro_settings/test_package',
                                headers={'Authorization': token})
    assert response.status_code == 400


def test_delete_data_source_share_with(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    body = {'user': users[1].email}

    response = test_client.delete(f'/proctor/data_sources/share/{ds_uuid}',
                                  json=body,
                                  headers={'Authorization': token})
    assert response.status_code == 204

    body = {'user': users[1].email}

    response = test_client.delete(f'/proctor/data_sources/share/{ds_uuid}',
                                  json=body,
                                  headers={'Authorization': token})
    assert response.status_code == 404


def test_datasource_index_search_inuse(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(
        f'/proctor/data_sources/index_search/inuse/{ds_uuid}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2


def test_datasource_index_search(test_client,
                                 mock_index_search):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/proctor/data_sources/index_search/{ds_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 3


def test_datasource_index_search_unused(test_client,
                                        mock_index_search):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(
        f'/proctor/data_sources/index_search/unused/{ds_uuid}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1


def test_datasource_connect_unused(test_client,
                                   mock_index_search):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    index = 'team_cluster:flog-*'

    body = {
        'index_name': index,
        'env_display_name': index.split(":")[0].replace("_", " ").title()
    }
    flexmock(celery_datasource_tasks.create_environment).should_receive(
        'delay').and_return(
            celery_datasource_tasks.create_environment(users[0].id, ds_uuid,
                                                       body))

    response = test_client.get(
        f'/proctor/data_sources/indexes/connect_unused/{ds_uuid}',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_get_datasource_icon(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/proctor/data_sources/icon/{ds_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == {}


def test_update_datasource_icon(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    base_path = path.dirname(__file__)
    filepath = path.abspath(
        path.join(base_path, "..", "static", "test_image.png"))

    file = {'datasource_icon': open(filepath, 'rb')}

    response = test_client.patch(f'/proctor/data_sources/icon/{ds_uuid}',
                                 data=file,
                                 headers={
                                     'Authorization': token,
                                     'Content-Type': 'multipart/form-data'
                                 })
    assert response.status_code == 200
    assert response.json['uuid'] == ds_uuid

    response = test_client.patch(f'/proctor/data_sources/icon/{ds_uuid}',
                                 data={},
                                 headers={
                                     'Authorization': token,
                                     'Content-Type': 'multipart/form-data'
                                 })
    assert response.status_code == 400


def test_delete_env(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'
    env_id = 3

    flexmock(celery_datasource_tasks.delete_environment).should_receive(
        'delay').and_return(
            celery_datasource_tasks.delete_environment(users[0].id, test_uuid,
                                                       env_id))
    #  Assert delete env
    response = test_client.delete(
        f'/proctor/data_sources/environments/{test_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 404

    #  Assert delete non existing env
    response = test_client.get(
        f'/proctor/data_sources/environments/{test_uuid}/{env_id}',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_delete_datasource(test_client):
    from smarty.celery import celery_datasource_tasks

    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    test_uuid = 'ce51cdab-e679-4486-8575-f9a19a231c19'

    body = {'user_password': users[0].password}

    flexmock(solutions_controller).should_receive('delete_datasource_saio')
    flexmock(celery_datasource_tasks.delete_data_source).should_receive(
        'delay').and_return(
            celery_datasource_tasks.delete_data_source(users[0].id, test_uuid))
    #  Assert after delete data source
    response = test_client.delete(f'/proctor/data_sources/{test_uuid}',
                                  json=body,
                                  headers={'Authorization': token})
    assert response.status_code == 404

    #  Assert get non existing data source
    response = test_client.get(f'/proctor/data_sources/{test_uuid}',
                               headers={'Authorization': token})
    assert response.status_code == 400
