import copy
import datetime
import json
import os
import pytz
import sys
import unittest
from unittest import TestCase
from unittest.mock import patch

import mock
import pytest
from flexmock import flexmock
import smarty.errors as error

from sqlalchemy.orm.query import Query

import smarty.errors
from smarty.alerts import controller as alerts_controller
from smarty.app import create_app
from smarty.data_sources import controller as ds_controller
from smarty.domain.models import Alert, HelpdeskSubCategory
from smarty.domain.models import CategoryOccurrences
from smarty.domain.models import DataSource
from smarty.domain.models import Environment
from smarty.domain.models import EscalationHistory
from smarty.domain.models import EscalationPolicy
from smarty.domain.models import FlagSolution
from smarty.domain.models import HelpdeskCategory
from smarty.domain.models import Incident
from smarty.domain.models import IncidentCategory
from smarty.domain.models import IncidentEvent
from smarty.domain.models import IncidentExternalSolution
from smarty.domain.models import IncidentLinkedSolution
from smarty.domain.models import IncidentNextRun
from smarty.domain.models import IncidentResponse
from smarty.domain.models import IncidentSolution
from smarty.domain.models import IncidentStateEvent
from smarty.domain.models import IncidentType
from smarty.domain.models import IncidentTypeCommonWords
from smarty.domain.models import IncidenttypeHistory
from smarty.domain.models import IncidentTypeLabelEvent
from smarty.domain.models import IncidentTypeRefinementEvent
from smarty.domain.models import IncidentTypeSeverityEvent
from smarty.domain.models import LogCategory
from smarty.domain.models import ProctorModel
from smarty.domain.models import ProctorTrainingData
from smarty.domain.models import Reaction
from smarty.domain.models import Signature
from smarty.extensions import db
from smarty.incidents import controller
from smarty.on_call import controller as oncall_controller
from smarty.proctor import controller as proctor_controller
from smarty.proctor import utils as proctor_utils
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

    def test__incident_input_validation(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        body = {'main_state': 'open'}
        should_return = None

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)

        returned = controller._incident_input_validation(datasource_uuid, body)
        assert returned == should_return

    def test__set_is_open(self):
        body = {
            'main_state': 'open',
        }
        should_return = True
        returned = controller._set_is_open(body)
        assert returned == should_return

        body = {'is_open': 0}
        should_return = False
        returned = controller._set_is_open(body)
        assert returned == should_return

    def test__handle_host(self):
        host = "compute001"
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handle_host(query, host)
        assert returned == should_return

    def test__handle_assignee(self):
        assignee = "unassigned"
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handle_assignee(query, assignee)
        assert returned == should_return

    def test__handle_logger(self):
        logger = "openstack.nova"
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handle_logger(query, logger)
        assert returned == should_return

    def test__handle_severity(self):
        severity = "Critical"
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handle_severity(query, severity)
        assert returned == should_return

    def test__handel_search(self):
        search = "nova"
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handel_search(query, search)
        assert returned == should_return

        search = '1'
        returned = controller._handel_search(query, search)
        assert returned == should_return

    def test__handle_filter_by(self):
        filter_by_date_of = "created_date"
        start_date = 'yesterday'
        end_date = 'today'
        date = datetime.datetime.now()
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        returned = controller._handle_filter_by(query, filter_by_date_of,
                                                start_date, end_date, date)
        assert returned == should_return

    def test__handle_sorted_by(self):
        sorted_by = "created_date"
        sort_direction = 'asc'
        query = Query
        should_return = query

        flexmock(Query).should_receive('order_by').and_return(query)

        returned = controller._handle_sorted_by(query, sorted_by,
                                                sort_direction)
        assert returned == should_return

        sort_direction = 'des'

        flexmock(Query).should_receive('order_by').and_return(query)

        returned = controller._handle_sorted_by(query, sorted_by,
                                                sort_direction)
        assert returned == should_return

        sorted_by = "current_severity"
        sort_direction = 'asc'
        query = Query
        should_return = query

        flexmock(Query).should_receive('order_by').and_return(query)

        returned = controller._handle_sorted_by(query, sorted_by,
                                                sort_direction)
        assert returned == should_return

        sort_direction = 'des'

        flexmock(Query).should_receive('order_by').and_return(query)

        returned = controller._handle_sorted_by(query, sorted_by,
                                                sort_direction)
        assert returned == should_return

    def test__handle_extra_filters(self):
        user = unit_test_fixtures.user

        body = {
            'current_severity': 'healthy',
            'search': 'nova',
            'filter_by_date_of': 'created_date',
            'current_label': 'label',
            'my_tickets': 1,
            'current_state': 'OPEN'
        }
        query = Query
        should_return = query

        flexmock(Query).should_receive('filter').and_return(query)

        flexmock(controller).should_receive('_handel_search').and_return(query)

        flexmock(controller).should_receive('_handle_filter_by').and_return(
            query)

        flexmock(controller).should_receive('_handle_sorted_by').and_return(
            query)

        returned = controller._handle_extra_filters(user, query, body)
        assert returned == should_return

    def test_update_host(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        incidents = [unit_test_fixtures.incident]
        should_return = None

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)
        flexmock(Incident).should_receive(
            'query.filter.all').and_return(incidents)
        flexmock(Incident).should_receive('add')
        flexmock(db.session).should_receive('commit')

        returned = controller.update_host(datasource_uuid)
        assert returned == should_return

    def test_get_incidents(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        incident_type = unit_test_fixtures.incident_type
        query = Query

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)
        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(Incident).should_receive('query.filter').and_return(query)

        flexmock(controller).should_receive(
            'filter_own_data').and_return(query)

        flexmock(controller).should_receive(
            '_handle_extra_filters').and_return(query)

        flexmock(controller).should_receive(
            '_handle_pagination').and_return(query)

        flexmock(controller).should_receive('_handle_host').and_return(query)

        flexmock(query).should_receive('filter').and_return(query)

        flexmock(query).should_receive('limit').and_return(query)

        flexmock(query).should_receive('offset').and_return(query)

        flexmock(query).should_receive('order_by').and_return(query)

        flexmock(query).should_receive('all').and_return(
            unit_test_fixtures.incident)

        body = {
            'host': 'computer001',
            'incident_id': 1,
            'is_read': 0,
            'logger': 'openstack.nova',
            'name': 'any name',
            'number_solutions': 1,
            'occurrences': 2,
            'limit': 10,
            'offset': 1
        }
        user = unit_test_fixtures.user
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # current_state parameter
        current_state = unit_test_fixtures.incident.current_state.name
        body = {'current_state': current_state}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # incidenttype_id parameter
        incidenttype_id = unit_test_fixtures.incident.it_id
        body = {'incidenttype_id': incidenttype_id}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # current_label parameter
        current_label = unit_test_fixtures.incident.current_label
        body = {'current_label': current_label}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # environment parameter
        environment = unit_test_fixtures.incident.environment
        body = {'env': environment}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # is_open parameter
        is_open = unit_test_fixtures.incident.is_open
        body = {'is_open': is_open}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

        # last parameter
        last = 1
        body = {'last': last}
        returned = controller.get_incidents(user,
                                            body=body,
                                            datasource_uuid=datasource_uuid)
        assert returned == unit_test_fixtures.incident

    def test_extract_categories(self):
        hd_category_str = 'cat1/subcat1,cat2'
        should_return = ('cat2', 'cat1/subcat1')

        returned = controller.extract_categories(hd_category_str)
        assert returned == should_return

    def test__handle_hd_category(self):
        query = Query
        hd_category = 'cat1'
        should_return = []

        flexmock(controller).should_receive(
            '_get_ic_expressions').and_return('', False, 0)
        flexmock(IncidentCategory).should_receive(
            'query.filter.all').and_return([])
        flexmock(controller).should_receive('_get_exclude_i').and_return([])
        flexmock(controller).should_receive(
            '_get_i_expressions').and_return([])

        returned = controller._handle_hd_category(query, hd_category)
        assert returned == should_return

    def test__get_ic_expressions(self):
        hd_category = 'cat1'
        should_return = ('', False, 1)

        flexmock(HelpdeskCategory).should_receive(
            'query.filter.all').and_return([])

        returned = controller._get_ic_expressions(hd_category)
        assert returned == should_return

    def test__get_exclude_i(self):
        hd_i_list = ['cat1']
        should_return = ['cat2']

        flexmock(IncidentCategory).should_receive(
            'query.all').and_return(['cat1', 'cat2'])

        returned = controller._get_exclude_i(hd_i_list)
        assert returned == should_return

    def test__get_i_expressions(self):
        hd_i_list = [unit_test_fixtures.incident]
        query = Incident.query

        returned = controller._get_i_expressions(query, hd_i_list)
        assert isinstance(returned, Query)

    def test__handle_hd_subcategory(self):
        query = Incident.query
        hd_category = unit_test_fixtures.hd_category
        hd_subcat = unit_test_fixtures.hd_subcategory
        hd_subcategory = 'hd_cat1/hd_sc1'

        flexmock(HelpdeskCategory).should_receive(
            'query.filter.all').and_return([])

        returned = controller._handle_hd_subcategory(query, hd_subcategory)
        assert isinstance(returned, Query)

        flexmock(HelpdeskCategory).should_receive(
            'query.filter.all').and_return([hd_category])
        flexmock(HelpdeskSubCategory).should_receive(
            'query.filter.all').and_return([hd_subcat])
        flexmock(IncidentCategory).should_receive(
            'query.filter.all').and_return([])

        returned = controller._handle_hd_subcategory(query, hd_subcategory)
        assert isinstance(returned, Query)

    def test__handle_pagination(self):
        query = Incident.query
        limit = 1
        offset = 1
        last = True

        returned = controller._handle_pagination(query, limit, offset, last)
        assert isinstance(returned, Query)

    def test__set_close_incident_entries(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)
        close_incident_id = 1
        should_return = None

        flexmock(proctor_controller)\
            .should_receive('get_training_data')\
            .and_return([training_datum])

        returned = controller._set_close_incident_entries(
            user, close_incident_id, datasource_uuid)
        assert returned == should_return

    def test__merge_solutions(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        child_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        child_incidenttype_id = child_incident_type.incidenttype_id

        parent_incident_type = copy.deepcopy(unit_test_fixtures.incident_type2)
        parent_incidenttype_id = parent_incident_type.incidenttype_id

        no_sln_incident_type = copy.deepcopy(unit_test_fixtures.incident_type3)
        no_sln_incidenttype_id = no_sln_incident_type.incidenttype_id

        # test for no solution for the child
        child_incident_solution = None
        parent_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution2)

        (flexmock(Query).should_receive('first').and_return(
            child_incident_solution).and_return(parent_incident_solution))

        should_return = None
        returned = controller._merge_solutions(parent_incident_type,
                                               child_incident_type,
                                               datasource_uuid)
        assert returned == should_return

        # test for solution for child but not for parent
        child_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution)
        parent_incident_solution = None

        (flexmock(Query).should_receive('first').and_return(
            child_incident_solution).and_return(parent_incident_solution))

        returned = controller._merge_solutions(parent_incident_type,
                                               child_incident_type,
                                               datasource_uuid)
        assert child_incident_solution.it_id == parent_incident_type.it_id

        # test for solution for child and parent
        # test for solution script for child and parent
        child_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution)
        parent_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution2)
        no_sln_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution3)

        (flexmock(Query).should_receive('first').and_return(
            child_incident_solution).and_return(parent_incident_solution))

        combined_script = parent_incident_solution.solution_script.decode() + \
            "\n\n*** Other scripts ***\n\n" + \
            child_incident_solution.solution_script.decode()

        controller._merge_solutions(parent_incident_type, child_incident_type,
                                    datasource_uuid)

        assert parent_incident_solution.solution_script == combined_script.encode(
        )

        # test for solution script for child
        child_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution)
        parent_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution2)
        no_sln_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution3)

        (flexmock(Query).should_receive('first').and_return(
            child_incident_solution).and_return(no_sln_incident_solution))

        new_script = child_incident_solution.solution_script

        controller._merge_solutions(no_sln_incident_type, child_incident_type,
                                    datasource_uuid)

        assert no_sln_incident_solution.solution_script == new_script
        assert no_sln_incident_solution.number_solutions == 1

        # test for solution script for parent
        child_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution)
        parent_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution2)
        no_sln_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution3)

        (flexmock(Query).should_receive('first').and_return(
            no_sln_incident_solution).and_return(parent_incident_solution))

        same_solution = copy.deepcopy(parent_incident_solution)

        controller._merge_solutions(parent_incident_type, no_sln_incident_type,
                                    datasource_uuid)

        assert same_solution.solution_script == parent_incident_solution.solution_script
        assert same_solution.number_solutions == parent_incident_solution.number_solutions

        # test for no solution script for child or parent
        child_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution)
        parent_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution2)
        no_sln_incident_solution = copy.deepcopy(
            unit_test_fixtures.incident_solution3)

        c_solution = copy.deepcopy(no_sln_incident_solution)
        p_solution = copy.deepcopy(no_sln_incident_solution)

        (flexmock(Query).should_receive('first').and_return(
            c_solution).and_return(p_solution))

        controller._merge_solutions(no_sln_incident_type, no_sln_incident_type,
                                    datasource_uuid)

        assert c_solution.solution_script == no_sln_incident_solution.solution_script
        assert p_solution.solution_script == no_sln_incident_solution.solution_script

        assert c_solution.number_solutions == no_sln_incident_solution.number_solutions
        assert p_solution.number_solutions == no_sln_incident_solution.number_solutions

    def test_create_incident(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        environment = copy.deepcopy(unit_test_fixtures.environment)
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_dict = unit_test_fixtures.incident_dict
        incidenttype_id = incident.it_id
        occurrence_date = datetime.datetime(2017, 12, 31, 19, tzinfo=pytz.UTC)
        name = incident.name
        env = incident.environment
        host = incident.host
        logger = incident.logger
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(controller).should_receive(
            'check_datasource_status').and_return(data_source)

        (flexmock(Environment).should_receive('query.get').and_return(
            environment))

        # publish exception
        (flexmock(controller).should_receive('publish_message')
         ).and_raise(Exception)

        (flexmock(controller).should_receive(
            '_get_number_solutions').and_return(1))

        flexmock(Incident).should_receive(
            'query.filter.order_by.first').and_return(incident)

        (flexmock(IncidentStateEvent).should_receive('query.get').and_return(
            environment))

        (flexmock(Incident).should_receive('add').and_return(incident))

        (flexmock(IncidentStateEvent).should_receive('add'))
        (flexmock(IncidentEvent).should_receive('add'))

        flexmock(IncidentResponse).should_receive('add')

        (flexmock(db.session).should_receive('commit'))

        (flexmock(controller).should_receive('incident_to_dict').and_return(
            incident_dict))

        (flexmock(IncidenttypeHistory).should_receive('add'))

        (flexmock(controller).should_receive('get_incidents').and_return(
            [incident]))

        (flexmock(controller).should_receive('_set_close_incident_entries'))

        (flexmock(alerts_controller).should_receive('alerts'))

        (flexmock(controller).should_receive('reactions'))

        (flexmock(controller).should_receive('get_incident_info').and_return(
            {}))

        payload = {
            'occurrence_date': occurrence_date,
            'incidenttype_id': incidenttype_id,
            'number_solutions': 0,
            'name': name,
            'env': env,
            'host': host,
            'logger': logger
        }

        returned = controller.create_incident(user, payload, datasource_uuid)
        assert returned.it_id == incidenttype_id
        assert returned.occurrence_date == occurrence_date
        assert returned.name == name
        assert returned.environment == env

        # deleting env
        environment.environment_status = 'deleting'
        (flexmock(Environment).should_receive('query.get').and_return(
            environment))

        try:
            returned = controller.create_incident(user, payload,
                                                  datasource_uuid)
        except error.Forbidden:
            pass

    def test_assign_ownership_proxy(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id
        should_return = None

        flexmock(Incident).should_receive('query.filter.first').and_return(incident)
        flexmock(controller).should_receive('_assign_ownership').and_return(None)

        returned = controller.assign_ownership_proxy(user, datasource_uuid, incident_id)
        assert returned == should_return

    def test__assign_ownership(self):
        user = unit_test_fixtures.user
        user_dict = unit_test_fixtures.user_dict
        incident = copy.deepcopy(unit_test_fixtures.incident)
        should_return = 'Escalation Policy for e199ac5c-ee7d-4d73-bb61-ab2b48425adf not found'

        flexmock(EscalationPolicy).should_receive('query.filter.first').and_return(None)

        returned = controller._assign_ownership(user, incident)
        assert returned == should_return

        should_return = None

        flexmock(EscalationPolicy).should_receive('query.filter.first').and_return(1)
        flexmock(oncall_controller).should_receive('get_user_on_call').and_return(None)
        flexmock(controller).should_receive('get_user_by_email').and_return(user_dict)

        returned = controller._assign_ownership(user, incident)
        assert returned == should_return

    def test_get_incident_info(self):
        user = unit_test_fixtures.user
        env = 1
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = unit_test_fixtures.incident_info
        incident = copy.deepcopy(unit_test_fixtures.incident)

        (flexmock(controller).should_receive('get_incidents').and_return(
            [incident]))

        flexmock(EscalationHistory).should_receive('query.filter.all').and_return([])
        flexmock(alerts_controller).should_receive('check_snoozed_ticket').and_return(False)

        returned = controller.get_incident_info(user, env, datasource_uuid)
        assert returned == should_return

        env = 0

        (flexmock(ds_controller).should_receive(
            'get_environments_by_datasource').and_return([1]))

        returned = controller.get_incident_info(user, env, datasource_uuid)
        assert returned == should_return

    def test_get_incident(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id

        (flexmock(Incident).should_receive('query.first').and_return(incident))

        returned = controller.get_incident(incident_id, datasource_uuid)
        assert returned == incident

        # no incident
        flexmock(Incident).should_receive('query.first').and_return(None)

        try:
            controller.get_incident(incident_id, datasource_uuid)
        except error.NotFound:
            pass

    def test__get_open_incident(self):
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id
        label = incident.current_label
        env = incident.environment
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        (flexmock(Incident).should_receive('query.first').and_return(incident))

        returned = controller._get_open_incident(
            label=label,
            env=env,
            incidenttype_id=incident_id,
            datasource_uuid=datasource_uuid)
        assert returned == incident

    def test_merge_incidents(self):
        user = unit_test_fixtures.user
        incident_parent = unit_test_fixtures.incident
        incident_id_parent = incident_parent.incident_id
        incident_child = unit_test_fixtures.another_incident
        incident_id_child = incident_child.incident_id
        training_data = unit_test_fixtures.training_datum
        incident_type = unit_test_fixtures.incident_type
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        (flexmock(Incident).should_receive('query.get').and_return(incident_parent))

        (flexmock(Incident).should_receive('query.get').and_return(incident_child))

        (flexmock(ProctorTrainingData).should_receive('query.all').and_return(
            [training_data]))

        (flexmock(IncidentType).should_receive('query.filter.first').and_return(
            incident_type))

        (flexmock(controller).should_receive('delete_incident').and_return(
            incident_type))

        (flexmock(db.session).should_receive('commit'))

        (flexmock(Incident).should_receive('query.all').and_return(
            incident_parent))

        (flexmock(proctor_controller).should_receive('check_rule'))

        incident_dict = unit_test_fixtures.incident_dict

        flexmock(controller).should_receive('incident_to_dict').and_return(
            incident_dict)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)
        
        flexmock(IncidentEvent).should_receive('add')

        should_return = [[]]
        returned = controller.merge_incidents(
            current_user=user,
            i_id_parent=incident_id_parent,
            i_id_child=incident_id_child,
            datasource_uuid=datasource_uuid)
        assert returned == should_return

    def test__archive_close_incident(self):
        user = unit_test_fixtures.user
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incidents_close = [incident]
        payload = {'current_state': 'discovered'}
        new_state = 'resolved'
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(controller).should_receive('get_close_states').and_return(
            ['resolved'])

        flexmock(controller).should_receive('_set_close_incident_entries')

        returned = controller._archive_close_incident(user, incidents_close, payload,
                                                      new_state,
                                                      datasource_uuid)
        assert returned is None

    def test__update_incident_sanitation(self):
        user = unit_test_fixtures.user
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id
        payload = {'current_state': 'discovered'}
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type

        flexmock(Incident).should_receive(
            'query.filter.first').and_return(incident)

        flexmock(IncidentType).should_receive(
            'query.get').and_return(incident_type)

        flexmock(Incident).should_receive('query.filter.first').and_return(
            incident)

        flexmock(controller).should_receive('get_close_states').and_return(
            ['resolved'])

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive('get_incidents').and_return([])

        flexmock(controller).should_receive('_archive_close_incident')

        returned = controller._update_incident_sanitation(
            user, incident_id, payload, datasource_uuid)
        assert returned == incident

        # no incident
        flexmock(Incident).should_receive('query.filter.first').and_return(
            None)

        try:
            controller._update_incident_sanitation(user, incident_id, payload,
                                                   datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # archived
        incident.current_state._name_ = 'ARCHIVED'

        flexmock(Incident).should_receive('query.filter.first').and_return(
            incident)

        try:
            controller._update_incident_sanitation(user, incident_id, payload,
                                                   datasource_uuid)
        except:
            pass

        # closed
        incident.current_state._name_ = 'INVESTIGATING'
        payload = {'current_state': 'RESOLVED'}

        flexmock(controller).should_receive('get_close_states').and_return(
            ['RESOLVED'])

        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._update_incident_sanitation(user, incident_id, payload,
                                                   datasource_uuid)
        except:
            pass

        # no closed
        incident.current_state._name_ = 'INVESTIGATING'
        payload = {'current_state': 'SIMULATING_INCIDENT'}

        flexmock(controller).should_receive('get_close_states').and_return(
            ['RESOLVED'])

        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._update_incident_sanitation(user, incident_id, payload,
                                                   datasource_uuid)
        except:
            pass

    def test__check_closed_condition(self):
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_type = unit_test_fixtures.incident_type
        hd_c = unit_test_fixtures.hd_category
        hd_category = unit_test_fixtures.hd_category_test
        incident_solution = unit_test_fixtures.incident_solution
        incident_liked_solution = unit_test_fixtures.incident_liked_solution
        payload = {'current_state': 'CLOSED'}
        should_return = None

        flexmock(IncidentCategory).should_receive('query.get').and_return(hd_c)
        flexmock(HelpdeskCategory).should_receive('query.get').and_return(hd_category)
        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(incident_solution)
        flexmock(IncidentLinkedSolution).should_receive('query.get').and_return(incident_liked_solution)

        returned = controller._check_closed_condition(incident, incident_type, payload)
        assert returned == should_return

        hd_category = unit_test_fixtures.hd_category
        flexmock(HelpdeskCategory).should_receive('query.get').and_return(hd_category)
        flexmock(IncidentSolution).should_receive('query.filter.first').and_return(None)
        flexmock(IncidentLinkedSolution).should_receive('query.get').and_return(None)

        try:
            returned = controller._check_closed_condition(incident, incident_type, payload)
        except smarty.errors.Forbidden:
            pass

    def test__trigger_updates(self):
        user = unit_test_fixtures.user
        incident = copy.deepcopy(unit_test_fixtures.incident)
        old_state = 'resolved'
        data_source = unit_test_fixtures.data_source
        datasource_uuid = data_source.uuid
        training_datum = unit_test_fixtures.training_datum
        training_data = [training_datum]

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.all').and_return(training_data)

        flexmock(alerts_controller).should_receive('alerts')

        flexmock(controller).should_receive('reactions')

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)

        returned = controller._trigger_updates(user, incident, old_state,
                                               datasource_uuid)
        assert returned is None

    def test_update_incident(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id
        incident_dict = unit_test_fixtures.incident_dict
        occurrences = incident.occurrences
        occurrence_date = incident.occurrence_date
        number_solutions = incident.number_solutions
        current_severity = incident.current_severity
        payload = {
            'occurrences': occurrences,
            'last_occurrence_date': occurrence_date,
            'number_solutions': number_solutions,
            'current_severity': current_severity,
            'current_state': incident.current_state.name
        }
        user = unit_test_fixtures.user

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive(
            '_update_incident_sanitation').and_return(incident)

        flexmock(controller).should_receive('incident_to_dict').and_return(
            incident_dict)

        flexmock(controller).should_receive('_trigger_updates')

        flexmock(controller).should_receive('get_incident_info').and_return({})

        flexmock(controller).should_receive('update_report').and_return()

        flexmock(IncidentNextRun).should_receive('query.get').and_return()
        flexmock(controller).should_receive('update_extras').and_return()
        flexmock(controller).should_receive('_add_incident_event').and_return()

        # Exception
        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        returned = controller.update_incident(user, incident_id, payload,
                                              datasource_uuid)
        assert returned == incident

    def test_delete_incident(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        user = unit_test_fixtures.user
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_id = incident.incident_id
        incident_dict = unit_test_fixtures.incident_dict

        flexmock(Incident).should_receive(
            'query.filter.first').and_return(incident)

        flexmock(controller).should_receive('incident_to_dict').and_return(
            incident_dict)

        # Exception
        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        flexmock(controller).should_receive(
            'delete_incident_dependants').and_return(None)

        flexmock(controller).should_receive('get_incident_info').and_return({})

        should_return = True
        returned = controller.delete_incident(user, incident_id,
                                              datasource_uuid)
        assert returned == should_return

        # with a reason
        reason = 'reason'
        should_return = True
        returned = controller.delete_incident(user, incident_id,
                                              datasource_uuid, reason)
        assert returned == should_return

        # not incident
        flexmock(Incident).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.delete_incident(user, incident_id, datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # commit exception
        flexmock(Incident).should_receive('query.filter.first').and_return(
            incident)

        flexmock(db.session).should_receive('commit').and_raise(Exception)

        try:
            controller.delete_incident(user, incident_id, datasource_uuid)
        except smarty.errors.DeletionFail:
            pass

    def test_get_incident_types(self):
        incident_type = unit_test_fixtures.incident_type
        incident = unit_test_fixtures.incident
        cluster_id = incident_type.cluster_id
        proctormodel_id = incident_type.proctormodel_id
        label = incident_type.label
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        query = Query

        flexmock(IncidentType).should_receive(
            'query.get').and_return(incident_type)

        flexmock(IncidentType).should_receive('query.filter').and_return(query)

        flexmock(query).should_receive('filter').and_return(query)

        flexmock(controller)\
            .should_receive('set_query_incident_type_property')\
            .and_return(query)

        flexmock(controller).should_receive(
            'filter_by_logcategory').and_return([incident_type])

        flexmock(controller).should_receive(
            'filter_by_logcategories').and_return([incident_type])

        flexmock(Query).should_receive('all').and_return(incident_type)

        flexmock(controller).should_receive('get_incident').and_return(
            incident)

        flexmock(controller).should_receive('get_incident_type').and_return(
            incident_type)

        body = {
            'cluster_id': cluster_id,
            'proctormodel_id': proctormodel_id,
            'label': label,
            'logcategory': 1,
            'logcategories': json.dumps([1]),
            'search': 'nova',
            'incident_id': 1
        }
        returned = controller.get_incident_types(
            body=body,
            datasource_uuid=datasource_uuid,
            except_proctormodel_id=1)
        assert returned == [incident_type]

        # no body
        returned = controller.get_incident_types(
            datasource_uuid=datasource_uuid)
        assert returned == incident_type

    def test_filter_by_logcategory(self):
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_type.logcategories = "[1, 2]"
        incident_types = [incident_type]
        logcategory = 1
        should_return = [incident_type]

        returned = controller.filter_by_logcategory(incident_types,
                                                    logcategory)
        assert returned == should_return

    def test_filter_by_logcategories(self):
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_type.logcategories = "[1, 2]"
        incident_types = [incident_type]
        logcategories = json.dumps([1])
        should_return = [incident_type]

        returned = controller.filter_by_logcategories(incident_types,
                                                      logcategories)
        assert returned == should_return

    def test_set_query_incident_type_property(self):
        body = {
            'label': 'label',
            'proctormodel_id': 1,
            'cluster_id': 1,
            'severity': 'critical',
            'labeled': True,
            'limit': 1,
            'offset': 1
        }
        query = Query
        should_return = query

        flexmock(query).should_receive('filter').and_return(query)

        flexmock(query).should_receive('limit').and_return(query)

        flexmock(query).should_receive('offset').and_return(query)

        returned = controller.set_query_incident_type_property(body, query)
        assert returned == should_return

    def test__set_incident_types(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_type.logcategories = "[1]"
        incident_types = [incident_type]
        logcategories = [1]

        flexmock(controller).should_receive('get_incident_types').and_return(
            incident_types)

        returned = controller._set_incident_types(logcategories,
                                                  datasource_uuid)
        assert returned == incident_types

    def test__labeled_incident_types(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_type.logcategories = "[1]"
        incident_types = [incident_type]
        log_archetype_dict = unit_test_fixtures.log_archetype_dict
        should_return = unit_test_fixtures.label_incident_type

        flexmock(proctor_controller)\
            .should_receive('get_log_category')\
            .and_return(log_archetype_dict)

        returned = controller._labeled_incident_types(incident_types,
                                                      datasource_uuid)
        assert returned == should_return

    def test_labeled_incident_types(self):
        body = {'logcategories': '1'}
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_types = [incident_type]
        should_return = incident_types

        flexmock(controller).should_receive('_set_incident_types').and_return(
            incident_types)

        flexmock(controller).should_receive(
            '_labeled_incident_types').and_return(incident_types)

        returned = controller.labeled_incident_types(body, datasource_uuid)
        assert returned == should_return

    def test_create_incident_type(self):
        data_source = unit_test_fixtures.data_source
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        cluster_id = incident_type.cluster_id
        proctormodel_id = incident_type.proctormodel_id
        input_df = incident_type.input_df
        label_prediction = incident_type.label_prediction
        severity = incident_type.severity
        incident_label_event = unit_test_fixtures.label_event
        incident_type_severity_event = unit_test_fixtures.severity_event

        flexmock(IncidentType).should_receive('query.filter.order_by.first')

        flexmock(controller).should_receive('check_datasource_status')

        flexmock(IncidentType).should_receive('add').and_return(incident_type)

        flexmock(IncidentTypeLabelEvent).should_receive('add').\
            and_return(incident_label_event)

        flexmock(IncidentTypeSeverityEvent).should_receive('add').\
            and_return(incident_type_severity_event)

        flexmock(IncidentTypeRefinementEvent).should_receive('add').\
            and_return(incident_type_severity_event)

        flexmock(db.session).should_receive('commit')

        flexmock(alerts_controller).should_receive('alerts')

        flexmock(controller).should_receive('reactions')

        user = unit_test_fixtures.user
        payload = {
            'cluster_id': cluster_id,
            'proctormodel_id': proctormodel_id,
            'input_df': input_df,
            'label_prediction': label_prediction,
            'severity': severity,
            'label': 'label'
        }

        flexmock(controller).should_receive('get_incident_label')\
            .and_return('label')

        returned = controller.create_incident_type(user, payload,
                                                   datasource_uuid)
        assert returned.cluster_id == cluster_id
        assert returned.proctormodel_id == proctormodel_id
        assert returned.input_df == input_df
        assert returned.label_prediction == label_prediction

    def test_get_incident_type(self):
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incidenttype_id = incident_type.incidenttype_id
        incident_type.logcategories = "[1]"
        incident_solution = unit_test_fixtures.incident_solution
        log_category = copy.deepcopy(unit_test_fixtures.log_category)
        logcategory_id = log_category.logcategory_id
        signature = unit_test_fixtures.signature
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(IncidentType).should_receive(
            'query.first').and_return(incident_type)
        flexmock(LogCategory).should_receive(
            'query.first').and_return(log_category)
        flexmock(Signature).should_receive('query.get').and_return(signature)
        flexmock(IncidentSolution).should_receive(
            'query.filter').and_return([incident_solution])
        flexmock(controller).should_receive('update_payload_hd')
        flexmock(proctor_utils).should_receive(
            'get_openai_details').and_return(None)
        flexmock(proctor_utils).should_receive(
            'get_openai_solution').and_return(None)
        flexmock(proctor_utils).should_receive(
            'get_openai_reaction').and_return(None)
        flexmock(proctor_utils).should_receive(
            'get_openai_reply_msg').and_return(None)
        flexmock(proctor_utils).should_receive(
            'get_openai_severity').and_return(None)
        flexmock(proctor_utils).should_receive(
            'get_openai_category').and_return(None)

        returned = controller.get_incident_type(
            incidenttype_id=incidenttype_id, datasource_uuid=datasource_uuid)
        assert returned == incident_type

        # no incident_type
        flexmock(IncidentType).should_receive('query.first').and_return(None)

        returned = controller.get_incident_type(
            incidenttype_id=incidenttype_id, datasource_uuid=datasource_uuid)
        assert returned is None

    def test__merge_incident_type_attributes(self):
        parent_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        child_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        should_return = copy.deepcopy(unit_test_fixtures.incident_type)

        returned = controller._merge_incident_type_attributes(
            parent_incident_type, child_incident_type)
        assert returned == should_return

    def test__merge_ext_solutions(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        parent_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        child_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        should_return = None

        flexmock(IncidentExternalSolution).should_receive(
            'query.filter.all').and_return([incident])

        returned = controller._merge_ext_solutions(parent_incident_type,
                                                   child_incident_type,
                                                   datasource_uuid)
        assert returned == should_return

        flexmock(IncidentExternalSolution).should_receive(
            'query.filter.all').and_return(None)

        returned = controller._merge_ext_solutions(parent_incident_type,
                                                   child_incident_type,
                                                   datasource_uuid)
        assert returned == should_return

    def test__update_incident_solutions(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incidenttype_id = incident.it_id
        number_solutions = incident.number_solutions
        should_return = None
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(Incident).should_receive('query.filter.all').and_return(
            [incident])

        flexmock(controller).should_receive(
            '_get_number_solutions').and_return(number_solutions)

        returned = controller._update_incident_solutions(
            incidenttype_id, datasource_uuid)
        assert returned == should_return

    def test__delete_archived_incidents(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incidenttype_id = incident.it_id
        should_return = None

        flexmock(controller).should_receive('get_incidents').and_return(
            [incident])

        flexmock(proctor_controller).should_receive('delete_training_data')

        returned = controller._delete_archived_incidents(
            user, incidenttype_id, datasource_uuid)
        assert returned == should_return

    def test__merge_incident_type_history(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        parent_incident = copy.deepcopy(unit_test_fixtures.incident)
        parent_type_id = parent_incident.it_id
        child_incident = copy.deepcopy(unit_test_fixtures.incident)
        child_type_id = child_incident.it_id
        incident_type_history = copy.deepcopy(
            unit_test_fixtures.incident_type_history)
        should_return = None
        incident_type = copy.deepcopy(unit_test_fixtures.incident)

        flexmock(Incident).should_receive(
            'query.filter.first').and_return(parent_incident)
        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(IncidenttypeHistory)\
            .should_receive('query.filter.all')\
            .and_return([incident_type_history])

        flexmock(IncidenttypeHistory).should_receive('add')

        flexmock(db.session).should_receive('commit')

        returned = controller._merge_incident_type_history(
            datasource_uuid, parent_type_id, child_type_id)
        assert returned == should_return

    def test__label_propagation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        parent_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        child_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        environment_dict = unit_test_fixtures.environment_dict
        environments = [environment_dict]
        incident = copy.deepcopy(unit_test_fixtures.incident)
        should_return = copy.deepcopy(unit_test_fixtures.incident_type)

        flexmock(controller)\
            .should_receive('_merge_incident_type_attributes')\
            .and_return(parent_incident_type)

        flexmock(controller).should_receive('_merge_solutions')

        flexmock(controller).should_receive('_merge_ext_solutions')

        flexmock(controller).should_receive('_merge_incident_type_history')

        flexmock(ds_controller)\
            .should_receive('get_environments')\
            .and_return(environments)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        flexmock(controller)\
            .should_receive('get_incidents')\
            .and_return([incident])

        flexmock(controller).should_receive('_propagation_events')

        flexmock(controller).should_receive('_delete_archived_incidents')

        flexmock(proctor_controller).should_receive('delete_training_data')

        flexmock(controller).should_receive('delete_incident')

        flexmock(controller).should_receive('delete_incident_type')

        flexmock(controller).should_receive('_update_incident_solutions')

        returned = controller._label_propagation(user, parent_incident_type,
                                                 child_incident_type,
                                                 datasource_uuid)
        assert returned == should_return

    def test__propagation_events(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        parent_incident = copy.deepcopy(unit_test_fixtures.incident)
        parent_incidenttype_id = parent_incident.it_id
        child_incident = copy.deepcopy(unit_test_fixtures.incident)
        child_incident_dict = unit_test_fixtures.incident_dict
        should_return = None

        flexmock(controller).should_receive('merge_incidents')

        returned = controller._propagation_events(user, child_incident,
                                                  parent_incident,
                                                  parent_incidenttype_id,
                                                  datasource_uuid)
        assert returned == should_return

        # no parent_incident
        flexmock(controller)\
            .should_receive('incident_to_dict')\
            .and_return(child_incident_dict)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        flexmock(db.session).should_receive('commit')

        returned = controller._propagation_events(user, child_incident, None,
                                                  parent_incidenttype_id,
                                                  datasource_uuid)
        assert returned == should_return

    def test__check_label_auth(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        parent_incident = copy.deepcopy(unit_test_fixtures.incident)
        parent_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        v = 'label'
        current_label = parent_incident.current_label
        should_return = None

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        returned = controller._check_label_auth(user, v, current_label,
                                                parent_incident_type,
                                                datasource_uuid)
        assert returned == should_return

        # Unknown label
        v = 'Unknown'
        returned = controller._check_label_auth(user, v, current_label,
                                                parent_incident_type,
                                                datasource_uuid)
        assert returned == should_return

        # no permission
        v = 'label'
        current_label = 'Unknown'
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._check_label_auth(user, v, current_label,
                                         parent_incident_type, datasource_uuid)
        except error.Forbidden:
            pass

        # no permission
        v = 'Unknown'
        current_label = 'label'
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._check_label_auth(user, v, current_label,
                                         parent_incident_type, datasource_uuid)
        except:
            pass

    def test__check_severity_auth(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        new_severity = 'Critical'
        current_severity = 'Unknown'
        should_return = None

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive('get_severities').and_return(
            ['Critical'])

        returned = controller._check_severity_auth(user, new_severity,
                                                   current_severity,
                                                   datasource_uuid)
        assert returned == should_return

        # no found severity
        flexmock(controller).should_receive('get_severities').and_return([])

        try:
            controller._check_severity_auth(user, new_severity,
                                            current_severity, datasource_uuid)
        except error.BadRequest:
            pass

        # no permission
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._check_severity_auth(user, new_severity,
                                            current_severity, datasource_uuid)
        except error.Forbidden:
            pass

        # no permission
        new_severity = 'Unknown'
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller._check_severity_auth(user, new_severity,
                                            current_severity, datasource_uuid)
        except error.Forbidden:
            pass

    def test_find_incident_type(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incidenttype_id = 1
        should_return = unit_test_fixtures.incident_type

        flexmock(IncidentType)\
            .should_receive('query.filter.first')\
            .and_return(should_return)

        returned = controller.find_incident_type(incidenttype_id,
                                                 datasource_uuid)
        assert returned == should_return

        # no found
        flexmock(IncidentType)\
            .should_receive('query.filter.first')\
            .and_return(None)

        try:
            controller.find_incident_type(incidenttype_id, datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

    def test_get_parent_incident_type(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        new_label = 'label'
        should_return = 'it_id_2'

        flexmock(IncidentType)\
            .should_receive('query.filter.all')\
            .and_return(['it_id_2'])

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        returned = controller.get_parent_incident_type(user, datasource_uuid,
                                                       new_label, 'it_id_1')
        assert returned == should_return

        # no permission
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_parent_incident_type(user, datasource_uuid,
                                                new_label, 'it_id_1')
        except error.Forbidden:
            pass

    def test__handle_merge(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_type_dict = unit_test_fixtures.incident_type_dict
        new_label = 'label'
        data_source = unit_test_fixtures.data_source

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)

        # noting to merge
        flexmock(controller)\
            .should_receive('get_parent_incident_type')\
            .and_return(None)

        returned = controller._handle_merge(user, datasource_uuid,
                                            incident_type, new_label)
        assert returned is False

        # merge
        flexmock(controller)\
            .should_receive('get_parent_incident_type')\
            .and_return(incident_type)

        flexmock(controller)\
            .should_receive('incident_type_to_dict')\
            .and_return(incident_type_dict)

        flexmock(controller).should_receive('publish_message')

        flexmock(controller)\
            .should_receive('_label_propagation')\
            .and_return(incident_type_dict)

        flexmock(db.session).should_receive('commit')

        returned = controller._handle_merge(user, datasource_uuid,
                                            incident_type, new_label)
        assert returned is True

        # Exception
        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        returned = controller._handle_merge(user, datasource_uuid,
                                            incident_type, new_label)
        assert returned is False

    def test_sanitation(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident.occurrences = 0
        report = unit_test_fixtures.report
        training_data = [unit_test_fixtures.training_datum]
        proctor_model_dict = unit_test_fixtures.proctor_model_dict
        user = unit_test_fixtures.user

        flexmock(controller).should_receive('get_incidents').and_return(
            [incident])
        flexmock(ds_controller).should_receive(
            'get_environments_by_datasource').and_return(
                [incident.environment])

        flexmock(controller).should_receive('update_proctor_training_entries').\
            and_return(incident)

        flexmock(controller).should_receive('delete_incident')

        flexmock(ProctorModel)\
            .should_receive('query.filter.all')\
            .and_return([proctor_model_dict])

        returned = controller.sanitation(user, datasource_uuid)
        assert report == returned

    def test_update_incident_type(self):
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incidenttype_id = incident_type.incidenttype_id
        incident_type_dict = unit_test_fixtures.incident_type_dict
        payload = {'label': 'Unknown', 'severity': 'Unknown'}
        user = copy.deepcopy(unit_test_fixtures.user)
        data_source = unit_test_fixtures.data_source

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive('find_incident_type').and_return(
            incident_type)

        flexmock(controller).should_receive(
            'incident_type_to_dict').and_return(incident_type_dict)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        flexmock(controller).should_receive('_check_label_auth')

        flexmock(controller).should_receive('_check_severity_auth')

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('update_report_list').and_return()

        returned = controller.update_incident_type(user, incidenttype_id,
                                                   payload, data_source.uuid)
        assert returned == incident_type

        # merge
        payload = {'label': 'label'}
        flexmock(controller).should_receive('_handle_merge').and_return(True)

        returned = controller.update_incident_type(user, incidenttype_id,
                                                   payload, data_source.uuid)
        assert returned is None

    def test_update_incident_type_delay(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        payload = {'label': 'label'}
        incident_type = unit_test_fixtures.incident_type
        incidenttype_id = 1
        data_source = unit_test_fixtures.data_source

        flexmock(controller).should_receive('find_incident_type')

        flexmock(controller).should_receive(
            'find_incident_type').and_return(incident_type)

        flexmock(controller).should_receive(
            'get_parent_incident_type').and_return(False)

        flexmock(controller).should_receive('update_incident_type')

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        returned = controller.update_incident_type_delay(
            user, incidenttype_id, payload, datasource_uuid)
        assert returned is None

    def test_update_training_data_labels(self):
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)
        incident_type = unit_test_fixtures.incident_type

        controller.update_training_data_labels([training_datum], incident_type)

        assert training_datum.predicted_label == incident_type.label

    def test_delete_incident_type(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = unit_test_fixtures.incident_type
        incidenttype_id = incident_type.incidenttype_id
        incident_type_history = unit_test_fixtures.incident_type_history
        incident_solution = unit_test_fixtures.incident_solution
        flag_solution = unit_test_fixtures.flag_solution
        alert = unit_test_fixtures.alert
        common_word = unit_test_fixtures.common_word

        flexmock(IncidentType).should_receive('query.filter.first').\
            and_return(incident_type)

        flexmock(controller).should_receive('delete_incident_type_dependants')

        flexmock(IncidenttypeHistory).should_receive('query.filter.all').\
            and_return([incident_type_history])

        flexmock(IncidentSolution).should_receive('query.filter.all').\
            and_return([incident_solution])

        flexmock(FlagSolution).should_receive('query.filter.all').\
            and_return([flag_solution])

        flexmock(Alert).should_receive('query.filter.all').and_return([alert])

        flexmock(Reaction).should_receive('query.filter.all').and_return(
            [alert])

        flexmock(IncidentTypeCommonWords).should_receive('query.get').and_return(
            common_word)

        try:
            controller.delete_incident_type(user, incidenttype_id,
                                            datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

        # empty response
        flexmock(IncidentType).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.delete_incident_type(user, incidenttype_id,
                                            datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

    def test_get_incident_events(self):
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_type = unit_test_fixtures.incident_type
        state_event = unit_test_fixtures.state_event
        label_event = unit_test_fixtures.label_event
        severity_event = unit_test_fixtures.severity_event
        refinement_event = unit_test_fixtures.refinement_event
        start_date = incident.created_date
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        (flexmock(controller).should_receive('get_incidents').and_return(
            [incident]))

        (flexmock(controller).should_receive('get_incident_types').and_return(
            [incident_type]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            start_date, [state_event]).and_return([state_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            None, [state_event]).and_return([state_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            start_date, [label_event]).and_return([label_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            None, [label_event]).and_return([label_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            start_date, [severity_event]).and_return([severity_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            None, [severity_event]).and_return([severity_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            start_date, [refinement_event]).and_return([refinement_event]))

        (flexmock(controller).should_receive('filter_after_date').with_args(
            None, [refinement_event]).and_return([refinement_event]))

        returned = controller.get_incident_events(
            user, datasource_uuid=datasource_uuid)
        assert returned == [
            state_event, label_event, severity_event, refinement_event
        ]

        # with fields
        returned = controller.get_incident_events(
            user,
            datasource_uuid=datasource_uuid,
            fields=['label', 'state', 'severity', 'refinement'])
        assert returned == [
            state_event, label_event, severity_event, refinement_event
        ]

        # state with start_date
        returned = controller.get_incident_events(
            user,
            datasource_uuid=datasource_uuid,
            fields=['state'],
            start_date=start_date)
        assert returned == [state_event]

        # label with start_date
        returned = controller.get_incident_events(
            user,
            datasource_uuid=datasource_uuid,
            fields=['label'],
            start_date=start_date)
        assert returned == [label_event]

        # severity with start_date
        returned = controller.get_incident_events(
            user,
            datasource_uuid=datasource_uuid,
            fields=['severity'],
            start_date=start_date)
        assert returned == [severity_event]

        # refinement with start_date
        returned = controller.get_incident_events(
            user,
            datasource_uuid=datasource_uuid,
            fields=['refinement'],
            start_date=start_date)
        assert returned == [refinement_event]

    def test_filter_after_date(self):
        incident = copy.deepcopy(unit_test_fixtures.incident)
        start_date = incident.created_date

        # state_event test
        flexmock(IncidentStateEvent)
        state_event = IncidentStateEvent()
        state_event.state = unit_test_fixtures.state_event.state

        IncidentStateEvent.should_receive('query.count').and_return(1)
        IncidentStateEvent.should_receive('query.one').and_return(state_event)
        IncidentStateEvent.should_receive('query.all').and_return(
            [state_event])

        returned = controller.filter_after_date(start_date, state_event.query)
        assert returned[0].state.name == state_event.state.name

        returned = controller.filter_after_date(None, state_event.query)
        assert returned[0].state.name == state_event.state.name

        # label_event test
        flexmock(IncidentTypeLabelEvent)
        label_event = IncidentTypeLabelEvent()
        label_event.label = unit_test_fixtures.label_event.label

        IncidentTypeLabelEvent.should_receive('query.count').and_return(1)
        IncidentTypeLabelEvent.should_receive('query.one').and_return(
            label_event)
        IncidentTypeLabelEvent.should_receive('query.all').and_return(
            [label_event])

        returned = controller.filter_after_date(start_date, label_event.query)
        assert returned[0].label == label_event.label

        returned = controller.filter_after_date(None, label_event.query)
        assert returned[0].label == label_event.label

        # severity_event test
        flexmock(IncidentTypeSeverityEvent)
        severity_event = IncidentTypeSeverityEvent()
        severity_event.severity = unit_test_fixtures.severity_event.severity

        IncidentTypeSeverityEvent.should_receive('query.count').and_return(1)
        IncidentTypeSeverityEvent.should_receive('query.one').and_return(
            severity_event)
        IncidentTypeSeverityEvent.should_receive('query.all').and_return(
            [severity_event])

        returned = controller.filter_after_date(start_date,
                                                severity_event.query)
        assert returned[0].severity == severity_event.severity

        returned = controller.filter_after_date(None, severity_event.query)
        assert returned[0].severity == severity_event.severity

        # refinement_event test
        flexmock(IncidentTypeRefinementEvent)
        refinement_event = IncidentTypeRefinementEvent()
        refinement_event.refinement = unit_test_fixtures.refinement_event.refinement

        IncidentTypeRefinementEvent.should_receive('query.count').and_return(1)
        IncidentTypeRefinementEvent.should_receive('query.one').and_return(
            refinement_event)
        IncidentTypeRefinementEvent.should_receive('query.all').and_return(
            [refinement_event])

        returned = controller.filter_after_date(start_date,
                                                refinement_event.query)
        assert returned[0].refinement == refinement_event.refinement

        returned = controller.filter_after_date(None, refinement_event.query)
        assert returned[0].refinement == refinement_event.refinement

        # class with no created_date attribute
        flexmock(IncidentType)
        incident = IncidentType()

        IncidentTypeRefinementEvent.should_receive('query.count').and_return(1)
        IncidentTypeRefinementEvent.should_receive('query.one').and_return(
            incident)

        returned = controller.filter_after_date(start_date, incident.query)
        assert returned is None

        returned = controller.filter_after_date(None, incident.query)
        assert returned is None

        # class which is not query
        self.assertRaises(Exception,
                          controller.filter_after_date(start_date, incident))

    def test_get_severities(self):
        should_return = unit_test_fixtures.severities
        returned = controller.get_severities()
        assert returned == should_return

    def test_get_number_solutions(self):
        incidenttype_id = 1
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(IncidentSolution).should_receive(
            'query.filter.first').and_return(incident)

        should_return = incident.number_solutions
        returned = controller._get_number_solutions(incidenttype_id,
                                                    datasource_uuid)
        assert returned == should_return

        # no incident
        flexmock(IncidentSolution).should_receive(
            'query.filter.first').and_return(None)

        should_return = 0
        returned = controller._get_number_solutions(incidenttype_id,
                                                    datasource_uuid)
        assert returned == should_return

    def test_get_states(self):
        should_return = unit_test_fixtures.states
        returned = controller.get_states()
        assert returned == should_return

    def test_get_user_closed_states(self):
        should_return = unit_test_fixtures.user_closed_states
        returned = controller.get_user_closed_states('elastic')
        assert returned == should_return

    def test_get_user_open_states(self):
        should_return = unit_test_fixtures.open_states
        returned = controller.get_user_open_states('elastic')
        assert returned == should_return

    def test_get_close_states(self):
        should_return = unit_test_fixtures.closed_states
        returned = controller.get_close_states()
        assert returned == should_return

    def test_validate_datasource_uuid(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        should_return = data_source

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        returned = controller.validate_datasource_uuid(datasource_uuid)
        assert returned == should_return

        # no data source
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.validate_datasource_uuid(datasource_uuid)
        except error.BadRequest:
            pass

    def test_get_labels(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds = unit_test_fixtures.data_source
        label = unit_test_fixtures.label_event
        labels = [label]
        pattern = 'pattern'
        should_return = ['Unknown']

        flexmock(controller).should_receive(
            'validate_datasource_uuid').and_return(ds)

        flexmock(IncidentTypeLabelEvent).should_receive(
            'query.filter.all').and_return(labels)

        returned = controller.get_labels(pattern, datasource_uuid)
        assert returned == should_return

    def test_get_current_labels(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        label = unit_test_fixtures.label_event
        labels = [label]
        pattern = 'pattern'
        should_return = ['Unknown']

        flexmock(controller).should_receive('validate_datasource_uuid')

        flexmock(IncidentType).should_receive('query.filter.all').and_return(
            labels)

        returned = controller.get_current_labels(pattern, datasource_uuid)
        assert returned == should_return

    def test_get_names(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incidents = [incident]
        pattern = 'pattern'
        should_return = [incident.name]
        query = Query

        flexmock(controller).should_receive('validate_datasource_uuid')

        flexmock(Incident).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('filter').and_return(query)

        flexmock(Query).should_receive('all').and_return(incidents)

        returned = controller.get_names(pattern, datasource_uuid)
        assert returned == should_return

    def test_get_utc_time(self):
        returned = controller.get_utc_time()
        assert isinstance(returned, datetime.datetime)

    def test_refinement_validation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incidenttype_id = incident_type.incidenttype_id
        incident_type.logcategories = "[4, 5]"
        body = {'label': 'label', 'logs': unit_test_fixtures.raw_logs_2}
        data_source = unit_test_fixtures.data_source

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(IncidentType).should_receive('query.filter.first').and_return(
            incident_type)

        flexmock(controller).should_receive('validate_datasource_uuid')

        # refine blocked
        Config.REFINE_BLOCKED = True

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # log type no found
        incident_type.logcategories = "[1, 2]"
        body = {'label': 'label', 'logs': unit_test_fixtures.raw_logs_2}

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # not enough log types to split
        incident_type.logcategories = "[]"
        flexmock(IncidentType).should_receive('query.filter.first').and_return(
            incident_type)

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # no incident type
        flexmock(IncidentType).should_receive('query.filter.first').and_return(
            None)

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # incident under refinement
        Config.AFFECTED_INCIDENT_TYPES = [incidenttype_id]

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # no label
        body = {}

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned['Status code'] == should_return['Status code']

        # no permission
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        flexmock(controller).should_receive('publish_message')

        should_return = unit_test_fixtures.response_403_dict
        returned = controller.refinement_validation(user, incidenttype_id,
                                                    datasource_uuid, body)
        assert returned == should_return

        Config.AFFECTED_INCIDENT_TYPES = []
        Config.REFINE_BLOCKED = False

    def test__get_leaf_incident_type(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        parent_incident_type = [
            copy.deepcopy(unit_test_fixtures.incident_type)
        ]
        child_logcategories = set()
        root_incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        label = ''

        flexmock(controller).should_receive('update_incident_type').and_return(
            incident_type)

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        should_return = incident_type
        returned = controller._get_leaf_incident_type(user, datasource_uuid,
                                                      parent_incident_type,
                                                      child_logcategories,
                                                      root_incident_type,
                                                      label)
        assert returned == should_return

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        should_return = unit_test_fixtures.response_403_dict
        returned = controller._get_leaf_incident_type(user, datasource_uuid,
                                                      parent_incident_type,
                                                      child_logcategories,
                                                      root_incident_type,
                                                      label)
        assert returned == should_return

        # no parent_incident_type
        parent_incident_type = []

        flexmock(controller).should_receive('create_incident_type').and_return(
            incident_type)

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        should_return = incident_type
        returned = controller._get_leaf_incident_type(user, datasource_uuid,
                                                      parent_incident_type,
                                                      child_logcategories,
                                                      root_incident_type,
                                                      label)
        assert returned == should_return

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        should_return = unit_test_fixtures.response_403_dict
        returned = controller._get_leaf_incident_type(user, datasource_uuid,
                                                      parent_incident_type,
                                                      child_logcategories,
                                                      root_incident_type,
                                                      label)
        assert returned == should_return

    def test__get_incidents_to_refine(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = unit_test_fixtures.training_datum
        training_entries_id_to_update = [training_datum, training_datum]

        flexmock(ProctorTrainingData).should_receive(
            'query.get').and_return(training_datum)

        should_return = {1: training_entries_id_to_update}, [1]
        returned = controller._get_incidents_to_refine(
            datasource_uuid, training_entries_id_to_update)
        assert returned == should_return

    def test__delete_root_incident_type(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incidents = [incident]
        root_new_logcategories = []
        incidenttype_id = 1

        flexmock(controller).should_receive('get_incidents').and_return(
            incidents)

        flexmock(controller).should_receive('delete_incident')

        flexmock(controller).should_receive('delete_incident_type')

        should_return = None
        returned = controller._delete_root_incident_type(
            user, datasource_uuid, root_new_logcategories, incidenttype_id)
        assert returned == should_return

    def test__delete_ooo_incidents(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incidents = [incident]
        remain_training_entries = []
        incident_id = 1

        flexmock(controller).should_receive('delete_incident')

        should_return = None
        returned = controller._delete_ooo_incidents(user, datasource_uuid,
                                                    incident_id,
                                                    remain_training_entries)
        assert returned == should_return

    def test__update_category_occurrences(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        entry = unit_test_fixtures.training_datum
        input_df = [1, 1]
        category_occurrence = copy.deepcopy(
            unit_test_fixtures.category_occurrences)
        category_occurrence2 = copy.deepcopy(
            unit_test_fixtures.category_occurrences)
        category_occurrence2.logcategory_id = 7
        category_occurrences = [category_occurrence, category_occurrence2]
        log_category = unit_test_fixtures.log_category
        training_datum = unit_test_fixtures.training_datum

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.first').and_return(training_datum)

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)

        flexmock(CategoryOccurrences)\
            .should_receive('query.filter.all')\
            .and_return(category_occurrences)

        flexmock(db.session).should_receive('commit')

        should_return = None
        returned = controller._update_category_occurrences(
            datasource_uuid, entry, input_df)
        assert returned == should_return

    def test__update_input_df(self):
        incident_info = {}
        input_df = []
        entry = unit_test_fixtures.training_datum
        data = unit_test_fixtures.raw_logs
        child_logcategories = []
        new_hosts = set()
        new_loggers = set()
        category_occurrence = copy.deepcopy(
            unit_test_fixtures.category_occurrences)
        category_occurrences = [category_occurrence]
        incident = unit_test_fixtures.incident
        log_category = unit_test_fixtures.log_category
        training_datum = unit_test_fixtures.training_datum

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.first').and_return(training_datum)

        flexmock(LogCategory).should_receive(
            'query.filter.first').and_return(log_category)

        flexmock(CategoryOccurrences)\
            .should_receive('query.filter.all')\
            .and_return(category_occurrences)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('get_incident').and_return(
            incident)

        flexmock(controller).should_receive('update_incident')

        should_return = None
        returned = controller._update_input_df(incident_info, entry, input_df,
                                               data, child_logcategories,
                                               new_hosts, new_loggers)
        assert returned == should_return

        # if input_df
        input_df = [1]

        should_return = None
        returned = controller._update_input_df(incident_info, entry, input_df,
                                               data, child_logcategories,
                                               new_hosts, new_loggers)
        assert returned == should_return

    def test__update_occurrences(self):
        entry = unit_test_fixtures.training_datum
        label = 'label'
        child_logcategories = []
        am_ticket = False
        occ_info = {}

        should_return = [1], json.loads(entry.data.decode())
        returned = controller._update_occurrences(label, child_logcategories,
                                                  entry, am_ticket, occ_info)
        assert returned == should_return

        # with child logcategories
        child_logcategories = [4]

        flexmock(proctor_controller)\
            .should_receive('create_new_training_datum')\
            .and_return(unit_test_fixtures.response_403)

        should_return = [1], json.loads(entry.data.decode())
        returned = controller._update_occurrences(label, child_logcategories,
                                                  entry, am_ticket, occ_info)
        assert returned == should_return

    def test__delete_incident_dependants(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = copy.deepcopy(unit_test_fixtures.incident)
        query = Query

        flexmock(IncidentStateEvent).should_receive(
            'query.filter.all').and_return([])

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.all').and_return([])

        flexmock(CategoryOccurrences).should_receive(
            'query.filter').and_return(query)
        flexmock(query).should_receive('filter.all').and_return([])

        flexmock(IncidentResponse).should_receive('query.get').and_return()

        flexmock(db.session).should_receive('commit')

        controller.delete_incident_dependants(datasource_uuid, incident)

    def test_refine_incident(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        incident_types = [incident_type]
        incidenttype_id = 1
        training_data = unit_test_fixtures.training_datum
        incidents = [1]
        body = {'logs': unit_test_fixtures.raw_logs_2}

        flexmock(controller).should_receive('get_incident_type').and_return(
            incident_type)

        flexmock(controller).should_receive('get_incident_types').and_return(
            incident_types)

        flexmock(controller).should_receive(
            '_get_leaf_incident_type').and_return(incident_type)

        flexmock(controller).should_receive('update_incident_type')

        flexmock(proctor_controller)\
            .should_receive('get_training_data_by_logcategory')\
            .and_return(training_data)

        flexmock(controller)\
            .should_receive('_get_incidents_to_refine')\
            .and_return({1: training_data}, incidents)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        flexmock(controller)\
            .should_receive('_update_occurrences')\
            .and_return([1], json.loads(training_data.data.decode()))

        flexmock(controller).should_receive('_update_input_df')

        flexmock(proctor_controller).should_receive(
            'get_training_data').and_return([])

        flexmock(controller).should_receive('_delete_ooo_incidents')

        flexmock(controller).should_receive('_delete_root_incident_type')

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(data_source)

        should_return = unit_test_fixtures.response_200
        returned = controller.refine_incident(user, incidenttype_id, body,
                                              datasource_uuid)
        assert returned['Status code'] == should_return.status_code

        Config.MAPPING_BLOCKED = False

    def test__delete_occurrences(self):
        training_data = unit_test_fixtures.training_datum
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        category_occurrence = copy.deepcopy(
            unit_test_fixtures.category_occurrences)
        category_occurrences = [category_occurrence]

        flexmock(ProctorTrainingData).should_receive(
            'query.filter.first').and_return(training_data)

        flexmock(CategoryOccurrences)\
            .should_receive('query.filter.all')\
            .and_return(category_occurrences)

        should_return = None
        returned = controller._delete_occurrences(training_data,
                                                  datasource_uuid)
        assert returned == should_return

    def test_update_proctor_training_entries(self):
        incident = copy.deepcopy(unit_test_fixtures.incident)
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        training_datum = copy.deepcopy(unit_test_fixtures.training_datum)

        # no training data
        flexmock(ProctorTrainingData).should_receive(
            'query.filter.count').and_return([])

        should_return = incident
        returned = controller.update_proctor_training_entries(
            incident, datasource_uuid)
        assert returned == should_return

        # training data
        training_data = [training_datum]
        incident.current_state = 'ARCHIVED'

        flexmock(controller).should_receive('_delete_occurrences')

        flexmock(ProctorTrainingData)\
            .should_receive('query.filter.count')\
            .and_return(training_data)

        flexmock(db.session).should_receive('commit')

        should_return = incident
        returned = controller.update_proctor_training_entries(
            incident, datasource_uuid)
        assert returned == should_return

        # close incident
        incident.is_open = False

        should_return = incident
        returned = controller.update_proctor_training_entries(
            incident, datasource_uuid)
        assert returned == should_return

    def test_get_loggers(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        log_category = unit_test_fixtures.log_category
        log_categories = [log_category]
        query = Query

        flexmock(LogCategory).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('distinct').and_return(log_categories)

        should_return = ['logger']
        returned = controller.get_loggers(datasource_uuid)
        assert returned == should_return

    def test_get_hosts(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incidents = [incident]
        query = Query

        flexmock(Incident).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('distinct').and_return(incidents)

        should_return = ['controller001']
        returned = controller.get_hosts(datasource_uuid)
        assert returned == should_return

    def test_get_filters_template(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        datasource_uuid = data_source.uuid
        env = 1
        incident = unit_test_fixtures.incident
        incidents = [incident]
        users = unit_test_fixtures.users
        query = Query

        flexmock(controller).should_receive('validate_datasource_uuid')\
            .and_return(data_source)

        flexmock(Incident).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('filter').and_return(query)

        flexmock(Query).should_receive('distinct').and_return(incidents)

        flexmock(controller).should_receive(
            'filter_own_data').and_return(query)

        flexmock(controller).should_receive(
            'get_users_by_ds').and_return(users)
        flexmock(controller).should_receive(
            'hd_labels').and_return(['MyDeOS', 'Hayei'])

        should_return = unit_test_fixtures.filter_template
        returned = controller.get_filters_template(
            user, env, datasource_uuid, 'token')
        assert returned == should_return

    def test_get_type_history(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incidenttype_id = 1
        sort_by = 'history_datetime'
        query = Query
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive(
            'query.filter.first').and_return(incident_type)

        flexmock(IncidentType).should_receive(
            'query.get').and_return(incident_type)

        flexmock(IncidenttypeHistory).should_receive(
            'query.filter').and_return(query)

        flexmock(Query).should_receive('order_by').and_return(query)

        flexmock(Query).should_receive('limit').and_return(query)

        flexmock(Query).should_receive('offset').and_return(query)

        flexmock(Query).should_receive('all').and_return(query)

        flexmock(controller).should_receive('type_history_to_dict').and_return(
            [])

        should_return = []
        returned = controller.get_type_history(datasource_uuid,
                                               incidenttype_id,
                                               limit=1,
                                               offset=1,
                                               sort_by=sort_by,
                                               sort_direction='asc')
        assert returned == should_return

        should_return = []
        returned = controller.get_type_history(datasource_uuid,
                                               incidenttype_id,
                                               limit=1,
                                               offset=1,
                                               sort_by=sort_by,
                                               sort_direction='desc')
        assert returned == should_return

        # wrong direction
        try:
            controller.get_type_history(datasource_uuid,
                                        incidenttype_id,
                                        limit=1,
                                        offset=1,
                                        sort_by=sort_by,
                                        sort_direction='up')
        except error.BadRequest:
            pass

        # wrong sort
        sort_by = 'datetime'

        try:
            controller.get_type_history(datasource_uuid,
                                        incidenttype_id,
                                        limit=1,
                                        offset=1,
                                        sort_by=sort_by,
                                        sort_direction='asc')
        except error.BadRequest:
            pass

        # empty query
        flexmock(Query).should_receive('all').and_return(None)

        should_return = []
        returned = controller.get_type_history(datasource_uuid,
                                               incidenttype_id,
                                               limit=1,
                                               offset=1)
        assert returned == should_return

    def test_set_incident_is_read(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_id = 1
        incident = copy.deepcopy(unit_test_fixtures.incident)
        incident_dict = unit_test_fixtures.incident_dict

        flexmock(Incident).should_receive('query.filter.first').and_return(
            incident)
        flexmock(controller).should_receive('_add_incident_event')

        # none is_read
        body = {}

        try:
            controller.set_incident_is_read(user, datasource_uuid, incident_id,
                                            body)
        except error.BadRequest:
            pass

        # same is_read
        body = {'is_read': incident.is_read}

        try:
            controller.set_incident_is_read(user, datasource_uuid, incident_id,
                                            body)
        except error.BadRequest:
            pass

        # different is_read
        body = {'is_read': not incident.is_read}

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('incident_to_dict').and_return(
            incident_dict)

        flexmock(controller).should_receive('publish_message').and_raise(
            Exception)

        should_return = incident_dict
        returned = controller.set_incident_is_read(user, datasource_uuid,
                                                   incident_id, body)
        assert returned == should_return


if __name__ == '__main__':
    unittest.main()
