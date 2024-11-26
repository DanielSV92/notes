import copy
import datetime
import os

from flexmock import flexmock
from unittest import TestCase

from smarty.app import create_app
from smarty.domain.models import DataSource
from smarty.domain.models import Incident
from smarty.proctor import utils
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestUtils(TestCase):
    def setup_class(self):
        self.utils = utils

    def test_es_status_to_dict_list(self):
        query = []
        should_return = ['object']
        returned_value = self.utils.es_status_to_dict_list(query)
        assert len(returned_value) == len(should_return)

        es_status = copy.deepcopy(unit_test_fixtures.es_status1)
        should_return = [unit_test_fixtures.es_status_1_dict]
        returned_value = self.utils.es_status_to_dict_list([es_status])
        assert returned_value == should_return

    def test_check_off_diff(self):
        from_log = 'Thu, 16 May 2019 18:14:00 GMT'
        from_datum = datetime.datetime(2019, 5, 16, 18, 14)
        should_return = 1558030440000
        returned_value = self.utils.check_off_diff(from_log, from_datum)
        assert returned_value == should_return

    def test_proctor_model_to_short_dict(self):
        proctor_model = unit_test_fixtures.proctor_model
        should_return = unit_test_fixtures.proctor_model_short_dict
        returned_value = self.utils.proctor_model_to_short_dict(proctor_model)
        assert returned_value == should_return

    def test_proctor_model_to_dict(self):
        proctor_model = unit_test_fixtures.proctor_model
        should_return = unit_test_fixtures.proctor_model_dict
        returned_value = self.utils.proctor_model_to_dict(proctor_model)
        assert returned_value == should_return

    def test_log_category_to_dict(self):
        log_category = unit_test_fixtures.log_category
        should_return = unit_test_fixtures.log_category_dict

        flexmock(utils).should_receive('get_openai_details').and_return(None)
        flexmock(utils).should_receive('get_openai_solution').and_return(None)
        flexmock(utils).should_receive('get_openai_reaction').and_return(None)

        returned_value = self.utils.log_category_to_dict(log_category)
        assert returned_value == should_return

    def test_fingerprint_to_dict(self):
        fingerprint = unit_test_fixtures.fingerprint
        should_return = unit_test_fixtures.fingerprint_dict
        returned_value = self.utils.fingerprint_to_dict(fingerprint)
        assert returned_value == should_return

    def test_training_datum_to_dict(self):
        training_datum = unit_test_fixtures.training_datum
        should_return = unit_test_fixtures.training_datum_dict
        incident = unit_test_fixtures.incident
        data_source = unit_test_fixtures.data_source

        flexmock(Incident).should_receive('query.get').and_return(incident)
        flexmock(DataSource).should_receive('query.filter.first').and_return(data_source)

        returned = self.utils.training_datum_to_dict(training_datum)
        assert returned == should_return

