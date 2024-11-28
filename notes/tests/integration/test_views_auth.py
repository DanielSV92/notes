import json
import logging

def test_login(test_client):
    # Create user for login purposes
    test_user = {'email': 'admin@gmail.com', 'password': 'test'}

    # Login
    response = test_client.post('/auth/login', json=test_user)
    logging.info(response)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    assert 'auth_token' in json_data
    assert 'user' in json_data

    # Login with account that does not exist
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


def test_sign_up(test_client):
    # Create test model.
    test_credentials = {
        'email': 'daniel-test@test.com',
        'password': 'testtest'
    }

    response = test_client.post('/auth/sign_up',
                                json=test_credentials)
    assert response.status_code == 200
    json_data = json.loads(response.data)
    logging.info(json_data)
    assert 'email' in json_data['user']

    # Create another account with same email
    response = test_client.post('/auth/sign_up',
                                json=test_credentials)
    assert response.status_code == 409

