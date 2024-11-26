import os
from unittest import TestCase

from flexmock import flexmock

from smarty import utils
from smarty.app import create_app
from smarty.domain.models import Incident
from smarty.proctor import views as proctor_views
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestViews(TestCase):
    def setup_class(self):
        self.views = proctor_views

    def test__datetime_to_epoch_millis(self):
        date = unit_test_fixtures.datetime_datetime
        should_return = unit_test_fixtures.epoch_millis

        returned_epoch_millis = utils.datetime_to_epoch_millis(date)
        assert returned_epoch_millis == should_return

    def test__epoch_millis_to_datetime(self):
        epoch_millis = unit_test_fixtures.epoch_millis
        should_return = unit_test_fixtures.datetime_datetime

        returned_date = utils.epoch_millis_to_datetime(epoch_millis)
        assert returned_date == should_return

    def test__rules_to_dict(self):
        rule = unit_test_fixtures.rule_1
        should_return = unit_test_fixtures.rule_dict

        returned = self.views._rules_to_dict(rule)
        assert returned == should_return

    def test__rule_to_short_dict(self):
        rule = unit_test_fixtures.rule_1
        should_return = unit_test_fixtures.rule_short_dict

        returned = self.views._rule_to_short_dict(rule)
        assert returned == should_return

    def test__training_datum_to_short_dict(self):
        training_datum = unit_test_fixtures.training_datum
        should_return = unit_test_fixtures.training_datum_short_dict
        incident = unit_test_fixtures.incident

        flexmock(Incident).should_receive('query.get').and_return(incident)

        returned = self.views.training_datum_to_short_dict(training_datum)
        assert returned == should_return

    def test__training_sequence_to_full_dict(self):
        training_datum = unit_test_fixtures.training_datum
        should_return = unit_test_fixtures.training_sequence_full_dict
        incident = unit_test_fixtures.incident

        flexmock(Incident).should_receive('query.get').and_return(incident)

        returned = self.views._training_sequence_to_full_dict(training_datum)
        assert returned == should_return

    def test__training_sequence_to_dict(self):
        training_datum = unit_test_fixtures.training_datum
        should_return = unit_test_fixtures.training_sequence_dict
        incident = unit_test_fixtures.incident

        flexmock(Incident).should_receive('query.get').and_return(incident)

        returned = self.views._training_sequence_to_dict(training_datum)
        assert returned == should_return

    def test_get_proctor_model(self):
        proctor_model = unit_test_fixtures.proctor_model
        should_return = unit_test_fixtures.proctor_model_dict
        proctormodel_id = 1
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.proctor_model_dict
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        current_user = unit_test_fixtures.proctor

        flexmock(proctor_views.controller) \
            .should_receive('get_proctor_model') \
            .with_args(proctormodel_id=proctormodel_id, datasource_uuid=datasource_uuid) \
            .and_return(proctor_model)

        flexmock(self.views).should_receive('get_proctor_model').and_return(
            should_response)

        returned = self.views.get_proctor_model(
            proctormodel_id=proctormodel_id)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_create_proctor_model(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_return = unit_test_fixtures.proctor_model_dict
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.proctor_model_dict

        data = {'foo': 'this is some text'}
        from werkzeug.test import EnvironBuilder
        builder = EnvironBuilder(method='POST', data=data)
        env = builder.get_environ()
        from werkzeug.wrappers import Request
        request = Request(env)

        flexmock() \
            .should_receive('request') \
            .and_return(request)

        flexmock(proctor_views.controller) \
            .should_receive('create_proctor_model') \
            .with_args(body=data, datasource_uuid=datasource_uuid) \
            .and_return(should_return)

        flexmock(self.views).should_receive('create_proctor_model').and_return(
            should_response)

        returned = self.views.create_proctor_model(
            datasource_uuid=datasource_uuid)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_get_log_categories(self):
        should_return = unit_test_fixtures.log_category_dict
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.log_category_dict

        flexmock(proctor_views.controller) \
            .should_receive('get_log_categories') \
            .with_args(datasource_uuid=datasource_uuid) \
            .and_return(should_return)

        flexmock(self.views).should_receive('get_log_categories').and_return(
            should_response)

        returned = self.views.get_log_categories(
            datasource_uuid=datasource_uuid)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_get_log_category(self):
        log_category = unit_test_fixtures.log_category
        should_return = unit_test_fixtures.log_category_dict
        category_id = 1
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.log_category_dict
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"

        flexmock(proctor_views.controller) \
            .should_receive('get_log_category') \
            .with_args(category_id=category_id, datasource_uuid=datasource_uuid) \
            .and_return(log_category)

        flexmock(self.views).should_receive('get_log_category').and_return(
            should_response)

        returned = self.views.get_log_category(category_id=category_id,
                                               datasource_uuid=datasource_uuid)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_get_incident_rules(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = unit_test_fixtures.rule_1
        rules = [rule]
        should_return = unit_test_fixtures.rule_dict
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.rule_dict

        flexmock(proctor_views) \
            .should_receive('get_incident_rules') \
            .with_args(datasource_uuid=datasource_uuid) \
            .and_return(rules)

        flexmock(proctor_views) \
            .should_receive('_rules_to_dict') \
            .with_args(rule) \
            .and_return(should_return)

        flexmock(self.views).should_receive('get_incident_rules').and_return(
            should_response)

        returned = self.views.get_incident_rules(
            datasource_uuid=datasource_uuid)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_get_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule = unit_test_fixtures.rule_1
        should_return = unit_test_fixtures.rule_dict
        should_response = unit_test_fixtures.response
        should_response.json = unit_test_fixtures.rule_dict
        rule_id = 1

        flexmock(proctor_views.controller) \
            .should_receive('get_incident_rule') \
            .with_args(rule_id=rule_id, datasource_uuid=datasource_uuid) \
            .and_return(rule)

        flexmock(proctor_views) \
            .should_receive('_rules_to_dict') \
            .with_args(rule) \
            .and_return(should_return)

        flexmock(self.views).should_receive('get_incident_rule').and_return(
            should_response)

        returned = self.views.get_incident_rule(
            rule_id=rule_id, datasource_uuid=datasource_uuid)
        assert returned.status_code == '200 OK'
        assert returned.json == should_return

    def test_delete_incident_rule(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        rule_id = 1
        should_return = unit_test_fixtures.response_204

        flexmock(proctor_views.controller) \
            .should_receive('delete_incident_rule') \
            .with_args(rule_id=rule_id, datasource_uuid=datasource_uuid)

        flexmock(self.views).should_receive('delete_incident_rule').and_return(
            should_return)

        returned = self.views.delete_incident_rule(
            current_user='user',
            rule_id=rule_id,
            datasource_uuid=datasource_uuid)
        assert returned.status == '204 NO CONTENT'

    def test_mapping(self):
        datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        should_response = unit_test_fixtures.response

        flexmock(proctor_views.controller) \
            .should_receive('mapping') \
            .and_return({'Status code': 200})

        flexmock(
            self.views).should_receive('mapping').and_return(should_response)

        returned = self.views.mapping(datasource_uuid)
        assert returned.status_code == '200 OK'
