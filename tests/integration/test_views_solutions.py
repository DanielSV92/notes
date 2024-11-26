import json

import pytest
import requests
from flask import Response
from flexmock import flexmock

from smarty.domain.models import User
from smarty.solutions import controller
from tests.fixtures import integration_test_fixtures as fixtures


@pytest.fixture(autouse=True)
def mockToken():
    flexmock(requests).should_receive('get').and_return(
        fixtures.SKTokenResponse())

    saio_response = Response(None,
                             status=200,
                             headers={
                                 'X-Storage-Url': 'my_url',
                                 'X-Auth-Token': 'my_dummy_token'
                             })

    flexmock(controller).should_receive('authenticate_saio').and_return(
        saio_response)

    flexmock(controller).should_receive('list_files_saio').and_return([])


def test_add_text(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    # Assert create solution by text
    form_params = {
        'solution': 'This is a solution',
        'public': '0',
        'category': 'Billing',
        'subcategory': 'Missing bill',
        'description': 'A short description'
    }
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/text/{incident_type}',
        data=form_params,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['steps'] == form_params.get('solution')
    assert response.json['number_solutions'] == 1

    # Assert update solution by text
    form_params['solution'] = 'This is an updated test'
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/text/{incident_type}',
        data=form_params,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['steps'] == form_params.get('solution')
    assert response.json['number_solutions'] == 1


def test_get_solution(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1
    text_data = 'This is an updated test'

    # Assert get non existing solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/solutions/{incident_type}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['steps'] == text_data
    assert response.json['incidenttype_id'] == 1
    assert response.json['files'] == []
    assert response.json['actions'] == []
    assert response.json['liked'] is None
    assert response.json['total_likes'] == 0

    # Assert get non existing solution
    incident_type = 2
    response = test_client.get(
        f'/incidents/{datasource_uuid}/solutions/{incident_type}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json.get('incidentsolution_id') is None
    assert response.json.get('steps') == ''
    assert response.json['incidenttype_id'] == 2
    assert response.json['files'] == []
    assert response.json['actions'] == ''
    assert response.json['liked'] is None
    assert response.json['total_likes'] == 0


def test_delete_text(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    # Assert reaction creation with api type
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/solutions/text/{incident_type}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['steps'] == '""'
    assert response.json['number_solutions'] == 0
    assert response.json['incidenttype_id'] == 1

    # Add new text to solution
    form_params = {
        'solution': 'This is a solution',
        'public': '0',
        'category': 'Billing',
        'subcategory': 'Missing bill',
        'description': 'A short description'
    }
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/text/{incident_type}',
        data=form_params,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['steps'] == form_params.get('solution')
    assert response.json['number_solutions'] == 1


def test_like_incident_solution(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1
    body = {'liked': True}

    # Assert like solution with non existing user like
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/solutions/solution_like/{incident_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['liked'] == 1
    assert response.json['user_id'] == users[0].id
    assert response.json['total_likes'] == 1

    body = {'liked': False}

    # Assert dislike solution with existing user like
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/solutions/solution_like/{incident_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['liked'] == 0
    assert response.json['user_id'] == users[0].id
    assert response.json['total_likes'] == 0

    body = {'liked': True}

    # Assert like solution with existing user like
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/solutions/solution_like/{incident_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['liked'] == 1
    assert response.json['user_id'] == users[0].id
    assert response.json['total_likes'] == 1


def test_add_action(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    # Assert create solution by action
    body = {'action': 'my_action'}
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/action/{incident_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['solution_actions'] == body
    assert response.json['number_solutions'] == 1

    incident_type = 1

    # Assert update solution by action
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/action/{incident_type}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentsolution_id'] == 1
    assert response.json['solution_actions'] == body
    assert response.json['number_solutions'] == 1


def test_add_comment(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    # Assert add solution comment
    text_comment = 'daniel is awesome'
    response = test_client.post(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidenttype_id'] == 1
    assert response.json['comment'] == text_comment
    assert response.json['comment_id'] == 1

    incident_type = 20
    # Assert add solution comment to non existing solution
    text_comment = 'daniel is awesome'
    response = test_client.post(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 400

    # Assert add solution comment
    text_comment = None
    response = test_client.post(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 400


def test_edit_comment(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1
    comment_id = 1

    # Assert add solution comment
    text_comment = 'daniel is even more awesome'
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidenttype_id'] == 1
    assert response.json['comment'] == text_comment
    assert response.json['comment_id'] == 1

    incident_type = 25
    comment_id = 1

    # Assert edit a comment in a non existing incident type
    text_comment = 'daniel is even more awesome'
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 1
    comment_id = 4

    # Assert edit a non existing comment
    text_comment = 'daniel is even more awesome'
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 2
    comment_id = 1

    # Assert edit a comment that does not correspond to an incident type
    text_comment = 'daniel is even more awesome'
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        data=text_comment,
        headers={'Authorization': token})
    assert response.status_code == 400


def test_get_solution_comments(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    text_comment = 'daniel is even more awesome'
    # Assert get comments from a solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comments',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[0]['incidenttype_id'] == 1
    assert response.json[0]['comment'] == text_comment
    assert response.json[0]['comment_id'] == 1

    incident_type = 2
    # Assert get no comments from an existing solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comments',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == []

    incident_type = 5
    should_return = None
    # Assert get comments from non existing incident solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comments',
        headers={'Authorization': token})
    assert response.status_code == 500
    assert response.json == should_return


def test_remove_comment(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

    incident_type = 6
    comment_id = 1
    # Assert delete comment from non existing incident solution
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 2
    comment_id = 1
    # Assert delete non matching comment with incident solution
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 1
    comment_id = 5
    # Assert delete non existing comment from existing incident solution
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 1
    comment_id = 1
    # Assert delete solution comment
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/solutions/comment/{comment_id}',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_pin_external_solution(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    body = {
        "accepted": True,
        "code":
        "<div class=\"post-text\" itemprop=\"text\"><p>You need to import the module and not use quotes around <code>'uuid.uuid4'</code>.</p><p>It should be somewhat like:</p><pre><code>import uuid  # The uuid moduleclass Post(models.Model):    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # using the function uuid4 on the module    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)    from1 = models.CharField(max_length=20)    To = models.CharField(max_length=20)    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)    objects = PostManager()    def __unicode__(self):        return self.post_id    def __str__(self):        return self.post_id    def get_absolute_url(self):        return reverse(\"posts:detail\", kwargs={\"post_id\": self.post_id})    class Meta:        ordering = [\"-timestamp\", \"-Time\"]</code></pre><p>N.B I've not tested the above code, and I agree with some of the comments you shouldn't need a UUID for the post_id. Without knowing more I couldn't help further.</p></div>",
        "source": "stack_exchange",
        "url":
        "https://stackoverflow.com/questions/38459942/python-how-to-solve-the-issue-badly-formed-hexadecimal-uuid-string-in-djang&sa=U&ved=2ahUKEwid9re-gIbmAhU2xosBHQjKBTYQFjABegQIChAB&usg=AOvVaw2wogh1Ny_jzERfyseXW3ZW",
        "vote": "3"
    }

    # Assert pin an external solution from solver
    response = test_client.post(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['incidentextsolution_id'] == 1
    assert response.json['solution_payload'] == body
    assert response.json['incidenttype_id'] == 1


def test_get_external_solutions(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    body = {
        "accepted": True,
        "code":
        "<div class=\"post-text\" itemprop=\"text\"><p>You need to import the module and not use quotes around <code>'uuid.uuid4'</code>.</p><p>It should be somewhat like:</p><pre><code>import uuid  # The uuid moduleclass Post(models.Model):    post_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # using the function uuid4 on the module    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)    from1 = models.CharField(max_length=20)    To = models.CharField(max_length=20)    timestamp = models.DateTimeField(auto_now=False, auto_now_add=True)    objects = PostManager()    def __unicode__(self):        return self.post_id    def __str__(self):        return self.post_id    def get_absolute_url(self):        return reverse(\"posts:detail\", kwargs={\"post_id\": self.post_id})    class Meta:        ordering = [\"-timestamp\", \"-Time\"]</code></pre><p>N.B I've not tested the above code, and I agree with some of the comments you shouldn't need a UUID for the post_id. Without knowing more I couldn't help further.</p></div>",
        "source": "stack_exchange",
        "url":
        "https://stackoverflow.com/questions/38459942/python-how-to-solve-the-issue-badly-formed-hexadecimal-uuid-string-in-djang&sa=U&ved=2ahUKEwid9re-gIbmAhU2xosBHQjKBTYQFjABegQIChAB&usg=AOvVaw2wogh1Ny_jzERfyseXW3ZW",
        "vote": "3"
    }

    #  Assert get ext solution with existing ext solution on incident type
    response = test_client.get(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[0]['incidentextsolution_id'] == 1
    assert response.json[0]['solution_payload'] == body
    assert response.json[0]['incidenttype_id'] == 1

    incident_type = 2
    #  Assert get ext solution with no ext solution on incident type
    response = test_client.get(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions',
        headers={'Authorization': token})
    assert response.status_code == 200


def test_unpin_external_solution(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 2
    ext_solution_id = 1

    #  Assert delete unmatching ext solution with incident type
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions/{ext_solution_id}',
        headers={'Authorization': token})
    assert response.status_code == 400

    ext_solution_id = 2
    #  Assert delete non existing ext solution
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions/{ext_solution_id}',
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 1
    ext_solution_id = 1
    #  Assert delete existing ext solution
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/{incident_type}/external_solutions/{ext_solution_id}',
        headers={'Authorization': token})
    assert response.status_code == 204


def test_flag_a_solution(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 4

    text_reason = 'awesome solution'
    #  Assert flag a solution with no solution on incident type
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/flags/{incident_type}',
        data=text_reason,
        headers={'Authorization': token})
    assert response.status_code == 400

    incident_type = 1

    text_reason = 'awesome solution'
    #  Assert flag a solution with solution on incident type
    response = test_client.post(
        f'/incidents/{datasource_uuid}/solutions/flags/{incident_type}',
        data=text_reason,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['reason'] == text_reason
    assert response.json['flagged_by'] == users[0].email


def test_get_incident_flags(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    incident_type = 1

    text_reason = 'awesome solution'
    #  Assert get flags from a incident type with solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/solutions/flags/{incident_type}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json[0]['reason'] == text_reason
    assert response.json[0]['flagged_by'] == users[0].email

    incident_type = 4
    #  Assert get flags from a incident type with no solution
    response = test_client.get(
        f'/incidents/{datasource_uuid}/solutions/flags/{incident_type}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json == []


def test_claim_flag(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    text_reason = 'awesome solution'
    #  Assert claim existing flag
    response = test_client.post(
        f'/incidents/{datasource_uuid}/flags/claim/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['reason'] == text_reason
    assert response.json['flagged_by'] == users[0].email
    assert response.json['status'] == 'under_revision'


def test_get_flags(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    author = users[0].email
    solution_id = 1

    text_reason = 'awesome solution'
    #  Assert get flags with pagination solution id and author
    response = test_client.get(
        f'/incidents/{datasource_uuid}/flags?solution_id={1}&flag_author={author}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['reason'] == text_reason
    assert response.json[0]['flagged_by'] == users[0].email

    #  Assert get flags with pagination limit, reviewer and offset
    response = test_client.get(
        f'/incidents/{datasource_uuid}/flags?limit={1}&reviewer={author}&offset=0',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['reason'] == text_reason
    assert response.json[0]['flagged_by'] == users[0].email

    #  Assert get flags with pagination status
    response = test_client.get(
        f'/incidents/{datasource_uuid}/flags?status=under_revision',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['reason'] == text_reason
    assert response.json[0]['flagged_by'] == users[0].email


def test_get_flag(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    text_reason = 'awesome solution'
    #  Assert get flag by id
    response = test_client.get(f'/incidents/{datasource_uuid}/flags/{flag_id}',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['reason'] == text_reason
    assert response.json['flagged_by'] == users[0].email

    flag_id = 2

    text_reason = 'awesome solution'
    #  Assert get not existing flag
    response = test_client.get(f'/incidents/{datasource_uuid}/flags/{flag_id}',
                               headers={'Authorization': token})
    assert response.status_code == 404


def test_get_flag_statuses(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    #  Assert get flag statuses
    response = test_client.get(f'/incidents/flags/status',
                               headers={'Authorization': token})
    assert response.status_code == 200
    assert len(response.json['flag_statuses']) == 4


def test_give_up_flag(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    text_reason = 'awesome solution'
    #  Assert give up existing flag
    response = test_client.post(
        f'/incidents/{datasource_uuid}/flags/give_up/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['reason'] == text_reason
    assert response.json['flagged_by'] == users[0].email
    assert response.json['status'] == 'open'

    flag_id = 2
    #  Assert give up non existing flag
    response = test_client.post(
        f'/incidents/{datasource_uuid}/flags/give_up/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 404


def test_status_flag(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    text_reason = 'awesome solution'

    body = {'new_status': 'open'}
    #  Assert change flag status wihtout changes
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    flag_id = 2

    body = {'new_status': 're_open'}
    #  Assert change flag status of non existing flag
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 404

    flag_id = 1

    body = {'new_status': 're_open'}
    #  Assert change flag status with wrong reviewer
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    #  Claim flag to change status
    response = test_client.post(
        f'/incidents/{datasource_uuid}/flags/claim/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 200

    body = {'new_status': 're_open'}
    #  Assert change flag status
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 200
    assert response.json['reason'] == text_reason
    assert response.json['flagged_by'] == users[0].email
    assert response.json['status'] == 're_open'

    body = {'new_status': 'my_status'}
    #  Assert change flag status with non existing status
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json=body,
        headers={'Authorization': token})
    assert response.status_code == 400

    #  Assert change flag status with nothing
    response = test_client.patch(
        f'/incidents/{datasource_uuid}/flags/status/{flag_id}',
        json={},
        headers={'Authorization': token})
    assert response.status_code == 400


def test_delete_flag(test_client):
    users = User.query.all()
    token = users[0].encode_auth_token(users[0].id)
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    flag_id = 1

    #  Assert delete flag
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/flags/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 204

    #  Assert delete non existing flag
    response = test_client.delete(
        f'/incidents/{datasource_uuid}/flags/{flag_id}',
        headers={'Authorization': token})
    assert response.status_code == 404
