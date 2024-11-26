import json
import uuid
from os import path

import flask
import pytest
import requests
from flask import Response
from flexmock import flexmock

from smarty.auth import utils
from smarty.domain.models import User
from tests.fixtures import integration_test_fixtures as fixtures


def test_login(test_client):
    # Create user for login purposes
    test_user = {'email': 'admin@gmail.com', 'password': 'test'}

    # Login
    flexmock(requests).should_receive('post').and_return(
        fixtures.SKLoginResponse())
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKUserGroups())
    response = test_client.post('/auth/login', json=test_user)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'status' in json_data
    assert 'authentication_token' in json_data
    assert 'message' in json_data

    # Login with account that does not exist
    flexmock(requests).should_receive('post').and_return(
        fixtures.SKLoginResponse(False))
    test_invalid_credentials = {
        'email': 'invalid@invalid.com',
        'password': 'testtest'
    }
    response = test_client.post('/auth/login', json=test_invalid_credentials)
    assert response.status_code == 401

    # Login with wrong password
    test_wrong_password = {
        'email': 'admin@gmail.com',
        'password': 'testtesttest'
    }
    response = test_client.post('/auth/login', json=test_wrong_password)
    assert response.status_code == 401


def test_get_user(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Get account for a valid token
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())
    response = test_client.get('/auth/status',
                               headers={'Authorization': token})
    assert response.status_code == 200

    # Invalid token
    auth_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MzQ5OTA1MzEsImlhdCI6MTUzNDk4NjkzMSwic3ViIjoyfQ.9C3wYW4nSzv6Zj7jxeVb5ABUVD245ugQXIF67RRDLbs'

    # Get account for an invalid token
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse(False))
    response = test_client.get('/auth/status',
                               headers={'Authorization': auth_token})
    assert response.status_code == 401

    # Try to get user
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())
    email = {'email': 'admin@gmail.com'}
    response = test_client.get('/auth/user',
                               query_string=email,
                               headers={'Authorization': token})
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'email' in json_data


def test_logout(test_client):
    test_user = {'email': 'admin@gmail.com', 'password': 'test'}

    # Login
    flexmock(requests).should_receive('post').and_return(
        fixtures.SKLoginResponse())
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKUserGroups())
    response = test_client.post('/auth/login', json=test_user)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    user_id = json_data['id']
    auth_token = json_data['authentication_token']

    # Logout
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())
    response = test_client.post(f'/auth/logout',
                                headers={'Authorization': auth_token})
    assert response.status_code == 200


def test_get_auth_token_status(test_client):
    test_user = {'email': 'admin@gmail.com', 'password': 'test'}
    # Login
    flexmock(requests).should_receive('post').and_return(
        fixtures.SKLoginResponse())
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKUserGroups())
    response = test_client.post('/auth/login', json=test_user)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    user_id = json_data['id']
    auth_token = json_data['authentication_token']

    # Try to get a token when you are logged in
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())
    response = test_client.get(f'/auth/status',
                               headers={'Authorization': auth_token})
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'email' in json_data['data']
    assert 'status' in json_data

    # Try to get status without a token
    response = test_client.get('/auth/status')
    assert response.status_code == 401


@pytest.fixture(autouse=True)
def mockToken():
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())

    # proctor_response = Response(None, status=500)
    # proctor_response.headers.remove('Content-Type')

    # flexmock(requests).should_receive('post').and_return(
    #     proctor_response)


def test_get_user(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    response = test_client.get(f'/auth/user?email=admin2@gmail.com',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None


def test_get_users(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(
        f'/auth/users?search=admin2@gmail.com&role_name=Administrator',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1


def test_validate(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/validate',
                               headers={'Authorization': token})
    assert response.status_code == 200


def test_get_roles(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/get_roles',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1


def test_create_role(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {'name': 'Intern', 'description': 'Some that works for free'}
    response = test_client.post(f'/auth/create_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200


def test_create_user_by_admin(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    # Create test model.
    test_credentials = {
        'email': 'cerebro-test@test.com',
        'password': 'testtest',
        'role_name': 'Administrator'
    }

    response = test_client.post('/auth/register',
                                json=test_credentials,
                                headers={'Authorization': token})
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'email' in json_data

    # Create another account with same email
    response = test_client.post('/auth/register',
                                json=test_credentials,
                                headers={'Authorization': token})
    assert response.status_code == 409


def test_assign_role(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    body = {'email': 'cerebro-test@test.com', 'role_name': 'Intern'}

    response = test_client.post(f'/auth/assign_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None


def test_confirm_account(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/confirm_account/{token}')
    assert response.status_code == 302

    token = users[1].encode_auth_token(users[1].id)
    response = test_client.get(f'/auth/confirm_account/{token}')
    assert response.status_code == 302

    token = users[2].encode_auth_token(users[2].id)
    response = test_client.get(f'/auth/confirm_account/{token}')
    assert response.status_code == 302

    token = users[3].encode_auth_token(users[3].id)
    response = test_client.get(f'/auth/confirm_account/{token}')
    assert response.status_code == 302


def test_reconfirm_account(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {
        'email': 'cerebro-test@test.com',
    }
    flexmock(utils).should_receive('send_email_pass_reset').and_return(True)
    response = test_client.post(f'/auth/confirm_account', json=body)
    assert response.status_code == 200


def test_change_password(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    body = {'old_password': 'test', 'new_password': 'moretest'}
    response = test_client.patch(f'/auth/change_password',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json is not None


def test_reset_password(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/reset_password/{token}')
    assert response.status_code == 302


def test_create_admin(test_client):

    response = test_client.post(f'/auth/create_admin', json={})
    assert response.status_code == 501


def test_create_admin(test_client):

    response = test_client.post(f'/auth/create_proctor', json={})
    assert response.status_code == 501


def test_remove_role(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {'email': 'cerebro-test@test.com', 'role_name': 'Intern'}

    response = test_client.post('/auth/remove_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['email'] == body['email']

    body = {'email': 'mock_account@test.com', 'role_name': 'Intern'}

    response = test_client.post('/auth/remove_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 404

    body = {'email': 'cerebro-test@test.com', 'role_name': 'Mockrole'}

    response = test_client.post('/auth/remove_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 404


def test_update_user(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {
        'email': 'admin@gmail.com',
        'first_name': 'iwashere',
        'last_name': 'iwashereagain',
        'phone_number': '44435654'
    }

    response = test_client.patch(f'/auth/user',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['id'] == '1'
    assert response.json['email'] == 'admin@gmail.com'
    assert response.json['first_name'] == body['first_name']
    assert response.json['last_name'] == body['last_name']


def test_delete_role(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {'role_name': 'Intern'}

    response = test_client.post('/auth/delete_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 204

    response = test_client.post('/auth/delete_role',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 404


def test_delete_user(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    body = {'email': 'cerebro-test@test.com'}
    response = test_client.post(f'/auth/delete_user',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 204

    body = {'email': 'cerebro-test@test.com'}
    response = test_client.post(f'/auth/delete_user',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 404


def test_get_all_roles_and_permissions(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/get_all_roles_permissions',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 2


def test_patch_account_picture(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    base_path = path.dirname(__file__)
    filepath = path.abspath(
        path.join(base_path, "..", "static", "test_image2.png"))

    body = {
        'email': 'admin@gmail.com',
        'img_filename': 'test_image2',
        'img_src': filepath
    }
    response = test_client.patch(f'/auth/account_picture',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['id'] == 1


def test_post_account_picture(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    base_path = path.dirname(__file__)
    filepath = path.abspath(
        path.join(base_path, "..", "static", "test_image.png"))

    file = {
        'email': 'admin@gmail.com',
        'img_filename': 'test_image',
        'image': open(filepath, 'rb')
    }
    response = test_client.post(f'/auth/account_picture',
                                data=file,
                                headers={
                                    'Authorization': token,
                                    'Content-Type': 'multipart/form-data'
                                })
    assert response.status_code == 200
    assert response.json['id'] == 2
    assert response.json['img_filename'] == file['img_filename']

    base_path = path.dirname(__file__)
    filepath = path.abspath(
        path.join(base_path, "..", "static", "test_image2.png"))

    file = {
        'email': 'admin@gmail.com',
        'img_filename': 'test_image2',
        'image': open(filepath, 'rb')
    }
    response = test_client.post(f'/auth/account_picture',
                                data=file,
                                headers={
                                    'Authorization': token,
                                    'Content-Type': 'multipart/form-data'
                                })
    assert response.status_code == 200
    assert response.json['id'] == 2
    assert response.json['img_filename'] == file['img_filename']

    response = test_client.post(f'/auth/account_picture',
                                data={},
                                headers={
                                    'Authorization': token,
                                    'Content-Type': 'multipart/form-data'
                                })
    assert response.status_code == 404


def test_get_account_picture(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get(f'/auth/account_picture?email=admin@gmail.com',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['id'] == 2
    assert response.json['img_filename'] == 'test_image2'
