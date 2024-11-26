import copy
import json
import os
from unittest import TestCase
from unittest.mock import patch

import mock
from flexmock import flexmock
import smarty.errors as error

from sqlalchemy.orm.query import Query

import smarty.errors
from smarty.app import create_app
from smarty.data_sources import controller
from smarty.data_sources import utils
from smarty.domain.models import Alert
from smarty.domain.models import AlertsHistory
from smarty.domain.models import APIReaction
from smarty.domain.models import CategoryOccurrences
from smarty.domain.models import CerebroAgent
from smarty.domain.models import CerebroSettings
from smarty.domain.models import DataSource
from smarty.domain.models import DSShare
from smarty.domain.models import ElasticSearchStatus
from smarty.domain.models import EscalationHistory
from smarty.domain.models import EscalationPolicy
from smarty.domain.models import EnvFeatures
from smarty.domain.models import Environment
from smarty.domain.models import ESDayStatus
from smarty.domain.models import ESHourStatus
from smarty.domain.models import FlagSolution
from smarty.domain.models import HelpdeskEmail
from smarty.domain.models import HelpdeskServer
from smarty.domain.models import Incident
from smarty.domain.models import IncidentExternalSolution
from smarty.domain.models import IncidentOwnershipEvent
from smarty.domain.models import IncidentResponse
from smarty.domain.models import IncidentRule
from smarty.domain.models import IncidentSolution
from smarty.domain.models import IncidentSolutionComments
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
from smarty.domain.models import PrometheusAlert
from smarty.domain.models import Reaction
from smarty.domain.models import Role
from smarty.domain.models import Signature
from smarty.domain.models import SSHReaction
from smarty.domain.models import User
from smarty.domain.reference import IncidentSeverity
from smarty.extensions import db
from smarty.incidents import controller as incident_controller
from smarty.solutions import controller as solutions_controller
from smarty.settings import Config
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestControllerDataSources(TestCase):
    def setup_class(self):
        self.controller = controller

    def test_get_data_source(self):
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_dict = copy.deepcopy(unit_test_fixtures.data_source_dict_1)
        current_user = unit_test_fixtures.user
        role = unit_test_fixtures.role
        permission = unit_test_fixtures.permission_dict_1
        source_id = 1

        flexmock(controller).\
            should_receive('validate_capability').\
            with_args(current_user, action='view_data_source_information',
                      datasource_uuid=source_id).\
            and_return(True)

        flexmock(DataSource).\
            should_receive('query.first').\
            and_return(data_source)

        flexmock(utils).\
            should_receive('get_ds_status').\
            and_return("online")

        flexmock(DSShare).\
            should_receive('query.first').\
            and_return([])

        flexmock(Environment).\
            should_receive('query.all').\
            and_return([])

        flexmock(utils).\
            should_receive('get_role').\
            and_return(role)

        flexmock(utils).\
            should_receive('get_role_and_permissions').\
            and_return(permission)

        flexmock(controller).should_receive('get_loggers').and_return(['logger'])

        returned = controller.get_data_source(current_user, source_id)
        assert returned == data_source_dict

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_data_source(current_user, source_id)
        except:
            pass

    def test_get_datasource_uuid(self):
        user = unit_test_fixtures.user
        data_source_1 = unit_test_fixtures.data_source
        data_source_2 = unit_test_fixtures.data_source_2
        data_source_3 = unit_test_fixtures.data_source_3

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_datasource_uuid(user)
        except error.Forbidden:
            pass

        # authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource)\
            .should_receive('query.filter.all')\
            .and_return([data_source_1]).and_return([data_source_2])

        flexmock(DSShare)\
            .should_receive('query.filter.all')\
            .and_return([data_source_3])

        should_return = [
            data_source_1.uuid, data_source_2.uuid, data_source_3.uuid
        ]
        returned = controller.get_datasource_uuid(user)
        assert returned == should_return

    def test_create_env_validation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        environment = unit_test_fixtures.environment
        body = {}

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.create_env_validation(user, datasource_uuid, body)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.create_env_validation(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        # none value
        body = {'index_name': None}
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        try:
            controller.create_env_validation(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        # environment
        body = {'index_name': 'index_name'}

        flexmock(Environment).should_receive('query.filter.first').and_return(
            Environment)

        try:
            controller.create_env_validation(user, datasource_uuid, body)
        except error.BadRequest:
            pass

    def test_create_environment(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        env_features = unit_test_fixtures.env_features
        environment_dict = unit_test_fixtures.environment_dict
        response = unit_test_fixtures.response_200
        body = {}

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive('get_all_env_features').and_return(
            env_features)

        flexmock(Environment).should_receive('add')

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('environment_to_dict').and_return(
            environment_dict)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(controller).should_receive(
            '_check_ds_env_connection').and_return(response)

        should_return = environment_dict
        returned = controller.create_environment(user, datasource_uuid, body)
        assert returned == should_return

        # invalid feature
        body = {'features': json.dumps(['invalid'])}

        try:
            controller.create_environment(user, datasource_uuid, body)
        except error.BadRequest:
            pass

    def test_get_environments(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        environment = unit_test_fixtures.environment
        environments = [environment]
        environment_dict = unit_test_fixtures.environment_dict

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_environments(user, datasource_uuid)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.get_environments(user, datasource_uuid)
        except error.NotFound:
            pass

        # normal
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.all').and_return(
            environments)

        flexmock(controller).should_receive('environments_to_list').and_return(
            [environment_dict])

        should_return = [environment_dict]
        returned = controller.get_environments(user, datasource_uuid)
        assert returned == should_return

    def test_get_environment(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        environment = unit_test_fixtures.environment
        environment_id = environment.environment_id
        environment_dict = unit_test_fixtures.environment_dict

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_environment(user, datasource_uuid, environment_id)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.get_environment(user, datasource_uuid, environment_id)
        except error.NotFound:
            pass

        # no environment
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.first').and_return(None)

        try:
            controller.get_environment(user, datasource_uuid, environment_id)
        except error.NotFound:
            pass

        # bad request
        data_source.source_id = 'x'

        flexmock(Environment).should_receive('query.filter.first').and_return(
            environment)

        flexmock(controller).should_receive('environment_to_dict').and_return(
            environment_dict)

        try:
            controller.get_environment(user, datasource_uuid, environment_id)
        except error.BadRequest:
            pass

        # normal
        data_source.source_id = 1

        should_return = environment_dict
        returned = controller.get_environment(user, datasource_uuid,
                                              environment_id)
        assert returned == should_return

    def test_update_env_validation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        environment = unit_test_fixtures.environment
        environment_id = environment.environment_id
        body = {}

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.update_env_validation(user, datasource_uuid,
                                             environment_id, body)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.update_env_validation(user, datasource_uuid,
                                             environment_id, body)
        except error.BadRequest:
            pass

        # no environment
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.first').and_return(None)

        try:
            controller.update_env_validation(user, datasource_uuid,
                                             environment_id, body)
        except error.NotFound:
            pass

        # bad request
        data_source.source_id = 'x'

        flexmock(Environment).should_receive('query.filter.first').and_return(
            environment)

        try:
            controller.update_env_validation(user, datasource_uuid,
                                             environment_id, body)
        except error.BadRequest:
            pass

    def test_update_environment(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        environment = copy.deepcopy(unit_test_fixtures.environment)
        environment_id = environment.environment_id
        environment_dict = unit_test_fixtures.environment_dict
        body = {
            'env_display_name': environment.display_name,
            'features': environment.features,
            'index_name': environment.index_name
        }

        flexmock(Environment).should_receive('query.get').and_return(
            environment)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('environment_to_dict').and_return(
            environment_dict)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        should_return = environment_dict
        returned = controller.update_environment(user, datasource_uuid,
                                                 environment_id, body)
        assert returned == should_return

    def test_delete_env_validation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        environment = unit_test_fixtures.environment
        environment_id = environment.environment_id

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.delete_env_validation(user, datasource_uuid,
                                             environment_id)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        try:
            controller.delete_env_validation(user, datasource_uuid,
                                             environment_id)
        except error.BadRequest:
            pass

        # no environment
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.first').and_return(None)

        try:
            controller.delete_env_validation(user, datasource_uuid,
                                             environment_id)
        except error.NotFound:
            pass

        # bad request
        data_source.source_id = 'x'

        flexmock(Environment).should_receive('query.filter.first').and_return(
            environment)

        try:
            controller.delete_env_validation(user, datasource_uuid,
                                             environment_id)
        except error.BadRequest:
            pass

    def test_delete_environment(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        environment = copy.deepcopy(unit_test_fixtures.environment)
        environment_id = environment.environment_id
        environment_dict = unit_test_fixtures.environment_dict
        incident = unit_test_fixtures.incident
        incidents = [incident]

        flexmock(Environment).should_receive('query.get').and_return(
            environment)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('environment_to_dict').and_return(
            environment_dict)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(Incident).should_receive('query.filter.all').and_return(
            incidents)

        flexmock(incident_controller).should_receive(
            'delete_incident_dependants')

        flexmock(controller).should_receive('delete_data_source_children')

        flexmock(ElasticSearchStatus).should_receive(
            'query.filter.all').and_return(incidents)

        flexmock(ESHourStatus).should_receive('query.filter.all').and_return(
            incidents)

        flexmock(ESDayStatus).should_receive('query.filter.all').and_return(
            incidents)

        flexmock(Alert).should_receive('query.filter.all').and_return(
            incidents)

        flexmock(controller).should_receive('delete_env_from_alert')

        should_return = None
        returned = controller.delete_environment(user, datasource_uuid,
                                                 environment_id)
        assert returned == should_return

    def test_delete_env_from_alert(self):
        alert = copy.deepcopy(unit_test_fixtures.alert)
        alerts = [alert]
        alert_history = [unit_test_fixtures.alert_history]
        environment_id = 1

        flexmock(AlertsHistory).should_receive('query.filter.all').and_return(
            alert_history)

        should_return = None
        returned = controller.delete_env_from_alert(alerts, environment_id)
        assert returned == should_return

        # multiple environments
        alert.environment = json.dumps(['1', '2'])

        should_return = None
        returned = controller.delete_env_from_alert(alerts, environment_id)
        assert returned == should_return

    def test_get_environments_by_datasource(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        environment = unit_test_fixtures.environment
        environments = [environment]

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_environments_by_datasource(user, datasource_uuid)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.get_environments_by_datasource(user, datasource_uuid)
        except error.BadRequest:
            pass

        # normal
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.all').and_return(
            environments)

        should_return = [1]
        returned = controller.get_environments_by_datasource(
            user, datasource_uuid)
        assert returned == should_return

    def test_get_hosts_by_environment(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident2
        incidents = [incident]
        environment_id = 1

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_hosts_by_environment(user, datasource_uuid,
                                                environment_id)
        except error.Forbidden:
            pass

        # no environment
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([])

        try:
            controller.get_hosts_by_environment(user, datasource_uuid,
                                                environment_id)
        except error.NotFound:
            pass

        # normal
        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([1])

        flexmock(Incident).should_receive('query.filter.all').and_return(
            incidents)

        should_return = ['controller001']
        returned = controller.get_hosts_by_environment(user, datasource_uuid,
                                                       environment_id)
        assert returned == should_return

    def test_get_loggers_by_host(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident2
        incidents = [incident]
        environment_id = 1
        host = 'host'

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_loggers_by_host(user, datasource_uuid,
                                           environment_id, host)
        except error.Forbidden:
            pass

        # no environment
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([])

        try:
            controller.get_loggers_by_host(user, datasource_uuid,
                                           environment_id, host)
        except error.BadRequest:
            pass

        # no host
        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([1])

        flexmock(controller).should_receive(
            'get_hosts_by_environment').and_return(['controller001'])

        try:
            controller.get_loggers_by_host(user, datasource_uuid,
                                           environment_id, host)
        except error.BadRequest:
            pass

        # normal
        host = 'controller001'

        flexmock(Incident).should_receive('query.filter.all').and_return(
            incidents)

        should_return = ['openstack.nova']
        returned = controller.get_loggers_by_host(user, datasource_uuid,
                                                  environment_id, host)
        assert returned == should_return

    def test_get_logs_by_logger(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident2
        incidents = [incident]
        incident_type = unit_test_fixtures.incident_type2
        environment_id = 1
        host = 'host'
        logger = 'logger'

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_logs_by_logger(user, datasource_uuid,
                                          environment_id, host, logger)
        except error.Forbidden:
            pass

        # no environment
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([])

        try:
            controller.get_logs_by_logger(user, datasource_uuid,
                                          environment_id, host, logger)
        except error.BadRequest:
            pass

        # no host
        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([1])

        flexmock(controller).should_receive(
            'get_hosts_by_environment').and_return(['controller001'])

        try:
            controller.get_logs_by_logger(user, datasource_uuid,
                                          environment_id, host, logger)
        except error.BadRequest:
            pass

        # no logger
        host = 'controller001'

        flexmock(controller).should_receive('get_loggers_by_host').and_return(
            ['openstack.nova'])

        try:
            controller.get_logs_by_logger(user, datasource_uuid,
                                          environment_id, host, logger)
        except error.BadRequest:
            pass

        # normal
        logger = 'openstack.nova'

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        flexmock(Incident).should_receive('query.filter.all').and_return(
            incidents)

        flexmock(IncidentType).should_receive('query.filter.first').and_return(
            incident_type)

        should_return = [2]
        returned = controller.get_logs_by_logger(user, datasource_uuid,
                                                 environment_id, host, logger)
        assert returned == should_return

    def test_get_only_inter_relations(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = unit_test_fixtures.rule_3
        current_rules = [rule]

        flexmock(controller).should_receive('get_incident_rules').and_return(
            current_rules)

        should_return = [['openstack.magnum', 'openstack.nova']], [3]
        returned = controller.get_only_inter_relations(datasource_uuid)
        assert returned == should_return

    def test_get_data_source_relations(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_sources_uuid = [datasource_uuid]
        environments = [1]
        hosts = ['controller001']
        loggers = ['openstack.nova', 'openstack.magnum']
        logcategories = [2]
        relations = [loggers]

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_data_source_relations(user)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return(environments)

        flexmock(controller).should_receive('get_datasource_uuid').and_return(
            data_sources_uuid)

        flexmock(controller).should_receive(
            'get_hosts_by_environment').and_return(hosts)

        flexmock(controller).should_receive('get_loggers_by_host').and_return(
            loggers)

        flexmock(controller).should_receive('get_logs_by_logger').and_return(
            logcategories)

        flexmock(controller).should_receive(
            'get_relations_from_inter_relations').and_return(relations)

        should_return = relations
        returned = controller.get_data_source_relations(user)
        assert returned == should_return

    def test_get_relations_from_inter_relations(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        environment_id = 1
        host = 'controller001'
        logger = 'openstack.nova'
        logcategories = [2]
        inter_relations = [['openstack.nova']], [3]
        relations = dict()
        relations[datasource_uuid] = {}
        relations[datasource_uuid][environment_id] = {}
        relations[datasource_uuid][environment_id][host] = {}
        relations[datasource_uuid][environment_id][host][logger] = {}

        flexmock(controller).should_receive(
            'get_only_inter_relations').and_return(inter_relations)

        flexmock(controller).should_receive('get_logs_by_logger').and_return(
            logcategories)

        should_return = relations
        returned = controller.get_relations_from_inter_relations(
            user, relations, datasource_uuid, environment_id, host)
        assert returned == should_return

    def test_get_incident_rules(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule_entry = unit_test_fixtures.rule_2
        rule_id = rule_entry.rule_id
        rule = rule_entry.rule
        active = rule_entry.active

        flexmock(IncidentRule).should_receive('query.all').and_return(
            unit_test_fixtures.rule_1)

        returned = controller.get_incident_rules(datasource_uuid, rule_id,
                                                 rule, active)
        assert returned == unit_test_fixtures.rule_2

    def test__get_online_status(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = unit_test_fixtures.data_source
        environment = 1
        environments = [environment]
        es_status = unit_test_fixtures.es_status1

        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)
        flexmock(ElasticSearchStatus).should_receive('query.order_by.first').and_return(es_status)

        should_return = 1
        returned = controller._get_online_status(environments, datasource_uuid)
        assert returned == should_return

    def test__get_incidenttype_severities(self):
        incident_types_found = 1
        severities = unit_test_fixtures.severities
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(IncidentSeverity).should_receive('_member_names_').and_return(
            severities)

        flexmock(IncidentType).should_receive('query.filter.count').and_return(
            0)

        should_return = unit_test_fixtures.get_severities
        returned = controller._get_incidenttype_severities(
            incident_types_found, datasource_uuid)
        assert returned == should_return

    def test__get_incident_severities(self):
        tickets_open = 1
        severities = unit_test_fixtures.severities
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        user = unit_test_fixtures.user

        flexmock(IncidentSeverity).should_receive('_member_names_').and_return(
            severities)

        flexmock(incident_controller).should_receive('get_incidents').and_return([])

        should_return = unit_test_fixtures.get_severities
        returned = controller._get_incident_severities(user, tickets_open,
                                                       datasource_uuid)
        assert returned == should_return

    def test_get_data_sources_quick_view(self):
        Config.CURRENT_REFINEMENTS = []
        Config.CURRENT_MAPPINGS = {}
        data_source = unit_test_fixtures.data_source
        datasource_uuid = data_source.uuid
        data_source_dict = unit_test_fixtures.data_source_dict
        user = unit_test_fixtures.user
        environment = unit_test_fixtures.environment_dict
        environments = [environment]
        query = Query
        severities = unit_test_fixtures.get_severities
        model = unit_test_fixtures.proctor_model

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_data_sources_quick_view(user, datasource_uuid)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return(environments)

        flexmock(controller).should_receive('_get_online_status').and_return(1)

        flexmock(IncidentType).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('count').and_return(1)

        flexmock(Query).should_receive('filter.count').and_return(0)

        flexmock(controller).should_receive(
            '_get_incidenttype_severities').and_return(severities)

        flexmock(Incident).should_receive('query.filter').and_return(query)

        flexmock(Query).should_receive('filter.count').and_return(1)

        flexmock(controller).should_receive(
            '_get_incident_severities').and_return(severities)

        flexmock(ProctorModel).should_receive('query.filter.first').and_return(
            model)

        flexmock(controller).should_receive('source_to_dict').and_return(
            data_source_dict)

        should_return = unit_test_fixtures.ds_quick_view
        returned = controller.get_data_sources_quick_view(
            user, datasource_uuid)
        assert returned == should_return

        # offline
        flexmock(controller).should_receive('_get_online_status').and_return(0)

        should_return['current_status'] = 'offline'
        should_return['environments']['offlineEnvironments'] = 1
        should_return['environments']['onlineEnvironments'] = 0
        returned = controller.get_data_sources_quick_view(
            user, datasource_uuid)
        assert returned == should_return

        # connecting
        flexmock(controller).should_receive('_get_online_status').and_return(1)

        flexmock(ProctorModel).should_receive('query.filter.first').and_return(
            None)

        should_return['current_status'] = 'connecting'
        should_return['environments']['offlineEnvironments'] = 0
        should_return['environments']['onlineEnvironments'] = 1
        returned = controller.get_data_sources_quick_view(
            user, datasource_uuid)
        assert returned == should_return

    def test_get_environment_quick_view(self):
        data_source = unit_test_fixtures.data_source
        datasource_uuid = data_source.uuid
        user = unit_test_fixtures.user
        environment_id = 1
        environment_dict = unit_test_fixtures.environment_dict
        query = Query
        severities = unit_test_fixtures.get_severities

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_environment_quick_view(user, datasource_uuid,
                                                  environment_id)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive('get_environment').and_return(
            environment_dict)

        # flexmock(Incident).should_receive('query.filter').and_return(query)
        #
        # flexmock(Query).should_receive('filter.count').and_return(1)

        flexmock(incident_controller).should_receive('get_incidents').and_return([1]).and_return([1]).and_return([])

        flexmock(controller).should_receive(
            '_get_incident_severities').and_return(severities)

        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)

        should_return = unit_test_fixtures.env_quick_view
        returned = controller.get_environment_quick_view(
            user, datasource_uuid, environment_id)
        assert returned == should_return

    @patch('requests.post')
    def test__check_ds_env_connection(self, mocked_post):
        return_value = unit_test_fixtures.check_sequence_response
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = return_value
        ds_body = {}

        response = controller._check_ds_env_connection(ds_body)
        mocked_post.assert_called_with(
            f'http://cerebro-proctor:80/proctor/check_datasource',
            json=ds_body)
        self.assertEqual(response.status_code, 200)

    def test_check_connection(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        response_200 = unit_test_fixtures.response_200
        body = {}

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.check_connection(user, datasource_uuid, body)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.check_connection(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(controller).should_receive(
            '_check_ds_env_connection').and_return(response_200)

        should_return = unit_test_fixtures.connection_status
        returned = controller.check_connection(user, datasource_uuid, body)
        assert returned == should_return

    def test_datasource_create_validation(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        data_sources = [data_source]
        settings = unit_test_fixtures.setting
        img = 'imagen'
        body = {}

        # unauthorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.datasource_create_validation(user, body, img)
        except error.Forbidden:
            pass

        # None values
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        try:
            controller.datasource_create_validation(user, body, img)
        except error.BadRequest:
            pass

        body = {
            'display_name': 'display_name',
            'es_host': 'es_host',
            'es_port': 'es_port',
            'es_user': 'es_user',
            'es_password': 'es_password',
            'owner': 'owner',
            'env_display_name': 'env_display_name',
            'features': 'features',
            'index_name': 'index_name'
        }

        flexmock(DataSource).should_receive('query.all').and_return(
            data_sources)

        flexmock(CerebroSettings).should_receive('query.first').and_return(
            settings)

        flexmock(controller).should_receive('convert_img').and_return(img)

        try:
            controller.datasource_create_validation(user, body, img)
        except error.BadRequest:
            pass

    def test_create_data_source(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        display_name = data_source.display_name
        es_user = data_source.es_user
        es_password = data_source.es_password
        es_host = data_source.es_host
        es_port = data_source.es_port
        mapping_blocked = 0
        img_src = copy.deepcopy(unit_test_fixtures.account_pic.img_src)
        data_source_dict = copy.deepcopy(unit_test_fixtures.data_source_dict)
        response = unit_test_fixtures.response_200

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(db.session).should_receive('add').and_return(data_source)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('source_to_dict')\
            .and_return(data_source_dict)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        uuid = None
        owner = None
        public = 0
        shared = 0
        status = 'connecting'

        data_source = DataSource(display_name=display_name,
                                 es_host=es_host,
                                 es_port=es_port,
                                 es_user=es_user,
                                 es_password=es_password,
                                 mapping_blocked=mapping_blocked,
                                 uuid=uuid,
                                 owner=owner,
                                 public=public,
                                 shared=shared,
                                 datasource_icon=img_src,
                                 status=status)

        flexmock(controller).should_receive('source_to_dict')\
            .with_args(user, data_source=data_source, extended=True)\
            .and_return(data_source_dict)

        flexmock(controller).should_receive('_check_ds_env_connection')\
            .and_return(response)

        flexmock(controller).should_receive('get_and_spin_model')

        flexmock(controller).should_receive('create_environment')

        body = {
            "display_name": display_name,
            "es_user": es_user,
            "es_password": es_password,
            "es_host": es_host,
            "es_port": es_port,
            "mapping_blocked": 0
        }

        returned = controller.create_data_source(user, body, img_src)
        assert returned == data_source_dict

    def test_delete_datasource_validation(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        # no body
        body = {}
        flexmock(controller).should_receive('publish_message').and_return(
            False)

        try:
            controller.delete_datasource_validation(user, datasource_uuid,
                                                    body)
        except error.BadRequest:
            pass

        # no password
        body = {'user_password': None}

        try:
            controller.delete_datasource_validation(user, datasource_uuid,
                                                    body)
        except error.BadRequest:
            pass

        # bad password
        body = {'user_password': 'user_password'}

        flexmock(controller).should_receive('check_user_pass').and_return(
            False)

        try:
            controller.delete_datasource_validation(user, datasource_uuid,
                                                    body)
        except error.BadRequest:
            pass

        # no authorization
        flexmock(controller).should_receive('check_user_pass').and_return(True)

        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.delete_datasource_validation(user, datasource_uuid,
                                                    body)
        except error.Forbidden:
            pass

        # no datasource
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.delete_datasource_validation(user, datasource_uuid,
                                                    body)
        except error.NotFound:
            pass

    def test_delete_data_source(self):
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_dict = copy.deepcopy(unit_test_fixtures.data_source_dict)
        log_category = copy.deepcopy(unit_test_fixtures.log_category)
        log_categories = [log_category]
        solution = copy.deepcopy(unit_test_fixtures.incident_solution)
        solutions = [solution]
        datasource_uuid = data_source.uuid
        user = unit_test_fixtures.user

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([])

        flexmock(controller).should_receive('source_to_dict').and_return(
            data_source_dict)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(CategoryOccurrences).should_receive('query.filter.limit.all').and_return([])

        flexmock(controller).should_receive('delete_data_source_children')
        flexmock(solutions_controller).should_receive('delete_datasource_saio')
        flexmock(ProctorTrainingData).should_receive('query.filter.limit.all').and_return([])

        # flexmock(Alert).should_receive('query.filter.limit.all').and_return([]).and_return([])
        flexmock(Alert).should_receive('query.filter.all').and_return([])

        flexmock(AlertsHistory).should_receive('query.filter.limit.all').and_return([])

        flexmock(PrometheusAlert).should_receive('query.filter.all').and_return([])

        flexmock(EscalationPolicy).should_receive('query.filter.all').and_return([])

        flexmock(EscalationHistory).should_receive('query.filter.limit.all').and_return([])

        flexmock(APIReaction).should_receive('query.filter.limit.all').and_return([])

        flexmock(SSHReaction).should_receive('query.filter.limit.all').and_return([])

        flexmock(Reaction).should_receive('query.filter.limit.all').and_return([])

        # flexmock(LogCategory).should_receive('query.filter.limit.all').and_return(
        #     log_categories).and_return([])
        flexmock(LogCategory).should_receive('query.filter.all').and_return(
            log_categories)

        flexmock(Signature).should_receive('query.get')

        flexmock(IncidentStateEvent).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentOwnershipEvent).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentTypeRefinementEvent).should_receive(
            'query.filter.limit.all').and_return([])

        flexmock(IncidentTypeSeverityEvent).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentTypeLabelEvent).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidenttypeHistory).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentExternalSolution).should_receive('query.filter.limit.all').and_return([])

        # flexmock(IncidentSolution).should_receive(
        #     'query.filter.limit.all').and_return(solutions).and_return([])
        flexmock(IncidentSolution).should_receive(
            'query.filter.all').and_return(solutions)

        # flexmock(FlagSolution).should_receive('query.filter.limit.all').and_return([])
        flexmock(FlagSolution).should_receive('query.filter.all')

        # flexmock(IncidentSolutionComments).should_receive('query.filter.limit.all').and_return([])
        flexmock(IncidentSolutionComments).should_receive('query.filter.all')

        flexmock(ElasticSearchStatus).should_receive('query.filter.limit.all').and_return([])

        flexmock(ESHourStatus).should_receive('query.filter.limit.all').and_return([])

        flexmock(ESDayStatus).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentRule).should_receive('query.filter.limit.all').and_return([])

        flexmock(IncidentResponse).should_receive('query.filter.limit.all').and_return([])

        flexmock(Incident).should_receive('query.filter.limit.all').and_return([])

        # flexmock(IncidentType).should_receive('query.filter.limit.all').and_return([])
        flexmock(IncidentType).should_receive('query.filter.all')

        flexmock(IncidentTypeCommonWords).should_receive('query.get')

        flexmock(Environment).should_receive('query.filter.limit.all').and_return([])

        # flexmock(DSShare).should_receive('query.filter.limit.all').and_return([])
        flexmock(DSShare).should_receive('query.filter.all')

        flexmock(ProctorModel).should_receive('query.filter.limit.all').and_return([])

        flexmock(CerebroAgent).should_receive('query.filter.limit.all').and_return([])

        flexmock(HelpdeskEmail).should_receive('query.filter.limit.all').and_return([])

        flexmock(HelpdeskServer).should_receive('query.filter.limit.all').and_return([])

        flexmock(controller).should_receive('delete_data_source_children').and_return(True)

        should_return = None
        returned = controller.delete_data_source(user, datasource_uuid)
        assert returned == should_return

        # no data_source
        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        try:
            controller.delete_data_source(user, datasource_uuid)
        except smarty.errors.NoSuchObject:
            pass

    def test_delete_data_source_children(self):
        child_list = [copy.deepcopy(unit_test_fixtures.incident)]

        should_return = True
        returned = controller.delete_data_source_children(child_list)
        assert returned == should_return

    def test_update_data_source_validation(self):
        user = unit_test_fixtures.user
        img = 'image'
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.update_data_source_validation(user, img,
                                                     datasource_uuid, body, 'token')
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            None)

        flexmock(controller).should_receive('convert_img').and_return(img)

        try:
            controller.update_data_source_validation(user, img,
                                                     datasource_uuid, body, 'token')
        except smarty.errors.NoSuchObject:
            pass

    def test_update_data_source(self):
        user = unit_test_fixtures.user
        data_source = unit_test_fixtures.data_source
        data_source_dict = unit_test_fixtures.data_source_dict
        datasource_uuid = data_source.uuid
        body = unit_test_fixtures.data_source_dict
        body["es_host"] = 'url or IP address'
        body["es_port"] = 'port'
        body["es_user"] = 'user'
        body["es_password"] = 'password'

        img_src = unit_test_fixtures.account_pic.img_src

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('source_to_dict').and_return(
            data_source_dict)

        flexmock(controller).should_receive('publish_message')\
            .and_return(False)

        returned = controller.update_data_source(user, img_src,
                                                 datasource_uuid, body, 'token')
        assert returned == data_source_dict

        body["mapping_blocked"] = 1

        returned = controller.update_data_source(user, img_src,
                                                 datasource_uuid, body, 'token')
        assert returned == data_source_dict

    def test_upload_datasource_icon(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_dict = unit_test_fixtures.data_source_dict
        datasource_uuid = data_source.uuid
        img = 'image'
        img_src = unit_test_fixtures.account_pic.img_src

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.upload_datasource_icon(user, datasource_uuid, img_src)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(controller).should_receive('convert_img').and_return(img)

        flexmock(DataSource).should_receive('query.update').and_return(
            data_source)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('source_to_dict').and_return(
            data_source_dict)

        should_return = {
            'datasource_icon': 'image',
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        }
        returned = controller.upload_datasource_icon(user, datasource_uuid,
                                                     img_src)
        assert returned == should_return

    def test_convert_img(self):
        file = unit_test_fixtures.img_jpeg
        try:
            controller.convert_img(file)
        except:
            pass

        file = unit_test_fixtures.img_png
        try:
            controller.convert_img(file)
        except:
            pass

        file = unit_test_fixtures.img_svg
        try:
            controller.convert_img(file)
        except:
            pass

        file = unit_test_fixtures.file
        try:
            controller.convert_img(file)
        except:
            pass

    def test_get_datasource_icon(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_2 = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_2.datasource_icon = None
        datasource_uuid = data_source.uuid

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_datasource_icon(user, datasource_uuid)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        should_return = {
            'datasource_icon': 'xxx',
            'uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
        }
        returned = controller.get_datasource_icon(user, datasource_uuid)
        assert returned == should_return

        # none img
        flexmock(DataSource).should_receive('query.first').and_return(
            data_source_2)

        should_return = None
        returned = controller.get_datasource_icon(user, datasource_uuid)
        assert returned == should_return

    def test_check_datasource_env(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_2 = copy.deepcopy(unit_test_fixtures.data_source)
        data_source_2.datasource_icon = None
        datasource_uuid = data_source.uuid
        env_alert = [1]

        # empty list
        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return([])

        try:
            controller.check_datasource_env(user, datasource_uuid, env_alert)
        except error.BadRequest:
            pass

        flexmock(controller).should_receive(
            'get_environments_by_datasource').and_return(env_alert)

        should_return = None
        returned = controller.check_datasource_env(user, datasource_uuid,
                                                   env_alert)
        assert returned == should_return

    def test_get_data_source_share(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        ds_share = unit_test_fixtures.ds_share
        ds_shares = [ds_share]
        role = unit_test_fixtures.role

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_data_source_share(user, datasource_uuid)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(None)

        try:
            controller.get_data_source_share(user, datasource_uuid)
        except error.BadRequest:
            pass

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(DSShare).should_receive('query.filter.all').and_return(
            ds_shares)

        flexmock(User).should_receive('query.filter.first').and_return(user)

        flexmock(Role).should_receive('query.filter.first').and_return(role)

        should_return = unit_test_fixtures.ds_share_response
        returned = controller.get_data_source_share(user, datasource_uuid)
        assert returned == should_return

    def test_data_source_share_with(self):
        user = unit_test_fixtures.user
        user_dict = unit_test_fixtures.user_dict
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        ds_share = copy.deepcopy(unit_test_fixtures.ds_share)
        role = unit_test_fixtures.role
        roles = unit_test_fixtures.roles
        body = {
            'role_name': 'Administrator',
            'datasource_uuid': datasource_uuid,
            'user_email': "test@email.com",
            'user_id': '1'
        }

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.data_source_share_with(user, datasource_uuid, body)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(None)

        try:
            controller.data_source_share_with(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        # no role
        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(controller).should_receive('get_roles').and_return([])

        try:
            controller.data_source_share_with(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        # already shared
        flexmock(controller).should_receive('get_roles').and_return(roles)

        flexmock(controller).should_receive('get_user_by_email').and_return(
            user_dict)

        flexmock(DSShare).should_receive('query.filter.first').and_return(
            ds_share)

        try:
            controller.data_source_share_with(user, datasource_uuid, body)
        except error.BadRequest:
            pass

        flexmock(DSShare).should_receive('query.filter.first').and_return(None)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(Role).should_receive('query.filter.first').and_return(role)

        flexmock(DSShare).should_receive('add')

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive(
            'get_data_source_share').and_return(ds_share)

        should_return = ds_share
        returned = controller.data_source_share_with(user, datasource_uuid,
                                                     body)
        assert returned == should_return

    def test_update_data_source_share_with(self):
        user = unit_test_fixtures.user
        user_dict = unit_test_fixtures.user_dict
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        ds_share = copy.deepcopy(unit_test_fixtures.ds_share)
        role = unit_test_fixtures.role
        roles = unit_test_fixtures.roles
        body = {'role': 'Administrator', 'datasource_uuid': datasource_uuid}

        # no issues
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(controller).should_receive('get_roles').and_return(roles)

        flexmock(controller).should_receive('get_user_by_email').and_return(
            user_dict)

        flexmock(Role).should_receive('query.filter.first').and_return(role)

        flexmock(DSShare).should_receive('query.filter.first')\
            .and_return(None).and_return(ds_share)

        flexmock(controller).should_receive(
            'get_data_source_share').and_return(ds_share)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(db.session).should_receive('commit')

        should_return = ds_share
        returned = controller.update_data_source_share_with(
            user, datasource_uuid, body)
        assert returned == should_return

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.update_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(None)

        try:
            controller.update_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.BadRequest:
            pass

        # no role
        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(controller).should_receive('get_roles').and_return([])

        try:
            controller.update_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.BadRequest:
            pass

        # nothing to update
        flexmock(controller).should_receive('get_roles').and_return(roles)

        flexmock(controller).should_receive('get_user_by_email').and_return(
            user_dict)

        flexmock(Role).should_receive('query.filter.first').and_return(role)

        flexmock(DSShare).should_receive('query.filter.first').and_return(
            ds_share)

        try:
            controller.update_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.BadRequest:
            pass

        # no shared
        flexmock(DSShare).should_receive('query.filter.first').and_return(None)

        try:
            controller.update_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.NotFound:
            pass

    def test_delete_data_source_share_with(self):
        user = unit_test_fixtures.user
        user_dict = unit_test_fixtures.user_dict
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        ds_share = copy.deepcopy(unit_test_fixtures.ds_share)
        body = {'datasource_uuid': datasource_uuid}

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.delete_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.Forbidden:
            pass

        # no ds_share
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(controller).should_receive('get_user_by_email').and_return(
            user_dict)

        flexmock(DSShare).should_receive('query.filter.first').and_return(None)

        try:
            controller.delete_data_source_share_with(user, datasource_uuid,
                                                     body)
        except error.NotFound:
            pass

        flexmock(DSShare).should_receive('query.filter.first').and_return(
            ds_share)

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(db.session).should_receive('commit')

        should_return = None
        returned = controller.delete_data_source_share_with(
            user, datasource_uuid, body)
        assert returned == should_return

        # exception
        flexmock(db.session).should_receive('commit').and_raise(Exception)

        flexmock(db.session).should_receive('rollback')

        try:
            controller.delete_data_source_share_with(user, datasource_uuid,
                                                     body)
        except smarty.errors.DeletionFail:
            pass

    @patch('requests.get')
    def test_datasource_index_search(self, mocked_get):
        elk_nodes = unit_test_fixtures.elk_nodes
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = elk_nodes
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        list_elk_node = unit_test_fixtures.list_elk_node

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.datasource_index_search(user, datasource_uuid)
        except error.Forbidden:
            pass

        # no data source
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(DataSource).should_receive('query.first').and_return(None)

        try:
            controller.datasource_index_search(user, datasource_uuid)
        except error.NotFound:
            pass

        flexmock(controller).should_receive('publish_message').and_return(
            False)

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        should_return = list_elk_node
        returned = controller.datasource_index_search(user, datasource_uuid)
        assert returned == should_return

    def test_datasource_index_search_inuse(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        environment = unit_test_fixtures.environment
        environments = [environment]

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(Environment).should_receive('query.filter.all').and_return(
            environments)

        should_return = ['uat_cluster:flog-*']
        returned = controller.datasource_index_search_inuse(
            user, datasource_uuid)
        assert returned == should_return

    def test_datasource_index_search_unused(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid
        list_elk_node = unit_test_fixtures.list_elk_node

        flexmock(DataSource).should_receive('query.filter.first').and_return(
            data_source)

        flexmock(controller).should_receive(
            'datasource_index_search').and_return(list_elk_node)

        flexmock(controller).should_receive(
            'datasource_index_search_inuse').and_return(['uat_cluster:flog-*'])

        flexmock(controller).should_receive(
            'validate_capability').and_return(True)

        should_return = set(list_elk_node) - set(['uat_cluster:flog-*'])
        returned = controller.datasource_index_search_unused(
            user, datasource_uuid)
        assert returned == list(should_return)

    def test_datasource_connect_unused(self):
        user = unit_test_fixtures.user
        data_source = copy.deepcopy(unit_test_fixtures.data_source)
        datasource_uuid = data_source.uuid

        flexmock(controller).should_receive(
            'datasource_index_search_unused').and_return([])

        flexmock(controller).should_receive(
            'validate_capability').and_return(True)

        should_return = None
        returned = controller.datasource_connect_unused(user, datasource_uuid)
        assert returned == should_return

    def test_set_cerebro_settings(self):
        user = unit_test_fixtures.user
        setting = copy.deepcopy(unit_test_fixtures.setting)
        settings_dict = unit_test_fixtures.settings_dict
        settings = [setting]
        package = 'package'

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.set_cerebro_settings(user, package)
        except error.Forbidden:
            pass

        # no valid package
        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        try:
            controller.set_cerebro_settings(user, package)
        except error.BadRequest:
            pass

        # valid package
        package = 'premium'

        flexmock(CerebroSettings).should_receive('query.all').and_return(
            settings)

        flexmock(db.session).should_receive('commit')

        flexmock(controller).should_receive('settings_to_dict').and_return(
            settings_dict)

        should_return = settings_dict
        returned = controller.set_cerebro_settings(user, package)
        assert returned == should_return

        # no setting
        flexmock(CerebroSettings).should_receive('query.all').and_return([])

        flexmock(CerebroSettings).should_receive('add')

        should_return = settings_dict
        returned = controller.set_cerebro_settings(user, package)
        assert returned == should_return

    def test_get_cerebro_settings(self):
        user = unit_test_fixtures.user
        setting = copy.deepcopy(unit_test_fixtures.setting)
        settings_dict = unit_test_fixtures.settings_dict
        settings = [setting]

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_cerebro_settings(user)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(CerebroSettings).should_receive('query.all').and_return(
            settings)

        flexmock(controller).should_receive('settings_to_dict').and_return(
            settings_dict)

        should_return = settings_dict
        returned = controller.get_cerebro_settings(user)
        assert returned == should_return

    def test_get_all_env_features(self):
        user = unit_test_fixtures.user
        env_feature = copy.deepcopy(unit_test_fixtures.env_feature)
        env_features = [env_feature]

        # no authorized
        flexmock(controller).should_receive('validate_capability').and_return(
            False)

        try:
            controller.get_all_env_features(user)
        except error.Forbidden:
            pass

        flexmock(controller).should_receive('validate_capability').and_return(
            True)

        flexmock(EnvFeatures).should_receive('query.all').and_return(
            env_features)

        should_return = [env_feature.env_feature]
        returned = controller.get_all_env_features(user)
        assert returned == should_return
