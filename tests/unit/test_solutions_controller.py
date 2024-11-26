import copy
import json
import mock
import os
import sys
import unittest

from flexmock import flexmock
import smarty.errors as error

from sqlalchemy.orm.query import Query
from unittest import TestCase
from unittest.mock import patch

from smarty.app import create_app
from smarty.domain.models import DataSource
from smarty.domain.models import HelpdeskCategory
from smarty.domain.models import HelpdeskSubCategory
from smarty.domain.models import IncidentEvent
from smarty.domain.models import IncidentExternalSolution
from smarty.domain.models import IncidentSolution
from smarty.domain.models import IncidentType
from smarty.domain.models import LogCategory
from smarty.extensions import db
from smarty.incidents import controller as incident_controller
from smarty.proctor import controller as proctor_controller
from smarty.settings import Config
from smarty.solutions import controller
from smarty.solutions import utils
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestController(TestCase):
    def setup_class(self):
        self.controller = controller

    # @patch('requests.post')
    # def test_authenticate(self, mocked_post):
    #     headers = unit_test_fixtures.headers
    #     data = unit_test_fixtures.data
    #     return_value = unit_test_fixtures.auth_response
    #     mocked_post.return_value = mock.Mock(status_code=200)
    #     mocked_post.return_value.json.return_value = return_value
    #
    #     response = controller.authenticate()
    #
    #     mocked_post.assert_called_with(
    #         url='https://api-mtl-uat001.ormuco.com:5000/v3/auth/tokens',
    #         headers=headers, json=data)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json(), return_value)

    @patch('requests.get')
    def test_authenticate_saio(self, mocked_get):
        headers = unit_test_fixtures.headers_saio
        return_value = unit_test_fixtures.auth_response
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = return_value

        response = self.controller.authenticate_saio()

        mocked_get.assert_called_with(url='http://cerebro-swift:80/auth/v1.0',
                                      headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), return_value)

    @patch('requests.get')
    def test_list_files_saio(self, mocked_get):
        token = unit_test_fixtures.token_saio
        headers = {'X-Auth-Token': token}
        params = {"format": "json"}
        incident_id = 1
        storage_url = unit_test_fixtures.storage_url_saio
        return_value = unit_test_fixtures.object_storage_list
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = return_value
        datasource_uuid = unit_test_fixtures.datasource_uuid_saio

        should_return = controller.list_files_saio(
            token=token,
            storage_url=storage_url,
            datasource_uuid=datasource_uuid,
            folder_id=incident_id)

        mocked_get.assert_called_with(
            'http://swift-aio:8080/v1/AUTH_cerebro/a92c54c5-b1a5-4311-b476-f028171df345_incident_type_1',
            headers=headers,
            params=params)
        assert should_return == return_value

    @patch('requests.get')
    def test_list_object_storage_saio(self, mocked_get):
        token = unit_test_fixtures.token_saio
        headers = {'X-Auth-Token': token}
        params = {"format": "json"}
        storage_url = unit_test_fixtures.storage_url_saio
        return_value = unit_test_fixtures.object_storage_list
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = return_value

        should_return = controller.list_object_storage_saio(
            token=token, storage_url=storage_url)

        mocked_get.assert_called_with('http://swift-aio:8080/v1/AUTH_cerebro',
                                      headers=headers,
                                      params=params)
        assert should_return == return_value

    @patch('requests.put')
    def test_create_object_storage_saio(self, mocked_put):
        token = unit_test_fixtures.token_saio
        headers = {'X-Auth-Token': token, 'X-Container-Read': '.r:*'}
        incident_id = 1
        storage_url = unit_test_fixtures.storage_url_saio
        return_value = unit_test_fixtures.object_storage_list
        mocked_put.return_value = mock.Mock(status_code=200)
        mocked_put.return_value.json.return_value = return_value
        datasource_uuid = unit_test_fixtures.datasource_uuid_saio

        flexmock(incident_controller).should_receive('check_datasource_status')

        should_return = controller.create_object_storage_saio(
            token=token,
            storage_url=storage_url,
            datasource_uuid=datasource_uuid,
            incidenttype_id=incident_id)

        mocked_put.assert_called_with(
            'http://swift-aio:8080/v1/AUTH_cerebro/a92c54c5-b1a5-4311-b476-f028171df345_incident_type_1',
            headers=headers)
        assert should_return.json() == return_value

    @patch('requests.put')
    def test_add_file_saio(self, mocked_put):
        file = unit_test_fixtures.file
        filename = file.filename
        content = file.read
        token = unit_test_fixtures.token_saio
        headers = {
            'X-Auth-Token': token,
            'Content-Length': str(sys.getsizeof(content)),
            'Content-Type': 'application/force-download'
        }
        incident_id = 1
        storage_url = unit_test_fixtures.storage_url_saio
        return_value = unit_test_fixtures.object_storage_list
        mocked_put.return_value = mock.Mock(status_code=200)
        mocked_put.return_value.json.return_value = return_value
        datasource_uuid = unit_test_fixtures.datasource_uuid_saio

        should_return = controller.add_file_saio(
            token=token,
            storage_url=storage_url,
            datasource_uuid=datasource_uuid,
            folder_id=incident_id,
            file=file)

        mocked_put.assert_called_with(
            f'http://swift-aio:8080/v1/AUTH_cerebro/a92c54c5-b1a5-4311-b476-f028171df345_incident_type_1/{filename}',
            headers=headers,
            data=content)
        self.assertEqual(should_return.status_code, 200)
        assert should_return.json() == return_value

    @patch('requests.delete')
    def test_delete_file_saio(self, mocked_delete):
        file = unit_test_fixtures.file
        filename = file.filename
        token = unit_test_fixtures.token_saio
        headers = {'X-Auth-Token': token}
        incident_id = 1
        storage_url = unit_test_fixtures.storage_url_saio
        datasource_uuid = unit_test_fixtures.datasource_uuid_saio

        controller.delete_file_saio(token=token,
                                    storage_url=storage_url,
                                    datasource_uuid=datasource_uuid,
                                    incidenttype_id=incident_id,
                                    filename=filename)

        mocked_delete.assert_called_with(
            f'http://swift-aio:8080/v1/AUTH_cerebro/a92c54c5-b1a5-4311-b476-f028171df345_incident_type_1/{filename}',
            headers=headers)

    @patch('requests.delete')
    def test_delete_container_saio(self, mocked_delete):
        token = unit_test_fixtures.token_saio
        headers = {'X-Auth-Token': token}
        incident_id = 1
        storage_url = unit_test_fixtures.storage_url_saio
        datasource_uuid = unit_test_fixtures.datasource_uuid_saio

        controller.delete_container_saio(token=token,
                                         storage_url=storage_url,
                                         datasource_uuid=datasource_uuid,
                                         incidenttype_id=incident_id)

        mocked_delete.assert_called_with(
            'http://swift-aio:8080/v1/AUTH_cerebro/a92c54c5-b1a5-4311-b476-f028171df345_incident_type_1',
            headers=headers)

    def test_update_incident_solution(self):
        user = unit_test_fixtures.user
        incident_solution = unit_test_fixtures.incident_solution
        incident = unit_test_fixtures.incident
        incidents = [incident]
        incidenttype_id = 1
        number_solutions = 0
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        should_return = incident_solution
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(incident_solution)

        flexmock(controller).should_receive('get_incident_solution').and_return(incident_solution)

        flexmock(controller).should_receive('publish_message').and_return(False)

        flexmock(incident_solution).should_receive('update')

        flexmock(db.session).should_receive('commit')

        flexmock(incident_controller).should_receive('get_incidents').and_return(incidents)

        flexmock(incident_controller).should_receive('update_incident').and_return(incident)

        returned = controller.update_incident_solution(
            user, incidenttype_id, number_solutions, datasource_uuid)
        assert returned == should_return

    def test_add_incident_solution_text(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        hd_category = unit_test_fixtures.hd_category
        hd_subcategory = unit_test_fixtures.hd_subcategory
        token = 'some token'
        incident_solution = unit_test_fixtures.incident_solution
        incident = unit_test_fixtures.incident
        incidents = [incident]
        should_return = incident_solution
        incident_type = unit_test_fixtures.incident_type
        text = {
            'solution': 'This is a solution',
            'public': '0',
            'category': 'Billing',
            'subcategory': 'Missing bill',
            'description': 'A short description'
        }

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)
        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(incident_solution)
        flexmock(controller).should_receive('validate_capability').and_return(True)
        flexmock(controller).should_receive('_get_user_likes_dict').and_return({})
        flexmock(controller).should_receive('like_solution_dict').and_return({})
        flexmock(controller).should_receive('publish_message').and_return(False)
        flexmock(incident_solution).should_receive('update')
        flexmock(incident_controller).should_receive('get_incidents').and_return(incidents)
        flexmock(controller).should_receive('add_share_solution')
        flexmock(HelpdeskCategory).should_receive('query.filter.first').and_return(hd_category)
        flexmock(HelpdeskSubCategory).should_receive('query.filter.first').and_return(hd_subcategory)
        flexmock(IncidentEvent).should_receive('add')

        returned = controller.add_incident_solution_text(
            user, datasource_uuid, incidenttype_id, text, token)
        assert returned == should_return

    def test_get_incidenttype_archetypes(self):
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        incident_type = unit_test_fixtures.incident_type
        should_return = [incident_type]

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(LogCategory).should_receive('query.filter.first').and_return(incident_type)

        returned = controller.get_incidenttype_archetypes(datasource_uuid, incidenttype_id)
        assert returned == should_return

    def test_add_share_solution(self):
        user = unit_test_fixtures.user
        token = 'some token'
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incident_solution = unit_test_fixtures.incident_solution
        incidenttype_id = 1
        text = b'some text'
        should_return = None

        flexmock(controller).should_receive('get_incidenttype_archetypes').and_return([1])

        flexmock(proctor_controller).should_receive('anonymize_archetypes').and_return([])

        flexmock(controller).should_receive('publish_message').and_return(False)

        returned = controller.add_share_solution(
            user, token, datasource_uuid, incident_solution, incidenttype_id, text)
        assert returned == should_return

    def test_delete_incident_solution_text(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        token = 'some token'
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        incident = unit_test_fixtures.incident
        incidents = [incident]
        should_return = incident_solution
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(controller).should_receive('validate_capability').and_return(True)

        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(incident_solution)

        flexmock(incident_solution).should_receive('update')

        flexmock(incident_controller).should_receive('get_incidents').and_return(incidents)

        returned = controller.delete_incident_solution_text(
            user, datasource_uuid, incidenttype_id, token)
        assert returned == should_return

    def test_add_incident_solution_action(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        action = {}
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        should_return = incident_solution
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(incident_solution)

        flexmock(incident_solution).should_receive('update')

        returned = controller.add_incident_solution_action(
            user, datasource_uuid, incidenttype_id, action)
        assert returned == should_return

    def test_pin_external_solution(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        body = {}
        data_source = unit_test_fixtures.data_source
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        should_return = unit_test_fixtures.external_solution_dict
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)

        flexmock(controller).should_receive('validate_capability').and_return(True)

        flexmock(IncidentExternalSolution).should_receive('add').and_return(incident_solution)

        flexmock(controller).should_receive('publish_message').and_return(False)

        flexmock(db.session).should_receive('commit')

        returned = controller.pin_external_solution(
            user, datasource_uuid, incidenttype_id, body)
        del returned['pin_datetime']
        del should_return['pin_datetime']
        assert returned == should_return

    def test_get_ext_solution(self):
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        data_source = unit_test_fixtures.data_source
        external_solution = unit_test_fixtures.external_solution
        should_return = [unit_test_fixtures.external_solution_dict]
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)
        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)
        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)
        flexmock(IncidentExternalSolution).should_receive('query.filter.all').and_return([external_solution])
        flexmock(LogCategory).should_receive('query.filter.first').and_return(None)

        returned = controller.get_ext_solution(datasource_uuid, incidenttype_id)
        assert returned == should_return

    def test_unpin_external_solution(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        incidentextsolution_id = 1
        external_solution = unit_test_fixtures.external_solution
        data_source = unit_test_fixtures.data_source
        should_return = None
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        flexmock(IncidentExternalSolution).should_receive('query.filter.first').and_return(external_solution)

        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)

        flexmock(controller).should_receive('validate_capability').and_return(True)

        flexmock(db.session).should_receive('commit')

        returned = controller.unpin_external_solution(
            user, datasource_uuid, incidenttype_id, incidentextsolution_id)
        assert returned == should_return

    def test__get_user_likes_dict(self):
        user = unit_test_fixtures.user
        user_id = user.id
        incident_solution = unit_test_fixtures.incident_solution
        should_return = None

        flexmock(IncidentSolution).should_receive('query.filter.update')

        returned = controller._get_user_likes_dict(user_id, incident_solution)
        assert returned == should_return

        # with likes
        incident_solution.user_likes = json.dumps([{'user_id': user_id}])
        should_return = {'user_id': 1}

        returned = controller._get_user_likes_dict(user_id, incident_solution)
        assert returned == should_return

    def test__update_user_likes(self):
        user = unit_test_fixtures.user
        user_id = user.id
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        your_like = True
        should_return = {'liked': True, 'user_id': 1}

        flexmock(IncidentSolution).should_receive('query.filter.update')

        returned = controller._update_user_likes(user_id, incident_solution, your_like)
        assert returned == should_return

        # previous liked
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        incident_solution.user_likes = json.dumps([{'user_id': 2}])
        your_like = True
        should_return = {'liked': True, 'user_id': 1}

        flexmock(IncidentSolution).should_receive('query.filter.update')

        returned = controller._update_user_likes(user_id, incident_solution, your_like)
        assert returned == should_return

    def test_like_solution_dict(self):
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        incident_solution.user_likes = json.dumps([{'user_id': 2}])
        user_like = {'liked': True, 'user_id': 1}
        should_return = unit_test_fixtures.incident_solution_dict
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        returned = controller.like_solution_dict(incident_solution, user_like)
        assert returned == should_return

    def test_like_incident_solution(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        solution_dict = copy.deepcopy(unit_test_fixtures.incident_solution_dict)
        body = {'liked': True}
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        flexmock(IncidentSolution).should_receive('query.filter.first')\
            .and_return(None)

        try:
            controller.like_incident_solution(user, datasource_uuid,
                                              incidenttype_id, body)
        except error.BadRequest:
            pass

        flexmock(IncidentSolution).should_receive('query.filter.first')\
            .and_return(incident_solution)

        flexmock(controller).should_receive('publish_message').and_return(False)

        flexmock(controller).should_receive('like_solution_dict').and_return(solution_dict)

        # no liked
        user_like = {'liked': False, 'user_id': 1}

        flexmock(controller).should_receive('_get_user_likes_dict').and_return(user_like)

        flexmock(controller).should_receive('_update_user_likes').and_return(user_like)

        should_return = {'liked': False, 'total_likes': 2, 'user_id': 1}

        returned = controller.like_incident_solution(user, datasource_uuid,
                                                     incidenttype_id, body)
        assert returned == should_return

        # no liked
        body = {'liked': False}
        user_like = {'liked': True, 'user_id': 2}

        flexmock(controller).should_receive('_get_user_likes_dict').and_return(user_like)

        flexmock(controller).should_receive('_update_user_likes').and_return(user_like)

        should_return = {'liked': True, 'total_likes': 1, 'user_id': 2}

        returned = controller.like_incident_solution(user, datasource_uuid,
                                                     incidenttype_id, body)
        assert returned == should_return

        # no liked
        body = {'liked': False}
        user_like = {}

        flexmock(controller).should_receive('_get_user_likes_dict').and_return(user_like)

        flexmock(controller).should_receive('_update_user_likes').and_return(user_like)

        should_return = {'liked': None, 'total_likes': 0, 'user_id': None}

        returned = controller.like_incident_solution(user, datasource_uuid,
                                                     incidenttype_id, body)
        assert returned == should_return

    def test_get_incident_solution(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        incident_solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.filter.first').and_return(incident_type)

        should_return = {
            'incidentsolution_id': None,
            'it_id': 1,
            'incidenttype_id': 1,
            'incidenttype_id_saio': 1,
            'solution_likes': 0,
            'steps': '',
            'user_like': None,
            'actions': '',
            'description': '',
            'files': [], 
            'flags': [],
            'liked': None, 
            'total_likes': 0, 
            'user_id': None,
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
            }

        flexmock(controller).should_receive('validate_capability').and_return(False)

        try:
            controller.get_incident_solution(user, datasource_uuid,
                                             incidenttype_id)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(True)
        flexmock(utils).should_receive('incident_solution_to_dict').and_return({})

        # No solution
        flexmock(IncidentSolution).should_receive('query.filter.first')\
            .and_return(None)

        returned = controller.get_incident_solution(user, datasource_uuid,
                                                    incidenttype_id)
        assert returned == should_return

        # Solution
        user_like = {}
        should_return = {
            'actions': ['api here'],
            'incidenttype_id': 1,
            'it_id': 1,
            'files': [],
            'flags': None,
            'liked': None,
            'total_likes': 1,
            'user_id': None,
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
            }

        flexmock(controller).should_receive('_get_user_likes_dict').and_return(user_like)

        flexmock(IncidentSolution).should_receive('query.filter.first')\
            .and_return(incident_solution)

        flexmock(controller).should_receive('get_incident_flags').and_return(None)

        returned = controller.get_incident_solution(user, datasource_uuid,
                                                    incidenttype_id)
        assert returned == should_return

    def test_get_shared_solutions(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        log_archetype = unit_test_fixtures.log_category
        archetypes = [log_archetype.log_archetype]
        anonymized_archetypes = log_archetype
        token = 'token'
        solution = {
            'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
            'flags': None,
            'incidentsolution_id': 1,
            'incidenttype_id': 1,
            'solution_text': list('some text'.encode()),
            'solution_likes': 1,
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'}

        should_return = {'shared_solutions': []}

        flexmock(controller).should_receive('validate_capability').and_return(False)

        try:
            controller.get_shared_solutions(user, datasource_uuid,
                                            incidenttype_id, token)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(True)

        flexmock(controller).should_receive('get_incidenttype_archetypes').and_return(archetypes)

        flexmock(proctor_controller).should_receive('anonymize_archetypes')\
            .and_return(anonymized_archetypes)

        flexmock(utils).should_receive('search_solution').and_return(json.dumps([solution]))

        should_return = {
            'shared_solutions': [
                {
                    'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
                    'flags': None,
                    'incidentsolution_id': 1,
                    'incidenttype_id': 1,
                    'solution_likes': 1,
                    'solution_text': 'some text',
                    'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'}]}

        returned = controller.get_shared_solutions(user, datasource_uuid, incidenttype_id, token)
        assert returned == should_return

    def test_put_incident_solution_saio(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        file = unit_test_fixtures.file
        authorization_saio = unit_test_fixtures.authorization_saio
        solution = {
            'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
            'flags': None,
            'incidentsolution_id': 1,
            'incidenttype_id': 1,
            'solution_text': list('some text'.encode()),
            'solution_likes': 1,
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'}

        shold_return = solution

        flexmock(controller).should_receive('authenticate_saio').\
            and_return(authorization_saio)

        flexmock(controller).should_receive('create_object_storage_saio')

        flexmock(controller).should_receive('add_file_saio.__dict__').\
            and_return(unit_test_fixtures.status_code_201)

        flexmock(controller).should_receive('update_incident_solution').\
            and_return(solution)

        returned = controller.put_incident_solution_saio(user, datasource_uuid,
                                                         incidenttype_id, file)
        assert returned == shold_return

    def test_delete_incident_solution_saio(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        file = unit_test_fixtures.file
        filename = file.filename
        authorization_saio = unit_test_fixtures.authorization_saio
        solution = {
            'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
            'flags': None,
            'incidentsolution_id': 1,
            'incidenttype_id': 1,
            'solution_text': list('some text'.encode()),
            'solution_likes': 1,
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'}

        should_return = solution

        flexmock(controller).should_receive('authenticate_saio').\
            and_return(authorization_saio)

        flexmock(controller).should_receive('delete_file_saio')

        flexmock(controller).should_receive('update_incident_solution').\
            and_return(solution)

        returned = controller.delete_incident_solution_saio(
            user, datasource_uuid, incidenttype_id, filename)
        assert returned == should_return

    def test_download_incident_solution_file_saio(self):
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        incidenttype_id = 1
        file = unit_test_fixtures.file
        filename = file.filename
        Config.LOCATION = 'http://cerebro-swift:80'
        should_return = f'{Config.LOCATION}/swift/v1/AUTH_cerebro/e199ac5c-ee7d-4d73-bb61-ab2b48425adf_incident_type_1/filex.txt'

        returned = controller.download_incident_solution_file_saio(
            datasource_uuid, incidenttype_id, filename)

        assert returned == should_return

        Config.LOCATION = None


if __name__ == '__main__':
    unittest.main()
