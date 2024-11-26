import ast
import copy
import datetime
import json
import os
import pytz
import unittest
from unittest import TestCase
from unittest.mock import patch

import mock
import pytest
from flexmock import flexmock
import smarty.errors as error

from sqlalchemy import desc
from sqlalchemy.orm.query import Query
from sqlalchemy import exc

import smarty.errors
import smarty.serialization.proctor as proctor
from smarty.app import create_app
from smarty.alerts import controller as alerts_controller
from smarty.data_sources import controller as ds_controller
from smarty.domain.models import CategoryOccurrences
from smarty.domain.models import DataSource
from smarty.domain.models import ElasticSearchStatus
from smarty.domain.models import Environment
from smarty.domain.models import ESHourStatus
from smarty.domain.models import Fingerprint
from smarty.domain.models import Incident
from smarty.domain.models import IncidentResponse
from smarty.domain.models import IncidentRule
from smarty.domain.models import IncidentType
from smarty.domain.models import LogCategory
from smarty.domain.models import ProctorModel
from smarty.domain.models import ProctorTrainingData
from smarty.domain.models import Signature
from smarty.domain.models import user_datastore
from smarty.extensions import db
from smarty.health_desk import controller as hd_controller
from smarty.health_desk import utils as hd_utils
from smarty.incidents import controller as incidents_controller
from smarty.incidents import utils as incidents_utils
from smarty.proctor import controller
from smarty.proctor import utils
from smarty.solutions import controller as sol_controller
from smarty.settings import Config
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

    def test_get_proctor_models(self):
        model = unit_test_fixtures.proctor_model
        models = [model]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        except_proctormodel_id = 1
        query = Query

        flexmock(ProctorModel).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('filter').and_return(query)

        flexmock(Query).should_receive('all').and_return(models)

        returned = controller.get_proctor_models(datasource_uuid,
                                                 except_proctormodel_id)
        assert returned == models

    def test_create_proctor_model(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        datasource = unit_test_fixtures.data_source
        data = unit_test_fixtures.proctor_model.data.decode()

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')

        flexmock(incidents_controller).should_receive(
            'validate_datasource_uuid').and_return(datasource)

        (flexmock(ProctorModel).should_receive('add').and_return(
            unit_test_fixtures.proctor_model))

        (flexmock(db.session).should_receive('commit').and_return(
            unit_test_fixtures.proctor_model))

        returned = controller.create_proctor_model({'data': data},
                                                   datasource_uuid)
        assert returned

    def test_get_proctor_model(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        model = unit_test_fixtures.proctor_model
        proctormodel_id = model.proctormodel_id
        query = Query

        flexmock(ProctorModel).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('filter.first').and_return(model)

        returned = controller.get_proctor_model(proctormodel_id,
                                                datasource_uuid)
        assert returned == unit_test_fixtures.proctor_model_dict

        proctormodel_id = 0

        flexmock(Query).should_receive('filter.order_by.first').and_return(
            model)

        returned = controller.get_proctor_model(proctormodel_id,
                                                datasource_uuid)
        assert returned == unit_test_fixtures.proctor_model_dict

    def test_delete_proctor_model(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        model = unit_test_fixtures.proctor_model
        proctormodel_id = model.proctormodel_id

        flexmock(IncidentType).should_receive('query.filter.count').and_return(
            0)

        # no model
        flexmock(ProctorModel).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.delete_proctor_model(proctormodel_id, datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # exception
        flexmock(ProctorModel).should_receive('query.filter.first').and_return(
            model)

        flexmock(db.session).should_receive('commit').and_raise(Exception)

        flexmock(db.session).should_receive('rollback')

        try:
            controller.delete_proctor_model(proctormodel_id, datasource_uuid)
        except smarty.errors.DeletionFail:
            pass

        flexmock(db.session).should_receive('commit')

        should_return = None
        returned = controller.delete_proctor_model(proctormodel_id,
                                                   datasource_uuid)
        assert returned == should_return

    def test_get_training_data_by_logcategory(self):
        input_df = [1, 2]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        query = Query
        category_occurrence = unit_test_fixtures.category_occurrences
        category_occurrences = [category_occurrence]
        log_category = unit_test_fixtures.log_category

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)

        flexmock(CategoryOccurrences).should_receive(
            'query.filter').and_return(query)

        flexmock(Query).should_receive('filter').and_return(query)

        flexmock(Query).should_receive('all').and_return(category_occurrences)

        returned = controller.get_training_data_by_logcategory(
            input_df, datasource_uuid)
        assert returned == [1]

    def test_delete_training_data_by_logcategory(self):
        log_category = 1
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        category_occurrence = unit_test_fixtures.category_occurrences
        category_occurrences = [category_occurrence]
        log_category = unit_test_fixtures.log_category
        training_datum = unit_test_fixtures.training_datum

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)

        flexmock(ProctorTrainingData).should_receive(
            'query.get').and_return(training_datum)

        flexmock(CategoryOccurrences).should_receive(
            'query.filter.all').and_return(category_occurrences)

        flexmock(db.session).should_receive('commit')

        should_return = [1]
        returned = controller.delete_training_data_by_logcategory(
            log_category, datasource_uuid)
        assert returned == should_return

    def test_query_proctor_data_properties(self):
        body = {}
        query = Query
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = query

        returned = controller.query_proctor_data_properties(
            body, query, datasource_uuid)
        assert returned == should_return

    def test_set_date_epoch_millis(self):
        body = {}
        query = Query
        should_return = query

        returned = controller.set_date_epoch_millis(body, query)
        assert returned == should_return

    def test_get_occurrences_days(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum_1 = copy.deepcopy(unit_test_fixtures.training_datum)
        training_datum_2 = copy.deepcopy(unit_test_fixtures.training_datum)
        training_datum_2.end_date = unit_test_fixtures.end_date2
        training_data = [training_datum_1, training_datum_1, training_datum_2]
        incident = unit_test_fixtures.incident
        args = {}

        flexmock(controller).should_receive('filter_own_data')\
            .and_return([unit_test_fixtures.training_datum])

        # no incident
        try:
            controller.get_occurrences_days(user, args, datasource_uuid)
        except error.BadRequest:
            pass

        # no incident
        args = {'incident_id': 1, 'as_calendar': True}

        flexmock(incidents_controller).should_receive(
            'get_incident').and_return(None)

        try:
            controller.get_occurrences_days(user, args, datasource_uuid)
        except error.BadRequest:
            pass

        flexmock(incidents_controller).should_receive(
            'get_incident').and_return(incident)

        flexmock(controller).should_receive('get_training_data').and_return(
            training_data)

        should_return = unit_test_fixtures.occurrence_days
        returned = controller.get_occurrences_days(user, args, datasource_uuid)
        assert list(returned[0]).sort() == list(should_return[0]).sort()

    def test_get_training_data(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident

        flexmock(Incident).should_receive(
            'query.filter.first').and_return(incident)

        flexmock(controller).should_receive('filter_own_data')\
            .and_return([unit_test_fixtures.training_datum])

        flexmock(controller).should_receive('is_role_6').and_return(True)

        # get all data
        (flexmock(ProctorTrainingData).should_receive('query.all').and_return(
            [unit_test_fixtures.training_datum]))

        returned = controller.get_training_data(user, datasource_uuid)
        assert returned == [unit_test_fixtures.training_datum]

        flexmock(controller).should_receive('is_role_6').and_return(False)

        # get all data
        (flexmock(ProctorTrainingData).should_receive('query.all').and_return(
            [unit_test_fixtures.training_datum]))

        returned = controller.get_training_data(user, datasource_uuid)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by start_date
        start_date = {'start_date': unit_test_fixtures.end_date}
        returned = controller.get_training_data(
            user, datasource_uuid, start_date)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by end_date
        end_date = {'end_date': unit_test_fixtures.end_date}
        returned = controller.get_training_data(
            user, datasource_uuid, end_date)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by incident_id
        incident_id = {
            'incident_id': unit_test_fixtures.training_datum.i_id
        }
        returned = controller.get_training_data(
            user, datasource_uuid, incident_id)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by limit
        limit = {'limit': 1}
        returned = controller.get_training_data(user, datasource_uuid, limit)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by offset
        offset = {'offset': 0}
        returned = controller.get_training_data(user, datasource_uuid, offset)
        assert returned == [unit_test_fixtures.training_datum]

        # get data filter by offset
        last = {'last': 1}
        returned = controller.get_training_data(user, datasource_uuid, last)
        assert returned == [unit_test_fixtures.training_datum]

    @patch('requests.delete')
    def test_delete_training_data_task(self, mocked_delete):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}
        should_return = None

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(None)

        flexmock(controller).should_receive('delete_scheduled_training_data')

        returned = controller.delete_training_data_task(
            user, body, datasource_uuid)
        assert returned == should_return

    def test_delete_training_data(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)
        training_data = [training_datum]
        incident = unit_test_fixtures.incident
        incident.occurrences = 0
        body = {}

        flexmock(ds_controller).should_receive('ds_sanitation').and_return([])

        flexmock(controller).should_receive('get_training_data')\
            .and_return(training_data)

        flexmock(controller).should_receive('delete_training_datum')

        flexmock(Incident).should_receive(
            'query.get').and_return(incident)

        flexmock(incidents_controller)\
            .should_receive('update_proctor_training_entries')\
            .and_return(incident)

        flexmock(incidents_controller).should_receive('delete_incident')

        flexmock(db.session).should_receive('commit')

        flexmock(incidents_controller).should_receive('sanitation')

        should_return = None
        returned = controller.delete_training_data(user, body, datasource_uuid)
        assert returned == should_return

    @patch('requests.delete')
    def test_delete_scheduled_training_data(self, mocked_delete):
        mocked_delete.return_value = mock.Mock(status_code=204)
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        response = controller.delete_scheduled_training_data(datasource_uuid)

        mocked_delete.assert_called_with(
            'http://cerebro-scheduler:80/scheduler/e199ac5c-ee7d-4d73-bb61-ab2b48425adf/data_retention'
        )

    def test__split_logs_by_category(self):
        logcategories = [4]
        data = json.dumps(unit_test_fixtures.raw_logs)

        should_return = unit_test_fixtures.log_by_category
        returned = controller._split_logs_by_category(logcategories, data)
        assert returned == should_return

    def test__logcategory_seen_at_incident_type(self):
        logcategories = [4]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        incident_types = [incident_type]

        flexmock(incidents_controller).should_receive(
            'get_incident_types').and_return(incident_types)

        should_return = {4: 0}
        returned = controller._logcategory_seen_at_incident_type(
            logcategories, datasource_uuid)
        assert returned == should_return

    def test__combine_logs_by_incident_type(self):
        incident_types = [1]
        logcategory_seen_at_incident_type = {}
        split_logs_by_category = {}

        should_return = {1: []}
        returned = controller._combine_logs_by_incident_type(
            incident_types, logcategory_seen_at_incident_type,
            split_logs_by_category)
        assert returned == should_return

    def test__sort_logs(self):
        logs = unit_test_fixtures.raw_logs
        should_return = logs

        returned = controller._sort_logs(logs)
        assert returned == should_return

        logs = unit_test_fixtures.raw_logs_2
        should_return = logs

        returned = controller._sort_logs(logs)
        assert returned == should_return

    def test__incident_name(self):
        sequence = [4]
        logs = unit_test_fixtures.raw_logs
        should_return = 'nova-compute - logging_exception_prefix    '

        returned = controller._incident_name(sequence, logs)
        assert returned == should_return

    def test__extract_parameters(self):
        logs = unit_test_fixtures.raw_logs
        should_return = {
            'category_occurrences': {4: 1},
            'cerebro_commands': {},
            'hosts': {'controller002'},
            'loggers': {'openstack.nova'},
            'program_name': {'Unknown'},
            'sequence': [4]
        }

        returned = controller._extract_parameters(logs)
        assert returned == should_return

    def test_create_new_it_and_i(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        incident = copy.deepcopy(unit_test_fixtures.incident)
        payload = {}
        should_return = incident_type, incident

        flexmock(incidents_controller).should_receive('create_incident_type')\
            .and_return(incident_type)

        flexmock(controller).should_receive('create_new_incident')\
            .and_return(incident)

        returned = controller.create_new_it_and_i(
            user, payload, datasource_uuid)
        assert returned == should_return

    def test_find_incident(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        environment_id = 1
        incident_type = unit_test_fixtures.incident_type
        incident = copy.deepcopy(unit_test_fixtures.incident)
        should_return = incident
        payload = {
            'incident_type': incident_type,
            'environment_id': environment_id
        }

        flexmock(Incident).should_receive(
            'query.filter.all').and_return([incident])

        returned = controller.find_incident(user, payload, datasource_uuid)
        assert returned == should_return

        flexmock(Incident).should_receive(
            'query.filter.all').and_return([incident, incident])

        returned = controller.find_incident(user, payload, datasource_uuid)
        assert returned == should_return

        flexmock(Incident).should_receive('query.filter.all').and_return([])

        flexmock(controller).should_receive('create_new_incident')\
            .and_return(incident)

        returned = controller.find_incident(user, payload, datasource_uuid)
        assert returned == should_return

    def test_create_new_incident(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        payload = {}
        incident = unit_test_fixtures.incident
        should_return = incident

        flexmock(incidents_controller).should_receive('create_incident')\
            .and_return(incident)

        returned = controller.create_new_incident(
            user, ds_uuid, incident_type, payload)
        assert returned == should_return

    def test__split_logs_by_it(self):
        logs = unit_test_fixtures.logs
        incident_types = [unit_test_fixtures.incident_type]
        should_return = unit_test_fixtures.splited_logs

        returned = controller._split_logs_by_it(logs, incident_types)
        assert returned == should_return

    def test_split_training_datum(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = unit_test_fixtures.training_datum_split
        incident_type = unit_test_fixtures.incident_type
        should_return = None

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')
        flexmock(incidents_controller).should_receive(
            'check_environment_status')
        flexmock(incidents_controller).should_receive(
            'get_incident_types').and_return([incident_type])
        flexmock(controller).should_receive('create_training_datum')

        returned = controller.split_training_datum(user, body, ds_uuid)
        assert returned == should_return

    def test_create_training_datum(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        model = copy.deepcopy(unit_test_fixtures.proctor_model)
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)
        logs = copy.deepcopy(unit_test_fixtures.raw_logs)
        incident = copy.deepcopy(unit_test_fixtures.incident)
        data = training_datum.data
        predicted_label = training_datum.predicted_label
        input_df = training_datum.input_df

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.order_by.first')
        flexmock(incidents_controller).should_receive(
            'check_datasource_status').and_return(data_source)
        flexmock(incidents_controller).should_receive(
            'check_environment_status')
        flexmock(incidents_controller).should_receive(
            'get_incident_types').and_return([incident_type])
        flexmock(ProctorModel).should_receive(
            'query.filter.first').and_return(model)
        flexmock(controller).should_receive(
            '_incident_name').and_return(incident.name)
        flexmock(controller).should_receive(
            'find_incident').and_return(incident)
        flexmock(controller).should_receive(
            'create_training_data_category_amount')
        flexmock(controller).should_receive(
            '_split_logs_by_category').and_return()
        flexmock(controller).should_receive(
            '_logcategory_seen_at_incident_type').and_return({1: 1})
        flexmock(controller).should_receive(
            '_combine_logs_by_incident_type').and_return({1: logs})
        flexmock(controller).should_receive(
            'handle_existing_incident').and_return(incident, predicted_label)
        flexmock(ProctorTrainingData).should_receive('add')
        flexmock(db.session).should_receive('commit')
        flexmock(controller).should_receive(
            'create_training_data_category_occurrence')
        flexmock(alerts_controller).should_receive('alerts')
        flexmock(incidents_controller).should_receive('update_incident')

        body = {
            'input_df': json.dumps([1]),
            'data': json.dumps(logs),
            'label_prediction': json.dumps(['label 1', 'label 2', 'label 3']),
            'logger': json.dumps(['openstack.nova'])
        }
        returned = controller.create_training_datum(user, body,
                                                    datasource_uuid)
        assert returned.data == data

    def test_create_training_data_category_amount(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = unit_test_fixtures.training_datum
        input_df = unit_test_fixtures.input_df_str
        log_category = unit_test_fixtures.log_category
        category_occurrences = unit_test_fixtures.category_occurrences
        should_return = None

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)
        flexmock(CategoryOccurrences).should_receive(
            'add').and_return(category_occurrences)
        flexmock(db.session).should_receive('rollback')

        returned = controller.create_training_data_category_amount(
            datasource_uuid, training_datum, input_df)
        assert returned == should_return

    def test_update_attachments(self):
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        logs_hd = unit_test_fixtures.logs_hd
        new_att = 'new_att'
        should_return = logs_hd

        flexmock(sol_controller).should_receive(
            'put_attachment_saio').and_return(new_att)

        returned = controller.update_attachments(ds_uuid, logs_hd)
        assert returned == should_return

    def test_create_training_datum_hd(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = unit_test_fixtures.hd_log_1
        hd_log_by_category = unit_test_fixtures.hd_log_by_category
        model = unit_test_fixtures.proctor_model
        hd_parameters = unit_test_fixtures.hd_parameters
        incident = unit_test_fixtures.incident
        training_datum = unit_test_fixtures.training_datum
        should_return = b'[]'

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')
        flexmock(controller).should_receive(
            '_split_logs_by_category').and_return(hd_log_by_category)
        flexmock(controller).should_receive(
            '_logcategory_seen_at_incident_type').and_return({944: 944})
        flexmock(controller).should_receive(
            '_combine_logs_by_incident_type').and_return(hd_log_by_category)
        flexmock(ProctorModel).should_receive(
            'query.filter.first').and_return(model)
        flexmock(controller).should_receive(
            '_extract_parameters').and_return(hd_parameters)
        flexmock(controller).should_receive(
            'update_attachments').and_return([])
        flexmock(controller).should_receive(
            'handle_existing_incident').and_return(incident, 'Unknown')
        flexmock(ProctorTrainingData).should_receive(
            'query.filter.order_by.first').and_return(training_datum)
        flexmock(ProctorTrainingData).should_receive(
            'add').and_return(training_datum)
        flexmock(controller).should_receive(
            'create_training_data_category_occurrence')
        flexmock(controller).should_receive('_check_extras')
        flexmock(hd_controller).should_receive('get_incident_response')

        returned = controller.create_training_datum_hd(user, body, ds_uuid)
        assert returned.data == should_return

    def test__check_extras(self):
        user = unit_test_fixtures.user
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)
        incident = copy.deepcopy(unit_test_fixtures.incident)
        parameters = {'loggers': ['openstack.nova']}
        should_return = None

        flexmock(alerts_controller).should_receive('alerts').and_return(None)

        returned = controller._check_extras(
            user, training_datum, incident, parameters)
        assert returned == should_return

    def test_update_training_datum_hd(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {
            'data': json.dumps([{
                'subject': 'subject',
                'Logger': 'email@domain.ext'
            }])
        }
        incident = unit_test_fixtures.incident
        should_return = None

        flexmock(controller).should_receive(
            '_get_incident').and_return(incident)
        flexmock(controller).should_receive(
            'update_by_incident').and_return(None)
        flexmock(controller).should_receive(
            '_apply_escalation_policy').and_return(None)
        flexmock(controller).should_receive(
            '_openai_reply_as_internal_msg').and_return(None)

        returned = controller.update_training_datum_hd(
            user, body, datasource_uuid)
        assert returned == should_return

    def test_update_by_incident(self):
        user = unit_test_fixtures.user
        incident = unit_test_fixtures.incident
        incident_dict = copy.deepcopy(unit_test_fixtures.incident_dict)
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_response = unit_test_fixtures.incident_response
        incident_report = unit_test_fixtures.incident_report
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        training_datum = unit_test_fixtures.training_datum
        training_datum_dict = copy.deepcopy(
            unit_test_fixtures.training_datum_dict)
        data_source = unit_test_fixtures.data_source_hd
        body = {
            'input_df': json.dumps([1]),
            'data': json.dumps([{
                'subject': 'subject',
                '@timestamp': '2018-09-03T12:20:47.112000000+00:00'
            }])
        }
        should_return = training_datum

        flexmock(incidents_controller).should_receive(
            'update_incident').and_return(incident)
        flexmock(hd_controller).should_receive('get_incident_response')\
            .and_return(incident_response, incident_report)
        flexmock(hd_controller).should_receive('update_incident_report')
        flexmock(IncidentType).should_receive(
            'query.get').and_return(incident_type)
        flexmock(ProctorTrainingData).should_receive(
            'query.first').and_return(training_datum)
        flexmock(incidents_controller).should_receive(
            'incident_to_dict').and_return(incident_dict)
        flexmock(incidents_utils).should_receive(
            'notify_current_owner').and_return(True)
        flexmock(controller).should_receive(
            'training_datum_to_dict').and_return(training_datum_dict)
        flexmock(controller).should_receive(
            'update_training_data_category_occurrence')
        flexmock(controller).should_receive(
            'update_attachments').and_return([])
        flexmock(incidents_controller).should_receive('_add_incident_event')
        flexmock(DataSource).should_receive(
            'query.first').and_return(data_source)

        returned = controller.update_by_incident(
            user, incident, body, datasource_uuid)
        assert returned == should_return

    def test_get_raw_logs(self):
        user = unit_test_fixtures.user
        proctortrainingdata_id = 1
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        size = 10
        delta = 1
        training_datum = unit_test_fixtures.training_datum
        should_return = [training_datum]

        flexmock(controller).should_receive(
            'get_training_datum').and_return(training_datum)
        flexmock(controller).should_receive(
            'search_elk').and_return([training_datum])
        flexmock(controller).should_receive(
            '_filter_deos_logs').and_return([training_datum])

        returned = controller.get_raw_logs(
            user, proctortrainingdata_id, datasource_uuid, size, delta)
        assert returned == should_return

    def test_get_scroll(self):
        user = unit_test_fixtures.user
        datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        elk_client = unit_test_fixtures.elk_client
        scroll_id = 'some_scroll_id'
        should_return = unit_test_fixtures.elk_response

        flexmock(controller).should_receive(
            'get_elk_client').and_return(elk_client)
        flexmock(controller).should_receive(
            'scroll_id_logs').and_return(should_return)
        flexmock(controller).should_receive(
            '_filter_deos_logs').and_return(should_return)

        returned = controller.get_scroll(user, datasource_uuid, scroll_id)
        assert returned == should_return

    def test_search_elk(self):
        ds_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        index_name = 'elk-flog-*'
        hostname = 'controller002'
        logger = 'controller'
        timestamp = '2018-09-03T12:20:47.112000000+00:00'
        size = 10
        delta = 1
        elk_client = unit_test_fixtures.elk_client
        should_return = unit_test_fixtures.elk_response

        flexmock(controller).should_receive(
            'get_elk_client').and_return(elk_client)

        flexmock(controller).should_receive(
            'scroll_id_logs').and_return(should_return)

        returned = controller.search_elk(
            ds_uuid, index_name, hostname, logger, timestamp, size, delta)
        assert returned == should_return

    def test_scroll_id_logs(self):
        response = unit_test_fixtures.elk_raw_logs
        should_return = unit_test_fixtures.elk_response_raw

        returned = controller.scroll_id_logs(response)
        assert returned == should_return

    def test_get_common_words(self):
        training_datum = unit_test_fixtures.training_datum
        proctortrainingdata_id = training_datum.proctortrainingdata_id
        data_source = unit_test_fixtures.data_source_hd
        datasource_uuid = data_source.uuid
        should_return = []

        flexmock(DataSource).should_receive(
            'query.first').and_return(data_source)

        flexmock(ProctorTrainingData).should_receive(
            'query.first').and_return(training_datum)

        flexmock(controller).should_receive(
            'extract_common_words').and_return({})

        returned = controller.get_common_words(
            proctortrainingdata_id, datasource_uuid)
        assert returned == should_return

    def test_extract_common_words(self):
        training_datum = unit_test_fixtures.training_datum
        should_return = {}

        flexmock(hd_utils).should_receive(
            'extract_most_common_words').and_return([])

        returned = controller.extract_common_words(training_datum)
        assert returned == should_return

    def test_update_response(self):
        response = {}
        common_words = unit_test_fixtures.common_words
        should_return = unit_test_fixtures.common_words_dict

        returned = controller.update_response(response, common_words)
        assert returned == should_return

    def test_handle_existing_incident(self):
        user = unit_test_fixtures.user
        incident = unit_test_fixtures.incident
        environment = unit_test_fixtures.environment
        incident_type = unit_test_fixtures.incident_type
        predicted_label = 'Unknown'
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        attributes = {
            'incident_info': {
                'env': 1,
                'predicted_label': 'predicted_label',
                'incident_name': 'incident_name',
                'end_date': 'end_date'
            }
        }

        flexmock(Environment).should_receive('query.get').and_return(
            environment)

        flexmock(incidents_controller).should_receive(
            'get_incident_type').and_return(incident_type)

        flexmock(incidents_controller).should_receive(
            'get_incidents').and_return([])

        flexmock(incidents_controller).should_receive(
            'create_incident').and_return(incident)

        should_return = incident, predicted_label
        returned = controller.handle_existing_incident(user, attributes,
                                                       datasource_uuid)
        assert returned == should_return

    def test_get_training_datum(self):
        training_datum = unit_test_fixtures.training_datum
        proctortrainingdata_id = training_datum.proctortrainingdata_id
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        (flexmock(ProctorTrainingData).should_receive(
            'query.first').and_return(training_datum))

        returned = controller.get_training_datum(proctortrainingdata_id,
                                                 datasource_uuid)
        assert returned == training_datum

    def test_get_display_logs(self):
        user = unit_test_fixtures.user
        data_sources = [unit_test_fixtures.data_source]
        envs = [unit_test_fixtures.environment]
        size = 5
        pit = 1500000
        hostname = 'hostname'
        should_return = {}

        flexmock(DataSource).should_receive(
            'query.filter.all').and_return(data_sources)
        flexmock(Environment).should_receive(
            'query.filter.all').and_return(envs)
        flexmock(controller).should_receive('search_display').and_return({})

        returned = controller.get_display_logs(user, size, pit, hostname, True)
        assert returned == should_return

    def test_get_indexes(self):
        env = unit_test_fixtures.environment
        incidents = [unit_test_fixtures.incident]
        hayei_envs = [
            {
                'environment': env
            }
        ]
        should_return = [{'uat_cluster:flog-*': {'controller001'}}]

        flexmock(Incident).should_receive(
            'query.filter.distinct').and_return(incidents)

        returned = controller.get_indexes(hayei_envs)
        assert returned == should_return

    def test_search_display(self):
        user = unit_test_fixtures.user
        elk_client = copy.deepcopy(unit_test_fixtures.elk_client)
        elk_client.search = {}
        ds_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        index_name = 'uat_cluster:flog-*'
        hostname = 'hostname'
        size = 5
        pit = 15000000
        should_return = {'elk_connection': 'Bad', 'fluentd_connection': 'Bad'}

        flexmock(controller).should_receive(
            'get_elk_client').and_return(elk_client)

        returned = controller.search_display(
            user, ds_uuid, index_name, hostname, size, pit)
        assert returned == should_return

    def test_pit_logs(self):
        response = unit_test_fixtures.elk_raw_logs
        response['elk_connection'] = 'Good'
        response['fluentd_connection'] = 'Good'
        should_return = {
            'datetime': datetime.datetime.utcfromtimestamp(1627392899948/1000).replace(
                tzinfo=pytz.utc).strftime('%Y-%m-%d %H:%M:%S %Z%z'),
            'elk_connection': 'Good',
            'fluentd_connection': 'Good',
            'logs': {'sublime': []},
            'loggers': ['sublime'],
            'pit': 1627392899948
        }

        returned = controller.pit_logs(response, True)
        assert returned == should_return

    def test_delete_training_datum(self):
        training_datum = unit_test_fixtures.training_datum
        proctortrainingdata_id = training_datum.proctortrainingdata_id
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        log_category = unit_test_fixtures.log_category
        should_return = None

        flexmock(ProctorTrainingData).should_receive('query.first').\
            and_return(training_datum)

        flexmock(CategoryOccurrences).should_receive('query.all').\
            and_return([log_category])

        returned = controller.delete_training_datum(
            training_datum, datasource_uuid)
        assert returned == should_return

    @patch('requests.post')
    def test__create_training_datum(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        new_logs = unit_test_fixtures.raw_logs

        response = controller.create_new_training_datum(new_logs)

        mocked_post.assert_called_with(
            'http://cerebro-proctor:80/proctor/new_training_datum',
            json={
                'sequence': json.dumps(new_logs),
                'label': None
            })
        self.assertEqual(response.status_code, 200)

    def test__split_training_data(self):
        training_datum = unit_test_fixtures.training_datum
        new_logs = unit_test_fixtures.raw_logs
        should_return = json.dumps(
            ast.literal_eval(training_datum.data.decode()))

        # index mismatch
        index = json.dumps([1, 1])

        returned_logs, returned_index = controller._split_training_data(
            index, training_datum)
        assert returned_logs == should_return
        assert len(returned_index) != len(index)

        # expected behavior
        index = json.dumps([1])

        returned_logs, returned_index = controller._split_training_data(
            index, training_datum)
        assert returned_logs == should_return
        assert returned_index == index

        # expected behavior, creating new logs
        index = json.dumps([0])
        should_return = unit_test_fixtures.response_201
        empty_response = unit_test_fixtures.empty_response

        (flexmock(controller).should_receive('create_new_training_datum').
         with_args(new_logs).and_return(should_return))

        returned_logs, returned_index = controller._split_training_data(
            index, training_datum)
        assert returned_logs == empty_response
        assert returned_index == empty_response

    def test_update_training_data_blob(self):
        training_data = unit_test_fixtures.training_datum
        trainingdata_id = training_data.proctortrainingdata_id
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        # trying to update no existing training data
        (flexmock(ProctorTrainingData).should_receive(
            'query.first').and_return(None))

        try:
            controller.update_training_data_blob(datasource_uuid,
                                                 trainingdata_id)
        except smarty.errors.NoSuchObject:
            pass

        # no update
        (flexmock(ProctorTrainingData).should_receive(
            'query.first').and_return(training_data))

        returned = controller.update_training_data_blob(
            datasource_uuid, trainingdata_id)
        assert returned == training_data

        # data_blob update
        data_blob = unit_test_fixtures.data_str
        returned = controller.update_training_data_blob(datasource_uuid,
                                                        trainingdata_id,
                                                        data_blob=data_blob)
        assert returned == training_data

        # label update
        label = unit_test_fixtures.training_datum.predicted_label
        returned = controller.update_training_data_blob(datasource_uuid,
                                                        trainingdata_id,
                                                        label=label)
        assert returned == training_data

        # incident_id update
        incident_id = unit_test_fixtures.training_datum.i_id
        returned = controller.update_training_data_blob(
            datasource_uuid, trainingdata_id, incident_id=incident_id)
        assert returned == training_data

        # input_df update
        input_df = unit_test_fixtures.input_df_str
        returned = controller.update_training_data_blob(datasource_uuid,
                                                        trainingdata_id,
                                                        input_df=input_df)
        assert returned == training_data

        # index update
        index = json.dumps([1])
        updated_data = json.dumps(ast.literal_eval(
            training_data.data.decode()))
        updated_input_df = json.dumps([1])

        (flexmock(controller).should_receive('_split_training_data').with_args(
            index, training_data).and_return(updated_data, updated_input_df))

        returned = controller.update_training_data_blob(datasource_uuid,
                                                        trainingdata_id,
                                                        index=index)
        assert returned == training_data

    def test_get_log_categories(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(LogCategory).should_receive('query.all').and_return(
            [unit_test_fixtures.log_category])
        flexmock(LogCategory).should_receive(
            'query.first').and_return(unit_test_fixtures.log_category)
        flexmock(utils).should_receive('get_openai_details').and_return(None)
        flexmock(utils).should_receive('get_openai_solution').and_return(None)
        flexmock(utils).should_receive('get_openai_reaction').and_return(None)

        returned = controller.get_log_categories(
            datasource_uuid=datasource_uuid)
        assert returned == [unit_test_fixtures.log_category_dict]

    def test_get_log_category(self):
        logcategory_id = unit_test_fixtures.log_category.logcategory_id
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(LogCategory).should_receive(
            'query.first').and_return(unit_test_fixtures.log_category)
        flexmock(utils).should_receive('get_openai_details').and_return('')
        flexmock(utils).should_receive('get_openai_solution').and_return('')
        flexmock(utils).should_receive('get_openai_reaction').and_return('')

        returned = controller.get_log_category(logcategory_id,
                                               datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.log_category_dict

    def test_update_log_category(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        log_category = unit_test_fixtures.log_category
        category_id = log_category.logcategory_id
        body = {'key': 'value'}
        should_return = unit_test_fixtures.log_category_dict

        flexmock(LogCategory).should_receive(
            'query.first').and_return(log_category)
        flexmock(utils).should_receive('get_openai_details').and_return(None)
        flexmock(utils).should_receive('get_openai_solution').and_return(None)
        flexmock(utils).should_receive('get_openai_reaction').and_return(None)

        returned = controller.update_log_category(
            category_id, body, datasource_uuid)
        assert returned == should_return

    def test_create_log_category(self):
        log_category = unit_test_fixtures.log_category
        log_archetype = log_category.log_archetype
        logger = log_category.logger
        signature = unit_test_fixtures.signature
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        current_user = unit_test_fixtures.proctor
        query = Query

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')

        flexmock(LogCategory).should_receive('query.filter').and_return(query)
        flexmock(Query).should_receive('first').and_return(None)
        flexmock(Signature).should_receive('add').and_return(
            unit_test_fixtures.signature_db)
        flexmock(LogCategory).should_receive('query.filter').and_return(query)
        flexmock(Query).should_receive('order_by.first').and_return(None)
        flexmock(LogCategory).should_receive('add').and_return(
            unit_test_fixtures.log_category)
        flexmock(db.session).should_receive('commit')
        flexmock(utils).should_receive('get_openai_details').and_return(None)
        flexmock(utils).should_receive('get_openai_solution').and_return(None)
        flexmock(utils).should_receive('get_openai_reaction').and_return(None)
        flexmock(utils).should_receive('_get_tags').and_return(None)

        returned_la = controller.create_log_category(
            current_user, {
                'log_archetype': log_archetype,
                'logger': logger,
                'signature': signature.__dict__
            },
            datasource_uuid=datasource_uuid)

        assert returned_la['log_archetype'] == log_archetype

    def test_delete_category(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        log_category = copy.deepcopy(unit_test_fixtures.log_category)
        signature = copy.deepcopy(unit_test_fixtures.signature)
        category_id = 1
        should_return = None

        (flexmock(LogCategory).should_receive('query.first').and_return(
            log_category))

        (flexmock(Signature).should_receive('query.get').and_return(
            signature))

        returned = controller.delete_category(datasource_uuid, category_id)
        assert returned == should_return

    def test_delete_log_category(self):
        user = unit_test_fixtures.user
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_types = [incident_type]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        category_id = '1'
        should_return = None

        flexmock(incidents_controller).should_receive(
            'get_incident_types').and_return(incident_types)

        flexmock(incidents_controller).should_receive('delete_incident_type')

        flexmock(controller).should_receive(
            'delete_training_data_by_logcategory')

        flexmock(controller).should_receive('delete_category')

        returned = controller.delete_log_category(
            user, category_id, datasource_uuid)
        assert returned == should_return

    def test_delete_duplicated_categories(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {'duplicated_categories': [1]}
        should_return = None

        returned = controller.delete_duplicated_categories(
            user, body, datasource_uuid)
        assert returned == should_return

    def test_get_signatures(self):
        should_return = []

        flexmock(Signature).should_receive('query.all').and_return([])

        returned = controller.get_signatures()
        assert returned == should_return

    def test_get_signature(self):
        signature_id = 1
        should_return = None

        flexmock(Signature).should_receive('query.get')

        returned = controller.get_signature(signature_id)
        assert returned == should_return

    @patch('requests.post')
    def test_create_text_signature(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        error_log = 'some text'

        response = controller.create_text_signature(error_log)

        mocked_post.assert_called_with(
            'http://cerebro-proctor:80/proctor/text_signature',
            json={'error_log': 'some text'}
        )
        self.assertEqual(response.status_code, 200)

    def test_get_fingerprints(self):
        should_return = []

        flexmock(Fingerprint).should_receive('query.all').and_return([])

        returned = controller.get_fingerprints()
        assert returned == should_return

    def test_get_fingerprint(self):
        fingerprint = unit_test_fixtures.fingerprint
        fingerprint_type = 'some text'
        should_return = unit_test_fixtures.fingerprint_dict

        flexmock(Fingerprint).should_receive(
            'query.get').and_return(fingerprint)

        returned = controller.get_fingerprint(fingerprint_type)
        assert returned == should_return

    def test_create_fingerprint(self):
        body = copy.deepcopy(unit_test_fixtures.fingerprint_dict)
        should_return = copy.deepcopy(unit_test_fixtures.fingerprint_dict)

        flexmock(Fingerprint).should_receive('add').and_return(
            unit_test_fixtures.log_category)

        returned = controller.create_fingerprint(body)
        assert returned == should_return

    def test_patch_fingerprint(self):
        fingerprint_type = 'email'
        fingerprint = copy.deepcopy(unit_test_fixtures.fingerprint)
        fingerprint_body = {}
        should_return = copy.deepcopy(unit_test_fixtures.fingerprint_dict)

        flexmock(Fingerprint).should_receive(
            'query.get').and_return(fingerprint)

        returned = controller.patch_fingerprint(
            fingerprint_type, fingerprint_body)
        assert returned == should_return

    @patch('requests.post')
    def test_anonymize_archetypes(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = 200
        log_category = unit_test_fixtures.log_category
        log_categories = [log_category]

        response = controller.anonymize_archetypes(log_categories)

        mocked_post.assert_called_with(
            'http://cerebro-proctor:80/proctor/anonymize_archetypes',
            json={
                'archetypes': '["got incomplete line before first line from /var/log/kolla/gnocchi/gnocchi-metricd.log: \\"2018-08-31 18:24:59,847 [127] ERROR    gnocchi.cli.metricd: Unexpected error updating the task partitioner: Unknown node `c5af8341-c8e6-4a7a-b1ab-7a7bbc3fe507\'\\\\n\\""]'}
        )
        self.assertEqual(response, 200)

    def test_create_training_data_category_occurrence(self):
        category_occurrences = unit_test_fixtures.category_occurrences
        trainingdata_id = category_occurrences.ptd_id
        logcategory_ids = [1, 1]
        occurrences = [1, 1]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        log_category = unit_test_fixtures.log_category
        training_datum = unit_test_fixtures.training_datum

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.first').and_return(training_datum)

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')

        (flexmock(CategoryOccurrences).should_receive('add').and_return(
            category_occurrences))

        (flexmock(db.session).should_receive('commit').and_return(
            category_occurrences))

        returned = controller.create_training_data_category_occurrence(
            trainingdata_id=trainingdata_id,
            logcategory_ids=logcategory_ids,
            occurrences=occurrences,
            datasource_uuid=datasource_uuid)
        for idx, item in enumerate(returned):
            assert item.ptd_id == trainingdata_id
            assert item.lc_id == logcategory_ids[idx]
            assert item.occurrences == occurrences[idx]

    def test_update_training_data_category_occurrence(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = unit_test_fixtures.training_datum
        logcategories = [1, 1]
        category_occurrences = unit_test_fixtures.category_occurrences
        should_return = None

        flexmock(CategoryOccurrences).should_receive(
            'query.filter.all').and_return([category_occurrences])
        flexmock(controller).should_receive(
            'create_training_data_category_occurrence')

        returned = controller.update_training_data_category_occurrence(
            datasource_uuid, training_datum, logcategories)
        assert returned == should_return

    def test_get_category_occurrences(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = unit_test_fixtures.training_datum
        category_occurrences = unit_test_fixtures.category_occurrences
        category_occurrences_dict = unit_test_fixtures.category_occurrences_dict
        log_category = unit_test_fixtures.log_category
        query = Query
        incident = unit_test_fixtures.incident
        incident_type = unit_test_fixtures.incident_type

        flexmock(Incident).should_receive(
            'query.filter.first').and_return(incident)

        flexmock(ProctorTrainingData).should_receive('query').and_return(
            query)

        flexmock(Query).should_receive('get').and_return(
            training_datum)

        flexmock(Query).should_receive('filter').and_return(
            query)

        flexmock(Query).should_receive('all').and_return(
            [training_datum])

        flexmock(Query).should_receive('first').and_return(
            training_datum)

        flexmock(controller).should_receive('filter_own_data')\
            .and_return([training_datum])

        flexmock(controller).should_receive('get_training_data')\
            .and_return([training_datum])

        flexmock(CategoryOccurrences).should_receive('query.filter.all')\
            .and_return([category_occurrences])

        flexmock(proctor).should_receive('category_occurrence_to_dict')\
            .and_return(category_occurrences_dict)

        flexmock(LogCategory).should_receive('query.filter.first')\
            .and_return(log_category)

        flexmock(LogCategory).should_receive(
            'query.get').and_return(log_category)

        flexmock(incidents_controller).should_receive(
            'get_incident').and_return(incident)

        flexmock(IncidentType).should_receive(
            'query.get').and_return(incident_type)

        # with incident_id argument
        should_return = {1: {'id': 1}}
        returned = controller.get_category_occurrences(
            incident_id=1, datasource_uuid=datasource_uuid)
        assert returned[1]['id'] == should_return[1]['id']

    def test_filter_own_data(self):
        user = copy.deepcopy(unit_test_fixtures.user)
        user.is_root = False
        user.id = '1'
        associated_training_data = [unit_test_fixtures.training_datum]
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = associated_training_data

        flexmock(controller).should_receive('is_role_6').and_return(False)

        returned = controller.filter_own_data(
            user, associated_training_data, datasource_uuid)
        assert returned == should_return

        flexmock(controller).should_receive('is_role_6').and_return(True)

        returned = controller.filter_own_data(
            user, associated_training_data, datasource_uuid)
        assert returned == []

    def test_is_role_6(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        user = unit_test_fixtures.user
        should_return = True

        flexmock(incidents_controller).should_receive(
            'get_role_id').and_return(6)

        returned = controller.is_role_6(user, datasource_uuid)
        assert returned == should_return

    @patch('requests.post')
    def test__trigger_proctor_update(self, mocked_post):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        mocked_post.return_value = mock.Mock(status_code=200)

        response = controller._trigger_proctor_update(
            datasource_uuid=datasource_uuid)

        mocked_post.assert_called_with(
            f'http://cerebro-proctor:80/proctor/update_rules/{datasource_uuid}'
        )
        self.assertEqual(response.status_code, 200)

    def test_create_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_str = rule.rule

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')

        (flexmock(IncidentRule).should_receive('add').and_return(rule))

        (flexmock(db.session).should_receive('commit').and_return(rule))

        (flexmock(controller).should_receive('_trigger_proctor_update'))

        returned = controller.create_incident_rule(
            rule=rule_str, datasource_uuid=datasource_uuid)
        assert returned.rule == rule_str

    def test_delete_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_id = rule.rule_id

        # testing not existing rule -> empty response
        (flexmock(IncidentRule).should_receive('query.first'))

        try:
            returned = controller.delete_incident_rule(
                rule_id, datasource_uuid=datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # testing well formed rule
        (flexmock(IncidentRule).should_receive('query.first').and_return(rule))

        (flexmock(db.session).should_receive('commit'))

        (flexmock().should_receive('delete'))

        (flexmock(controller).should_receive('_trigger_proctor_update'))

        returned = controller.delete_incident_rule(
            rule_id, datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.none_response

    def test_update_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_id = rule.rule_id
        rule_rule = rule.rule

        # testing not existing rule -> empty response
        (flexmock(IncidentRule).should_receive('query.first'))

        try:
            returned = controller.update_incident_rule(
                rule_id, rule_rule, datasource_uuid=datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # testing well formed rule
        (flexmock(IncidentRule).should_receive('query.first').and_return(rule))

        (flexmock(db.session).should_receive('commit'))

        (flexmock(controller).should_receive('_trigger_proctor_update'))

        returned = controller.update_incident_rule(
            rule_id, rule_rule, datasource_uuid=datasource_uuid)
        assert returned == rule

    def test_get_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_id = rule.rule_id

        (flexmock(IncidentRule).should_receive('query.first').and_return(rule))

        returned = controller.get_incident_rule(
            rule_id, datasource_uuid=datasource_uuid)
        assert returned == rule

    def test_activate_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_id = rule.rule_id

        flexmock(IncidentRule).should_receive('query.first').and_return(rule)

        flexmock(db.session).should_receive('commit')

        returned = controller.activate_rule(rule_id, datasource_uuid)
        assert returned == rule

    def test_deactivate_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = copy.deepcopy(unit_test_fixtures.rule_1)
        rule_id = rule.rule_id

        flexmock(IncidentRule).should_receive('query.first').and_return(rule)

        flexmock(db.session).should_receive('commit')

        returned = controller.deactivate_rule(rule_id, datasource_uuid)
        assert returned == rule

    def test_enable_user_rules(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        inter_relations = ['openstack.nova', 'openstack.neutron']
        rule_index = [1]
        aux_rule = [copy.deepcopy(unit_test_fixtures.rule_1)]
        should_return = None

        flexmock(ds_controller).should_receive('get_only_inter_relations').\
            and_return(inter_relations, rule_index)

        flexmock(ds_controller).should_receive('get_incident_rules').\
            and_return(aux_rule)

        flexmock(controller).should_receive('deactivate_rule')

        flexmock(controller).should_receive('activate_rule')

        returned = controller.enable_user_rules(datasource_uuid)
        assert returned == should_return

    def test_disable_user_rules(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        relations = ['openstack.nova']
        rule_index = [1]
        should_return = None

        flexmock(controller).should_receive('get_inter_relations').\
            and_return(relations, rule_index)

        flexmock(controller).should_receive('deactivate_rule')

        flexmock(controller).should_receive('activate_rule')

        returned = controller.disable_user_rules(datasource_uuid)
        assert returned == should_return

    def test_extract_rule(self):
        loggers_a = ['openstack.nova']
        loggers_b = ['openstack.neutron']
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        aux_rule = [copy.deepcopy(unit_test_fixtures.rule_1)]
        should_return = None

        flexmock(ds_controller).should_receive('get_incident_rules').\
            and_return(aux_rule)

        flexmock(controller).should_receive('activate_rule')

        returned = controller.extract_rule(
            loggers_a, loggers_b, datasource_uuid)
        assert returned == should_return

    def test_check_rule(self):
        loggers = ['openstack.nova']
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        inter_relations = ['openstack.nova', 'openstack.neutron']
        rule_index = [1]
        aux_rule = [copy.deepcopy(unit_test_fixtures.rule_1)]
        should_return = None

        flexmock(ds_controller).should_receive('get_only_inter_relations').\
            and_return(inter_relations, rule_index)

        flexmock(ds_controller).should_receive('get_incident_rules').\
            and_return(aux_rule)

        flexmock(controller).should_receive('deactivate_rule')

        flexmock(controller).should_receive(
            'set_final_rule').and_return(aux_rule[0])

        flexmock(controller).should_receive('activate_rule')

        returned = controller.check_rule(loggers, datasource_uuid)
        assert returned == should_return

    def test_set_final_rule(self):
        idx_to_merge = [1, 2]
        final_rule = unit_test_fixtures.rule_3
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = final_rule

        flexmock(controller).should_receive(
            'update_incident_rule').and_return(final_rule)

        flexmock(controller).should_receive('delete_incident_rule')

        returned = controller.set_final_rule(
            idx_to_merge, final_rule, datasource_uuid)
        assert returned == should_return

    @patch('requests.post')
    def test__check_sequence(self, mocked_post):
        return_value = unit_test_fixtures.check_sequence_response
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = return_value
        input_df = [1, 2, 3]
        should_response = int(return_value['model_id']), int(
            return_value['cluster_id'])
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        response = controller._check_sequence(incident_type, datasource_uuid)
        mocked_post.assert_called_with(
            f'http://cerebro-proctor:80/proctor/check_sequence/{datasource_uuid}',
            json={'input_df': json.dumps(input_df)})
        assert response == should_response

    def test__delete_old_models(self):
        except_proctormodel_id = 0
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        model = [unit_test_fixtures.proctor_model]
        should_return = None

        flexmock(controller).should_receive(
            'get_proctor_models').and_return(model)

        flexmock(controller).should_receive('delete_proctor_model')

        returned = controller._delete_old_models(
            except_proctormodel_id, datasource_uuid)
        assert returned == should_return

    def test__incident_types_to_map(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        model_dict = unit_test_fixtures.proctor_model_dict
        incident_type = unit_test_fixtures.incident_type
        should_return = ([], 0, {})

        flexmock(controller).should_receive(
            'get_proctor_model').and_return(model_dict)

        flexmock(incidents_controller).should_receive('get_incident_types').\
            and_return([]).and_return([incident_type, incident_type])

        flexmock(controller).should_receive('_delete_old_models')

        returned = controller._incident_types_to_map(datasource_uuid)
        assert returned == should_return

        # not empty incident_types
        should_return = ([incident_type, incident_type], 2, {
                         1: [incident_type, incident_type]})

        returned = controller._incident_types_to_map(datasource_uuid)
        assert returned == should_return

    def test__validate_data_source_type(self):
        user = unit_test_fixtures.proctor
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        should_return = data_source

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source).and_return(None)

        returned = controller._validate_data_source_type(user, datasource_uuid)
        assert returned == should_return

        # No found DS
        try:
            controller._validate_data_source_type(user, datasource_uuid)
        except error.BadRequest:
            pass

    def test__get_new_cluster(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        should_return = None

        flexmock(controller).should_receive(
            '_check_sequence').and_raise(Exception)

        returned = controller._get_new_cluster(
            user, datasource_uuid, incident_type)
        assert returned == should_return

    def test__coverage(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        incident_types = [incident_type]
        incident_type_by_model = {1: [incident_type]}
        num_incident_types = 1
        should_return = None

        flexmock(controller).should_receive('delete_proctor_model')\
            .and_raise(smarty.errors.DeletionFail)

        flexmock(controller).should_receive(
            '_incident_types_to_map').and_return(0, 0, 0)

        returned = controller._coverage(user, datasource_uuid, incident_types,
                                        incident_type_by_model, num_incident_types)
        assert returned == should_return

    def test_mapping(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type

        flexmock(ds_controller).should_receive('ds_sanitation').and_return([])

        flexmock(controller).should_receive(
            '_validate_data_source_type').and_return(True)

        flexmock(incidents_controller).should_receive('sanitation')

        flexmock(controller).should_receive('_incident_types_to_map')\
            .and_return([], 0, {})\
            .and_return([incident_type], 1, {})\
            .and_return([], 0, {})

        # Nothing to map
        returned = controller.mapping(user, datasource_uuid)
        assert returned.get(
            'Status code') == unit_test_fixtures.report_202.get('Status code')

        # Something to map

        flexmock(controller).should_receive('_check_sequence').and_return(1, 1)

        flexmock(incidents_controller).should_receive('update_incident_type')

        flexmock(controller).should_receive('delete_proctor_model')

        returned = controller.mapping(user, datasource_uuid)
        assert returned.get(
            'Status code') == unit_test_fixtures.report_202.get('Status code')

    def test_mapping_snooze(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        should_return = {'Status': 'Could not snooze data source mapping'}

        flexmock(controller).should_receive('_validate_data_source_type').\
            and_return(True)

        flexmock(DataSource).should_receive(
            'query.first').and_return(data_source)

        returned = controller.mapping_snooze(user, body, datasource_uuid)
        assert returned == should_return

    @patch('requests.get')
    def test_update_snooze_interval(self, mocked_get):
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = []
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = (None, None)

        returned = controller.update_snooze_interval(datasource_uuid)
        assert returned == should_return

        # snoozed
        job = {
            'job_next_run_time': "Mon, 13 Jul 2020 15:00:00 UTC",
            'job_args': ['minutes', 60]
        }
        start_time = datetime.datetime.strptime(
            "Sun, 12 Jul 2020 16:00:00 UTC", "%a, %d %b %Y %H:%M:%S %Z")
        end_time = datetime.datetime.strptime(
            "Mon, 13 Jul 2020 15:00:00 UTC", "%a, %d %b %Y %H:%M:%S %Z")
        mocked_get.return_value.json.return_value = [job]
        should_return = (1000 * int(start_time.strftime('%s')),
                         1000 * int(end_time.strftime('%s')))

        returned = controller.update_snooze_interval(datasource_uuid)
        assert returned == should_return

        # snoozed
        job = {
            'job_next_run_time': "Mon, 13 Jul 2020 15:00:00 UTC",
            'job_args': ['hours', 1]
        }
        mocked_get.return_value.json.return_value = [job]
        should_return = (1000 * int(start_time.strftime('%s')),
                         1000 * int(end_time.strftime('%s')))

        returned = controller.update_snooze_interval(datasource_uuid)
        assert returned == should_return

    @patch('requests.delete')
    def test_delete_scheduled_enable_mapping(self, mocked_delete):
        mocked_delete.return_value = mock.Mock(status_code=204)
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        response = controller.delete_scheduled_enable_mapping(datasource_uuid)

        mocked_delete.assert_called_with(
            'http://cerebro-scheduler:80/scheduler/e199ac5c-ee7d-4d73-bb61-ab2b48425adf/enable_mapping'
        )

    @patch('requests.get')
    def test_get_snooze_time(self, mocked_get):
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = {
            'Snoozed start': 1594589520000,
            'Snoozed until': 1594589520000
        }
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        should_return = 1594589520000, 1594672320000

        flexmock(DataSource).should_receive('query.first').and_return(None)

        try:
            controller.get_snooze_time(datasource_uuid)
        except error.BadRequest:
            pass

        flexmock(DataSource).should_receive(
            'query.first').and_return(data_source)

        # snoozed
        flexmock(controller).should_receive('update_snooze_interval').\
            and_return(1594589520000, 1594672320000)

        returned = controller.get_snooze_time(datasource_uuid)
        assert returned == should_return

        # not snoozed
        should_return = 1594589520000, 1594589520000
        flexmock(controller).should_receive('update_snooze_interval').\
            and_return(None, None)

        returned = controller.get_snooze_time(datasource_uuid)
        assert returned == should_return

    def test_get_inter_relations(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = unit_test_fixtures.rule_1
        rules = [rule]
        should_return = (['openstack.octavia'], [1])

        flexmock(ds_controller).should_receive(
            'get_incident_rules').and_return(rules)

        returned = controller.get_inter_relations(datasource_uuid)
        assert returned == should_return

        # complex rule
        rule = unit_test_fixtures.rule_3
        rules = [rule]
        should_return = ([['openstack.magnum', 'openstack.nova']], [3])

        flexmock(ds_controller).should_receive(
            'get_incident_rules').and_return(rules)

        returned = controller.get_inter_relations(datasource_uuid)
        assert returned == should_return

    def test__update_minute_status_entry(self):
        es_minute_status = [copy.deepcopy(unit_test_fixtures.es_status1)]
        current_minute_status = unit_test_fixtures.es_status1
        should_return = unit_test_fixtures.es_status1

        returned = controller._update_minute_status_entry(
            es_minute_status, current_minute_status)
        assert returned == should_return

    def test__update_hour_status_entry(self):
        es_hour_status = [copy.deepcopy(unit_test_fixtures.es_status1)]
        current_hour_status = copy.deepcopy(unit_test_fixtures.es_hour_status1)
        should_return = unit_test_fixtures.es_status1

        returned = controller._update_hour_status_entry(es_hour_status,
                                                        current_hour_status)
        assert returned == should_return

    def test__update_day_status_entry(self):
        es_day_status = [copy.deepcopy(unit_test_fixtures.es_status1)]
        current_day_status = unit_test_fixtures.es_status1
        should_return = unit_test_fixtures.es_status1

        returned = controller._update_day_status_entry(
            es_day_status, current_day_status)
        assert returned == should_return

    def test_create_status_check(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        status_check = unit_test_fixtures.status_check
        es_status1 = unit_test_fixtures.es_status1
        environment = status_check['environment']
        polling_timestamp = status_check['polling_timestamp']
        errors_received = status_check['errors_received']
        connected = status_check['connected']

        flexmock(incidents_controller).should_receive(
            'check_datasource_status')

        (flexmock(ElasticSearchStatus).should_receive('add').and_return(
            status_check))

        (flexmock(
            db.session).should_receive('commit').and_return(status_check))

        body = {
            'environment': environment,
            'polling_timestamp': polling_timestamp,
            'connected': connected,
            'errors_received': errors_received
        }

        flexmock(controller).should_receive(
            '_update_minute_status').and_return(es_status1)
        flexmock(controller).should_receive(
            '_update_hour_status').with_args(body, datasource_uuid)
        flexmock(controller).should_receive(
            '_update_day_status').with_args(body, datasource_uuid)

        returned = controller.create_status_check(user, datasource_uuid, body)
        assert returned.environment == environment
        assert returned.polling_timestamp == polling_timestamp
        assert returned.connected == connected
        assert returned.errors_received == errors_received

    def test_get_status(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        status_list = unit_test_fixtures.status_list
        status_list_dict = unit_test_fixtures.status_list_dict
        status_hour_list = unit_test_fixtures.status_hour_list
        status_hour_list_dict = unit_test_fixtures.status_hour_list_dict
        env = 1

        flexmock(ElasticSearchStatus).should_receive(
            'query.all').and_return(status_list)
        flexmock().should_receive('es_status_to_list_dict').with_args(
            status_list).and_return(status_list_dict)
        flexmock(DataSource).should_receive(
            'query.first').and_return(data_source)
        flexmock(controller).should_receive('is_role_6').and_return(False)

        returned = controller.get_status(user, datasource_uuid, env, {})
        assert returned == status_list_dict
        assert len(returned) > 2

        flexmock(ESHourStatus).should_receive(
            'query.all').and_return(status_hour_list)
        flexmock().should_receive('es_status_to_list_dict').with_args(
            status_list).and_return(status_hour_list_dict)

        returned_hour = controller.get_status(
            user, datasource_uuid, env, {'group_by': 'hour'})
        assert len(returned_hour) == 2
        for idx, item in enumerate(returned_hour):
            assert item['connected'] == status_hour_list_dict[idx]['connected']
            assert item['errors_received'] == status_hour_list_dict[idx][
                'errors_received']


if __name__ == '__main__':
    unittest.main()
