from notes.domain.models import User

def test_create_note(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    body = {'note_description': 'my third incredible note'}
    response = test_client.post('/note/create_note',
                                json=body,
                                headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['note_description'] == body['note_description']

def test_update_note(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    note_id = 1
    body = {'note_description': 'my cool updated note'}
    response = test_client.patch(f'/note/update_note/{note_id}',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['note_description'] == body['note_description']

    # Test non existent note
    note_id = 20
    body = {'note_description': 'my_test_note'}
    response = test_client.patch(f'/note/update_note/{note_id}',
                                 json=body,
                                 headers={'Authorization': token})
    assert response.status_code == 404


def test_get_note(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    note_id = 1
    body = {'note_description': 'my cool updated note'}
    response = test_client.get(f'/note/get_note/{note_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['note_description'] == body['note_description']

    note_id = 20
    response = test_client.get(f'/note/get_note/{note_id}',
                               headers={'Authorization': token})
    assert response.status_code == 404


def test_get_notes(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)

    response = test_client.get('/note/get_notes',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['my_notes']) == 2


def test_delete_note(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    note_id = 3
    test_client.get(f'/note/delete_note/{note_id}',
                               headers={'Authorization': token})


def test_search_notes(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    query = 'cool'
    response = test_client.get(f'note/search_notes?query={query}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['my_notes']) == 1


def test_share_note(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    note_id = 1
    share_id = 2
    body = {'note_description': 'my cool updated note'}
    response = test_client.post(f'note/share_note/{note_id}/share/{share_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['note_description'] == body['note_description']

    # Share non existen note
    note_id = 4
    share_id = 2
    body = {'note_description': 'my cool updated note'}
    response = test_client.post(f'note/share_note/{note_id}/share/{share_id}',
                               headers={'Authorization': token})
    assert response.status_code == 404

    # Share to non existen user
    note_id = 1
    share_id = 5
    body = {'note_description': 'my cool updated note'}
    response = test_client.post(f'note/share_note/{note_id}/share/{share_id}',
                               headers={'Authorization': token})
    assert response.status_code == 400
