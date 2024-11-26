import os
from unittest import TestCase

from flexmock import flexmock

from smarty import utils as smarty_utils
from smarty.app import create_app
from smarty.domain.models import DataSource
from smarty.domain.models import Environment
from smarty.domain.models import Incident
from smarty.domain.models import IncidentRating
from smarty.domain.models import IncidentType
from smarty.domain.models import User
from smarty.incidents import utils
from smarty.health_desk import controller as hd_controller
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestUtils(TestCase):
    def test__datetime_to_epoch_millis(self):
        date = unit_test_fixtures.datetime_datetime
        should_return = unit_test_fixtures.epoch_micros

        returned_epoch_millis = smarty_utils.datetime_to_epoch_micros(date)
        assert returned_epoch_millis == should_return

    def test__epoch_micros_to_datetime(self):
        epoch_micros = unit_test_fixtures.epoch_micros
        should_return = unit_test_fixtures.datetime_datetime

        returned_date = smarty_utils.epoch_micros_to_datetime(epoch_micros)
        assert returned_date == should_return

    def test__epoch_millis_to_datetime(self):
        epoch_millis = unit_test_fixtures.epoch_millis
        should_return = unit_test_fixtures.datetime_datetime

        returned_date = smarty_utils.epoch_millis_to_datetime(epoch_millis)
        assert returned_date == should_return

    def test_incident_to_dict(self):
        user = unit_test_fixtures.user
        incident = unit_test_fixtures.incident
        state_event_dict = unit_test_fixtures.state_event_dict
        should_return = unit_test_fixtures.incident_dict
        incident_type = unit_test_fixtures.incident_type
        data_source = unit_test_fixtures.data_source
        role_dict = unit_test_fixtures.role_dict
        permission_dict = unit_test_fixtures.permission_dict
        environment = unit_test_fixtures.environment

        flexmock(utils).should_receive('_incident_state_event_to_dict')\
            .and_return(state_event_dict)

        flexmock(utils).should_receive('_incident_ownership_event_to_dict')\
            .and_return()

        flexmock(IncidentType).should_receive('query.get')\
            .with_args(incident.it_id).and_return(incident_type)

        flexmock(DataSource).should_receive('query.first').and_return(
            data_source)

        flexmock(utils).should_receive('get_role').and_return(role_dict)

        flexmock(utils).should_receive('get_role_and_permissions').and_return(
            permission_dict)

        flexmock(Environment).should_receive('query.first').and_return(
            environment)

        flexmock(User).should_receive('query.get').and_return(None)

        flexmock(utils).should_receive('get_env_agent').and_return({})

        flexmock(hd_controller).should_receive('get_unreplied').and_return({})

        flexmock(IncidentRating).should_receive('query.filter.order_by.first').and_return(None)
        
        flexmock(utils).should_receive('get_incident_rating').and_return(None)

        flexmock(utils).should_receive('get_pending_survey').and_return(None)

        flexmock(utils).should_receive('get_without_survey').and_return(False)

        flexmock(utils).should_receive('_event_history').and_return(should_return)

        returned = utils.incident_to_dict(user, incident)
        assert returned['incident_id'] == should_return['incident_id']

    def test_incident_type_to_dict(self):
        user = unit_test_fixtures.user
        incident_type = unit_test_fixtures.incident_type
        should_return = unit_test_fixtures.incident_type_dict
        data_source = unit_test_fixtures.data_source
        role_dict = unit_test_fixtures.role_dict
        permission_dict = unit_test_fixtures.permission_dict

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)
        flexmock(DataSource).should_receive('query.first').and_return(data_source)
        flexmock(utils).should_receive('get_role').and_return(role_dict)
        flexmock(utils).should_receive('get_role_and_permissions').and_return(permission_dict)
        flexmock(utils).should_receive('_get_log_archetypes').and_return([])

        returned = utils.incident_type_to_dict(user, incident_type)
        assert returned['incidenttype_id'] == should_return['incidenttype_id']

    def test__incident_state_event_to_dict(self):
        state_evt = unit_test_fixtures.state_event
        should_return = unit_test_fixtures.state_event_dict
        incident = unit_test_fixtures.incident

        flexmock(Incident).should_receive('query.get').and_return(incident)

        returned = utils._incident_state_event_to_dict(state_evt)
        assert returned == should_return

    def test__incident_type_label_event_to_dict(self):
        label_evt = unit_test_fixtures.label_event
        should_return = unit_test_fixtures.label_event_dict
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        returned = utils._incident_type_label_event_to_dict(label_evt)
        assert returned == should_return

    def test__incident_type_severity_event_to_dict(self):
        severity_evt = unit_test_fixtures.severity_event
        should_return = unit_test_fixtures.severity_event_dict
        incident_type = unit_test_fixtures.incident_type

        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)

        returned = utils._incident_type_severity_event_to_dict(severity_evt)
        assert returned == should_return

    def test__event_to_dict(self):
        # label event
        label_evt = unit_test_fixtures.label_event
        label_event_dict = unit_test_fixtures.label_event_dict

        flexmock(utils) \
            .should_receive('_incident_type_label_event_to_dict') \
            .with_args(label_evt) \
            .and_return(label_event_dict)

        returned = utils.event_to_dict(label_evt)
        assert returned == label_event_dict

        # state event
        state_evt = unit_test_fixtures.state_event
        state_event_dict = unit_test_fixtures.state_event_dict

        flexmock(utils) \
            .should_receive('_incident_state_event_to_dict') \
            .with_args(state_evt) \
            .and_return(state_event_dict)

        returned = utils.event_to_dict(state_evt)
        assert returned == state_event_dict

        # severity event
        severity_evt = unit_test_fixtures.severity_event
        severity_event_dict = unit_test_fixtures.severity_event_dict

        flexmock(utils) \
            .should_receive('_incident_type_severity_event_to_dict') \
            .with_args(severity_evt) \
            .and_return(severity_event_dict)

        returned = utils.event_to_dict(severity_evt)
        assert returned == severity_event_dict

        # type error
        wrong_evt = unit_test_fixtures.proctor_model

        try:
            returned = utils.event_to_dict(wrong_evt)
        except TypeError:
            pass
