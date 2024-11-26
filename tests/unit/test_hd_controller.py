from datetime import datetime
import copy
import os
import unittest

from flexmock import flexmock
from tests.fixtures import unit_test_fixtures

from smarty.app import create_app
from smarty.domain.models import HelpdeskCategory
from smarty.domain.models import Incident
from smarty.domain.models import IncidentRating
from smarty.domain.models import IncidentReport
from smarty.domain.models import IncidentResponse
from smarty.domain.models import IncidentStateEvent
from smarty.domain.models import IncidentType
from smarty.domain.models import ProctorTrainingData
from smarty.domain.models import User
from smarty.extensions import db
from smarty.health_desk import controller
from smarty.incidents import controller as incident_controller
from smarty.incidents import utils as incident_utils
from smarty.settings import Config
from smarty.solutions import controller as sol_controller

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestControllerHealthDesk(unittest.TestCase):
    def setup_class(self):
        self.controller = controller

    def test_get_report(self):
        current_user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {'new_report': '1'}
        should_return = []

        flexmock(incident_controller).should_receive('get_incidents').and_return([])

        flexmock(controller).should_receive('get_incident_report').and_return([])

        flexmock(controller).should_receive('get_full_report').and_return([])

        returned = controller.get_report(current_user, datasource_uuid, body)
        assert returned == should_return

    def test_get_full_report(self):
        current_user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}
        should_return = {'dashboard': None, 'report_object': None}

        flexmock(incident_controller).should_receive('get_incidents').and_return([])
        flexmock(controller).should_receive('gen_excel_report').and_return({})

        returned = controller.get_full_report(current_user, datasource_uuid, body, {})
        assert returned == should_return

    def test_get_dashboard_last_day(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        env_id = 1
        incidents = [unit_test_fixtures.incident]
        should_return = unit_test_fixtures.dashboard_last_day

        flexmock(incident_controller).should_receive('get_incidents').and_return(incidents)

        returned = controller.get_dashboard_last_day(user, datasource_uuid, env_id)
        assert returned == should_return

    def test_create_incident_report(self):
        user = unit_test_fixtures.user
        incident = unit_test_fixtures.incident
        i_response = unit_test_fixtures.incident_response
        should_return = i_response

        flexmock(User).should_receive('query.get').and_return(user)
        flexmock(IncidentReport).should_receive('add')
        flexmock(db.session).should_receive('commit')
        flexmock(controller).should_receive('get_active_time').and_return(None)

        returned = controller.create_incident_report(incident, i_response)
        assert returned == should_return

    def test_get_active_time(self):
        incident = unit_test_fixtures.incident
        i_s_event = unit_test_fixtures.incident_state_event
        should_return = '1688d, 23h, 36m'

        flexmock(IncidentStateEvent).should_receive('query.filter.all').and_return([i_s_event])
        flexmock(controller).should_receive('get_delta_ts').and_return(should_return)

        returned = controller.get_active_time(incident)
        assert returned == should_return

        flexmock(IncidentStateEvent).should_receive('query.filter.all').and_return([i_s_event, i_s_event])

        returned = controller.get_active_time(incident)
        assert returned == should_return

    def test_get_delta_ts(self):
        delta = None
        should_return = delta

        returned = controller.get_delta_ts(delta)
        assert returned == should_return

        delta = unit_test_fixtures.end_date2 - unit_test_fixtures.datetime_datetime
        should_return = '0d, 19h, 0m'

        returned = controller.get_delta_ts(delta)
        assert returned == should_return

    def test_update_incident_report(self):
        i_report = unit_test_fixtures.incident_report
        i_response = unit_test_fixtures.incident_response
        incident = unit_test_fixtures.incident
        should_return = None

        flexmock(controller).should_receive('get_active_time').and_return(None)

        returned = controller.update_incident_report(i_report, i_response, incident)
        assert returned == should_return

    def test_get_incident_report(self):
        i_report = unit_test_fixtures.incident_report
        i_response = unit_test_fixtures.incident_response
        report = []
        incidents = [unit_test_fixtures.incident]
        should_return = [unit_test_fixtures.incident_report_dict]

        flexmock(IncidentReport).should_receive('query.get').and_return(i_report)
        flexmock(controller).should_receive('get_incident_response').and_return(i_response, i_report)
        flexmock(controller).should_receive('time_last_comm').and_return(None)
        flexmock(IncidentRating).should_receive('query.filter.order_by.first').and_return(None)
        flexmock(incident_utils).should_receive('get_incident_rating').and_return(None)
        flexmock(incident_utils).should_receive('get_pending_survey').and_return(None)
        flexmock(Incident).should_receive('query.get').and_return(None)
        flexmock(controller).should_receive('get_active_time').and_return(None)
        flexmock(incident_utils).should_receive('get_hd_category').and_return('Unknown')
        flexmock(incident_utils).should_receive('get_hd_subcategory').and_return('Unknown')
        flexmock(controller).should_receive('i_report_dict').and_return(should_return[0])

        returned = controller.get_incident_report(report, incidents, 'dict')
        assert returned == should_return

    def test_i_report_json(self):
        incident = unit_test_fixtures.incident
        incident_type = copy.deepcopy(unit_test_fixtures.incident_type)
        # incident_type.type_history = []
        incident_report = unit_test_fixtures.incident_report
        time_last_comm_str = incident_report.last_communication_date_str
        should_return = unit_test_fixtures.report_json
        Config.RESOLUTION_TIME = {
            'unknown': 15
        }
        flexmock(controller).should_receive('time_last_comm').and_return(time_last_comm_str)
        flexmock(Incident).should_receive('query.get').and_return(incident)
        flexmock(IncidentType).should_receive('query.get').and_return(incident_type)
        flexmock(controller).should_receive('get_active_time').and_return(None)
        flexmock(incident_utils).should_receive('get_hd_category').and_return('Unknown')
        flexmock(incident_utils).should_receive('get_hd_subcategory').and_return('Unknown')

        returned = controller.i_report_json(incident_report)
        assert returned == should_return

        Config.RESOLUTION_TIME = {}

    def test_time_last_comm(self):
        incident_report = unit_test_fixtures.incident_report
        incident_response = unit_test_fixtures.incident_response

        flexmock(IncidentResponse).should_receive('query.get').and_return(incident_response)

        returned = controller.time_last_comm(incident_report)
        assert isinstance(returned, str)

    def test_gen_excel_report(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        report = [unit_test_fixtures.incident_report_dict]
        should_return = unit_test_fixtures.excel_report

        flexmock(controller).should_receive('get_minutes').and_return(0)
        flexmock(sol_controller).should_receive('put_report_saio').and_return({})
        flexmock(Incident).should_receive('query.get').and_return(None)
        flexmock(controller).should_receive('get_active_time').and_return(None)
        flexmock(controller).should_receive('get_age_time').and_return(None)
        flexmock(HelpdeskCategory).should_receive('query.all').and_return([])

        returned = controller.gen_excel_report(datasource_uuid, report)
        assert returned == should_return

    def test_get_minutes(self):
        time_str = '1d, 1h, 1m'
        should_return = 1501

        returned = controller.get_minutes(time_str)
        assert returned == should_return

    def test_get_unreplied(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        i_response = [unit_test_fixtures.incident_response]
        should_return = {}

        flexmock(IncidentResponse).should_receive('query.filter.all').and_return(i_response)

        returned = controller.get_unreplied(datasource_uuid)
        assert returned == should_return

    def test_is_unreplied(self):
        incident = unit_test_fixtures.incident
        delay = 1
        i_report = unit_test_fixtures.incident_report
        i_response = unit_test_fixtures.incident_response
        should_return = False

        flexmock(controller).should_receive('get_incident_response').and_return(i_response, i_report)

        returned = controller.is_unreplied(incident, delay)
        assert returned == should_return

    def test_get_incident_response(self):
        incident = unit_test_fixtures.incident
        i_report = unit_test_fixtures.incident_report
        i_response = unit_test_fixtures.incident_response
        should_return = i_response, i_report

        flexmock(IncidentResponse).should_receive('query.get').and_return(i_response)

        flexmock(IncidentReport).should_receive('query.get').and_return(i_report)

        returned = controller.get_incident_response(incident)
        assert returned == should_return

        flexmock(IncidentReport).should_receive('query.get').and_return(None)

        flexmock(controller).should_receive('create_incident_report').and_return(i_report)

        returned = controller.get_incident_response(incident)
        assert returned == should_return

        # training_data = [unit_test_fixtures.training_datum]

        # flexmock(IncidentResponse).should_receive('query.get').and_return(None)

        # flexmock(IncidentReport).should_receive('query.get').and_return(None)

        # flexmock(ProctorTrainingData).should_receive('query.filter.all').and_return(training_data)

        # flexmock(IncidentResponse).should_receive('add')

        # flexmock(db.session).should_receive('commit')

        # flexmock(controller).should_receive('create_incident_report').and_return(i_report)

        # returned = controller.get_incident_response(incident)
        # assert isinstance(returned[0], IncidentResponse)
        # assert returned[1] == should_return[1]

    def test__get_last_(self):
        incident = unit_test_fixtures.incident
        last_raw = ''
        option = ''
        should_return = None

        returned = controller._get_last_(incident, last_raw, option)
        assert returned == should_return

        last_raw = unit_test_fixtures.end_date2

        try:
            returned = controller._get_last_(incident, last_raw, option)
        except:
            pass

    def test__get_closed(self):
        incident = unit_test_fixtures.incident
        should_return = None

        returned = controller._get_closed(incident)
        assert returned == should_return

        incident.is_open = 0
        i_s_event = unit_test_fixtures.incident_state_event

        flexmock(IncidentStateEvent).should_receive('query.filter.all').and_return([i_s_event])

        try:
            returned = controller._get_closed(incident)
        except:
            pass
        incident.is_open = 1

    def test_get_on_alert(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident_response = [unit_test_fixtures.incident_response]
        should_return = {}

        flexmock(IncidentResponse).should_receive('query.filter.all').and_return(incident_response)

        returned = controller.get_on_alert(datasource_uuid)
        assert returned == should_return

    def test_sent_alert(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}
        should_return = True

        flexmock(incident_utils).should_receive('notify_current_owner').and_return(True)

        returned = controller.sent_alert(user, datasource_uuid, body)
        assert returned == should_return

    def test_escalate_ticket(self):
        user = unit_test_fixtures.user
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        incident_id = incident.incident_id
        should_return = True

        flexmock(controller).should_receive('get_user_to_notify').and_return(user, incident)
        flexmock(incident_utils).should_receive('notify_users').and_return(True)

        returned = controller.escalate_ticket(user, datasource_uuid, incident_id)
        assert returned == should_return

    def test_reply_msg(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        incident = unit_test_fixtures.incident
        i_id = incident.incident_id
        body = {}
        files = {}
        text = 'An email body'
        msg_id = 'msg_id'
        subject = 'subject'
        datum = unit_test_fixtures.training_datum
        message = 'message'
        imap_msg = 'imap_msg'
        should_return = False

        flexmock(controller).should_receive('_validate_msg').and_return(text, datum)
        flexmock(controller).should_receive('get_msg_id').and_return(msg_id, subject)
        flexmock(controller).should_receive('create_message').and_return(message)
        flexmock(controller).should_receive('_response').and_return(False).and_return(1)
        flexmock(controller).should_receive('get_msg_header').and_return(imap_msg)
        flexmock(controller).should_receive('send_email_reply').and_return(False)
        flexmock(Incident).should_receive('query.filter.first').and_return(incident)
        flexmock(incident_controller).should_receive('_add_incident_event')

        returned = controller.reply_msg(user, ds_uuid, i_id, body, files)
        assert returned == should_return
