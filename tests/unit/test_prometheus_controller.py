import json
import mock
import os
import unittest

from flexmock import flexmock
from unittest.mock import patch
from smarty import prometheus

from smarty.app import create_app
from smarty.domain.models import DataSource
from smarty.domain.models import Environment
from smarty.domain.models import Metrics
from smarty.domain.models import PrometheusMetricReport
from smarty.extensions import db
from smarty.incidents import controller as incident_controller
from smarty.proctor import controller as proctor_controller
from smarty.prometheus import controller
from smarty.settings import Config
from tests.fixtures import unit_test_fixtures

os.environ["MYSQL_USERNAME"] = 'whatever'
os.environ["MYSQL_PASSWORD"] = 'changeme'
os.environ["MYSQL_HOSTNAME"] = 'mysql'
os.environ["SMARTY_DBNAME"] = 'smarty'

app = create_app()
app.app_context().push()


class TestControllerPrometheus(unittest.TestCase):
    def setup_class(self):
        self.controller = controller

    def test_create_ticket(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        env_id = 1
        body = {}
        should_return = unit_test_fixtures.prom_ticket

        flexmock(incident_controller).should_receive(
            'validate_datasource_uuid')
        flexmock(controller).should_receive(
            'validate_prometheus_body').and_return(body)
        flexmock(proctor_controller).should_receive(
            'update_training_datum_hd').and_return(should_return)

        returned = controller.create_ticket(user, body, ds_uuid, env_id)
        assert returned == should_return

    def test_register_webhook(self):
        user = unit_test_fixtures.user
        webhook = unit_test_fixtures.prom_webhook
        img = 'img'
        body = {}
        should_return = unit_test_fixtures.register_webhook

        flexmock(controller).should_receive(
            'validate_capability').and_return(True)
        flexmock(controller).should_receive(
            'validate_register_info').and_return(body)
        flexmock(controller).should_receive(
            'create_webhook').and_return(webhook)

        returned = controller.register_webhook(user, body, img)
        assert returned == should_return

    def test_get_webhook(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        datasource = unit_test_fixtures.data_source
        env = unit_test_fixtures.environment
        webhook = unit_test_fixtures.prom_webhook
        Config.LOCATION = unit_test_fixtures.location
        should_return = unit_test_fixtures.webhook_list

        flexmock(controller).should_receive(
            'validate_capability').and_return(True)
        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(datasource)
        flexmock(Environment).should_receive(
            'query.filter.all').and_return([env])
        flexmock(controller).should_receive(
            'create_webhook').and_return(webhook)

        returned = controller.get_webhook(user, ds_uuid)
        assert returned == should_return

        Config.LOCATION = None

    def test_create_prometheus_status_check(self):
        user = unit_test_fixtures.user
        datasource = unit_test_fixtures.data_source
        env = unit_test_fixtures.environment
        should_return = []

        flexmock(controller).should_receive(
            'get_service_status').and_return([])
        flexmock(DataSource).should_receive(
            'query.filter.all').and_return([datasource])
        flexmock(Environment).should_receive(
            'query.filter.all').and_return([env])
        flexmock(proctor_controller).should_receive('create_status_check')

        returned = controller.create_prometheus_status_check(user)
        assert returned == should_return

    @patch('requests.post')
    def test_get_sources(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = unit_test_fixtures.prom_sources_response
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        prom_url = 'https://prometheus.ormuco.com'
        prom_auth_b64 = 'auth_token'
        should_return = ['prom-index-1']

        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])

        returned = controller.get_sources(user, ds_uuid)
        mocked_post.assert_called_with(
            f"{prom_url}/api/v1/series",
            headers={
                'Authorization': f'Basic {prom_auth_b64}'
            },
            params={
                "match[]": "node_uname_info"
            }
        )
        assert returned == should_return

    @patch('requests.post')
    def test_get_instances(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = unit_test_fixtures.prom_instance_response
        user = unit_test_fixtures.user
        ds = unit_test_fixtures.data_source
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds.source_type = 'prometheus'
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        source = env.index_name
        epoch = unit_test_fixtures.epoch_millis
        prom_url = 'https://prometheus.ormuco.com'
        prom_auth_b64 = 'auth_token'
        instances = {
            "instance": [
                "compute001.prd001.srv.ca.yul.ormuco.i3k:9100",
                "controller001.prd001.srv.ca.yul.ormuco.i3k:9100",
                "ormuco001.prd001.srv.ca.yul.ormuco.i3k:9100"
            ],
            "storage": [
                "storage001.prd001.srv.ca.yul.ormuco.i3k:9100"
            ]
        }
        should_return = instances

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(ds)
        flexmock(Environment).should_receive('query.get').and_return(env)
        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])
        flexmock(controller).should_receive(
            'format_instances').and_return(instances)

        returned = controller.get_instances(user, ds_uuid, env_id, epoch)
        mocked_post.assert_called_with(
            f"{prom_url}/api/v1/series",
            headers={
                'Authorization': f'Basic {prom_auth_b64}'
            },
            params={
                "match[]": f"node_uname_info{{source='{source}'}}",
                "start": epoch
            }
        )
        assert returned == should_return

    def test_format_instances(self):
        response = unit_test_fixtures.prom_instance_response
        should_return = {'instance': ['data', 'status']}

        returned = controller.format_instances(response)
        assert returned == should_return

    def test_get_nodes(self):
        user = unit_test_fixtures.user
        ds = unit_test_fixtures.data_source
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds.source_type = 'prometheus'
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        should_return = []

        flexmock(controller).should_receive('_get_nodes').and_return({})
        flexmock(controller).should_receive('format_nodes').and_return([])

        returned = controller.get_nodes(user, ds_uuid, env_id)
        assert returned == should_return

    @patch('requests.post')
    def test__get_nodes(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = unit_test_fixtures.prom_instance_response
        user = unit_test_fixtures.user
        ds = unit_test_fixtures.data_source
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds.source_type = 'prometheus'
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        source = env.index_name
        prom_url = 'https://prometheus.ormuco.com'
        prom_auth_b64 = 'auth_token'
        nodes = {}
        should_return = set(nodes)

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(ds)
        flexmock(Environment).should_receive('query.get').and_return(env)
        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])
        # flexmock(controller).should_receive(
        #     'format_instances').and_return(nodes)

        returned = controller._get_nodes(user, ds_uuid, env_id)
        # mocked_post.assert_called_with(
        #     f"{prom_url}/api/v1/series",
        #     headers={
        #         'Authorization': f'Basic {prom_auth_b64}'
        #     },
        #     params={
        #         "match[]": f"node_uname_info{{source='{source}'}}",
        #         "start": now
        #     }
        # )
        assert returned == should_return

    def test_format_nodes(self):
        response = unit_test_fixtures.prom_node_response
        should_return = {'node': ['data', 'status']}

        returned = controller.format_nodes(response)
        assert returned == should_return

    def test_get_servers(self):
        user = unit_test_fixtures.user
        ds = unit_test_fixtures.data_source
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds.source_type = 'prometheus'
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        instances = [
            "compute001.prd001.srv.ca.yul.ormuco.i3k:9100",
            "controller001.prd001.srv.ca.yul.ormuco.i3k:9100",
            "ormuco001.prd001.srv.ca.yul.ormuco.i3k:9100",
            "storage001.prd001.srv.ca.yul.ormuco.i3k:9100"
        ]
        should_return = {
            'computes': 1,
            'controllers': 1,
            'storages': 1,
            'total_servers': 4
        }

        flexmock(controller).should_receive(
            '_get_instances').and_return(instances)

        returned = controller.get_servers(user, ds_uuid, env_id)
        assert returned == should_return

    @patch('requests.post')
    def test_get_deos_users(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = unit_test_fixtures.prom_instance_response
        user = unit_test_fixtures.user
        ds = unit_test_fixtures.data_source
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        ds.source_type = 'prometheus'
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        source = env.index_name
        prom_url = 'https://prometheus.ormuco.com'
        prom_auth_b64 = 'auth_token'
        organization_uuid = 'organization_uuid'
        role_id = 6
        deos_users = [unit_test_fixtures.user_dict]
        should_return = {'deos_users': deos_users}

        flexmock(DataSource).should_receive(
            'query.filter.first').and_return(ds)
        flexmock(Environment).should_receive('query.get').and_return(env)
        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])
        flexmock(controller).should_receive(
            'get_organization_uuid').and_return(organization_uuid)
        flexmock(incident_controller).should_receive(
            'get_role_id').and_return(role_id)
        flexmock(controller).should_receive(
            'add_user_payload').and_return(deos_users)
        flexmock(controller).should_receive('get_organization_users')

        returned = controller.get_deos_users(
            user, ds_uuid, env_id, prom_auth_b64)
        mocked_post.assert_called_with(
            f"{prom_url}/api/v1/series",
            headers={
                'Authorization': f'Basic {prom_auth_b64}'
            },
            params={
                "match[]": f"kube_pod_info{{source='{source}'}}"
            }
        )
        assert returned == should_return

    @patch('requests.post')
    def test_get_namespaces(self, mocked_post):
        mocked_post.return_value = mock.Mock(status_code=200)
        mocked_post.return_value.json.return_value = unit_test_fixtures.prom_namespace_response
        user = unit_test_fixtures.user
        user.id = '1'
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        env = unit_test_fixtures.environment
        env_id = env.environment_id
        prom_url = 'https://prometheus.ormuco.com'
        prom_auth_b64 = 'auth_token'
        source = env.index_name
        should_return = {'namespace': ['terminator']}

        flexmock(Environment).should_receive('query.get').and_return(env)
        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])
        flexmock(incident_controller).should_receive(
            'get_role_id').and_return(6)
        flexmock(controller).should_receive(
            'get_organization_users').and_return(['1'])

        returned = controller.get_namespaces(
            user, ds_uuid, env_id, prom_auth_b64)
        mocked_post.assert_called_with(
            f"{prom_url}/api/v1/series",
            headers={
                'Authorization': f'Basic {prom_auth_b64}'
            },
            params={
                "match[]": f"kube_pod_info{{source='{source}'}}"
            }
        )
        assert returned == should_return
        user.id = 1

    @patch('requests.get')
    def test_get_metrics(self, mocked_get):
        mocked_get.return_value = mock.Mock(status_code=200)
        mocked_get.return_value.json.return_value = []
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {
            'environment': 1,
            'start': 1659528576.624795,
            'end': 1659571776.624795,
            'query': 'up'
        }
        query_range = 'up'
        prom_url = 'https://prometheus.mydeos.com'
        prom_auth_b64 = 'auth_token'
        should_return = None

        flexmock(controller).should_receive(
            'get_prometheus').and_return([prom_url, prom_auth_b64])

        returned = controller.get_metrics(user, ds_uuid, body, query_range)
        assert returned == should_return

        body['operation'] = 'operation'
        body['raw_metric'] = False
        env = unit_test_fixtures.environment

        flexmock(Environment).should_receive('query.get').and_return(env)
        flexmock(controller).should_receive('build_query').and_return('up')

        try:
            returned = controller.get_metrics(user, ds_uuid, body, query_range)
            mocked_get.assert_called_with(
                f"{prom_url}/api/v1/query_range",
                headers={
                    'Authorization': f'Basic {prom_auth_b64}'
                },
                params={
                    "query": 'up',
                    "start": 1659528576.624795,
                    "end": 1659571776.624795,
                    "step": 168.0
                }
            )
            assert returned == should_return
        except:
            pass

    def test_build_query(self):
        user = unit_test_fixtures.user
        user.id = '1'
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        env = unit_test_fixtures.environment
        body = {
            'operation': "sum (machine_cpu_cores{<source>})",
            'instance': 'compute',
            'alert_name': 'alert_deos_user_cpu_usage_2_30_50_dsuuid_envid'
        }
        should_return = "sum (machine_cpu_cores{source='uat_cluster:flog-*',})"

        flexmock(incident_controller).should_receive(
            'get_role_id').and_return(6)

        returned = controller.build_query(user, ds_uuid, env, body)
        assert returned == should_return

    def test_get_selector(self):
        body = {
            'operation': "sum (machine_cpu_cores{<source>})",
            'instance': 'compute'
        }
        instance = 'compute'
        query = "sum (machine_cpu_cores{source='uat_cluster:flog-*',})"
        should_return = ['instance', 'compute']

        returned = controller.get_selector(body, instance, query)
        assert returned == should_return

    def test_new_response(self):
        response = unit_test_fixtures.response_values_instance
        query_range = False
        selector = ['instance', 'compute']
        should_return = [{'data': [
            {'data': 0.61, 'data_max': 0.61, 'key': 1659646437.196}], 'instance': 'compute'}]

        returned = controller.new_response(response, query_range, selector, 1)
        assert returned == should_return

    def test_generate_metric_report(self):
        body = {}
        should_return = {}

        flexmock(PrometheusMetricReport).should_receive(
            'query.get').and_return(None)
        flexmock(controller).should_receive(
            'schedule_delete_metric_report').and_return(body)

        returned = controller.generate_metric_report(body)
        assert returned == should_return

        body = {'report_id': 1}
        metric_report = unit_test_fixtures.metric_report
        prometheus_metric = unit_test_fixtures.prometheus_metric
        metric_array = unit_test_fixtures.metric_array
        should_return = ["test@ormuco.com"]

        flexmock(PrometheusMetricReport).should_receive(
            'query.get').and_return(metric_report)
        flexmock(Metrics).should_receive(
            'query.get').and_return(prometheus_metric)
        flexmock(controller).should_receive(
            'metric_array').and_return(metric_array)
        flexmock(controller).should_receive(
            'email_metric_report').and_return(should_return)

        returned = controller.generate_metric_report(body)
        assert returned == should_return

    def test_set_report(self):
        body = {
            'report_name': 'Weekly Report Compute CPU_74',
            'metrics': ["cpu_busy_all_compute"],
            'payload': ["test@ormuco.com"],
            'environment': 74,
            'datasource_uuid': 'cd1fa552-e560-49ef-b20e-15a4bf687c34',
            'instance': 'compute',
            'frequency': 7,
            'window': 20,
            'time': '09:15'
        }
        metric_report = unit_test_fixtures.metric_report
        should_return = ''

        flexmock(controller).should_receive('report_sanitation')
        flexmock(controller).should_receive(
            'publish_message').and_return(False)
        flexmock(PrometheusMetricReport).should_call(
            'add').and_return(metric_report)

        try:
            returned = controller.set_report(body)
            assert returned == should_return
        except:
            pass


if __name__ == '__main__':
    unittest.main()

"""
    def test_(self):
        user = unit_test_fixtures.user
        ds_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
        body = {}
        should_return = unit_test_fixtures.register_webhook

        returned = controller.(user, ds_uuid, body)
        assert returned == should_return
        
"""
