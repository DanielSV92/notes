"""Defines fixtures available to all tests."""

import json
from datetime import datetime

import pytest
from cryptography.hazmat.backends import \
    default_backend as crypto_default_backend
from cryptography.hazmat.primitives import \
    serialization as crypto_serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from smarty.app import create_app
from smarty.domain.models import CapabilityList
from smarty.domain.models import CategoryOccurrences
from smarty.domain.models import CerebroSettings
from smarty.domain.models import DataSource
from smarty.domain.models import EnvFeatures
from smarty.domain.models import Environment
from smarty.domain.models import Fingerprint
from smarty.domain.models import HelpdeskCategory
from smarty.domain.models import HelpdeskSubCategory
from smarty.domain.models import Incident
from smarty.domain.models import IncidentEvent
from smarty.domain.models import IncidentRule
from smarty.domain.models import IncidentStateEvent
from smarty.domain.models import IncidentType
from smarty.domain.models import IncidenttypeHistory
from smarty.domain.models import IncidentTypeLabelEvent
from smarty.domain.models import IncidentTypeRefinementEvent
from smarty.domain.models import IncidentTypeSeverityEvent
from smarty.domain.models import LogCategory
from smarty.domain.models import ProctorModel
from smarty.domain.models import ProctorTrainingData
from smarty.domain.models import Role
from smarty.domain.models import RolesUsers
from smarty.domain.models import Signature
from smarty.domain.models import SlackIntegration
from smarty.domain.models import User
from smarty.extensions import db as _db
from smarty.settings import TestConfig

key = rsa.generate_private_key(backend=crypto_default_backend(),
                               public_exponent=65537,
                               key_size=2048)

private_key = key.private_bytes(crypto_serialization.Encoding.PEM,
                                crypto_serialization.PrivateFormat.PKCS8,
                                crypto_serialization.NoEncryption())

public_key = key.public_key().public_bytes(
    crypto_serialization.Encoding.OpenSSH,
    crypto_serialization.PublicFormat.OpenSSH)


@pytest.fixture(scope='session')
def app():
    flask_app = create_app(TestConfig())

    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()

    yield flask_app  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='session')
def test_client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def init_database(app):
    # Create the database and the database table
    _db.app = app
    _db.create_all()

    # Insert user data
    role = Role(name="Administrator", description="Can do everything")
    proctor_role = Role(
        name="Proctor",
        description="A new role that just covers what Proctor does")
    _db.session.add(role)
    _db.session.add(proctor_role)
    user = User(id=1,
                email='admin@gmail.com',
                password='test',
                first_name="jean",
                last_name="guy",
                phone_number="5555555",
                confirmed_at=datetime(2012, 3, 3, 10, 10, 10),
                is_root=True)
    user_2 = User(id=2,
                  email='admin2@gmail.com',
                  password='test',
                  first_name="john",
                  last_name="smith",
                  phone_number="5555555",
                  confirmed_at=datetime(2012, 3, 3, 10, 10, 10))
    proctor_user = User(id='proctor',
                        email='proctor@infra',
                        password='test',
                        first_name="jean",
                        last_name="guy",
                        phone_number="5555555",
                        confirmed_at=datetime(2012, 3, 3, 10, 10, 10))
    _db.session.add(user)
    _db.session.add(user_2)
    _db.session.add(proctor_user)

    # Insert env features
    feature_1 = EnvFeatures(env_feature='Incidents')
    feature_2 = EnvFeatures(env_feature='EnvironmentDashboard')
    _db.session.add(feature_1)
    _db.session.add(feature_2)
    # Insert cerebro settings
    cerebro_settings = CerebroSettings(package_type='standard',
                                       domain='www.mytestdomain.com',
                                       max_ds=10,
                                       public=public_key,
                                       private=private_key)
    _db.session.add(cerebro_settings)
    # Commit the changes for the users
    _db.session.commit()
    roles_user = RolesUsers(user_id=1, role_id=1)
    roles_user_2 = RolesUsers(user_id=2, role_id=1)
    roles_proctor = RolesUsers(user_id='proctor', role_id=2)
    _db.session.add(roles_user)
    _db.session.add(roles_user_2)
    _db.session.add(roles_proctor)
    _db.session.commit()

    admin_capabilities = CapabilityList(role_id=1,
                                        view_data_source_information=1,
                                        view_action=1,
                                        delete_action=1,
                                        modify_action=1,
                                        execute_action=1,
                                        add_action=1,
                                        view_alert=1,
                                        delete_alert=1,
                                        modify_alert=1,
                                        add_alert=1,
                                        view_solution=1,
                                        delete_solution=1,
                                        modify_solution=1,
                                        add_solution=1,
                                        create_new_incident_by_refinement=1,
                                        merge_by_refinement=1,
                                        change_to_closed=1,
                                        set_to_open=1,
                                        modify_severity=1,
                                        set_severity=1,
                                        merge_by_labelling=1,
                                        create_account=1,
                                        update_account=1,
                                        delete_account=1,
                                        create_role=1,
                                        delete_role=1,
                                        get_roles=1,
                                        set_permissions=1,
                                        update_billing_info=1,
                                        view_billing_info=1,
                                        reset_password=1,
                                        view_account_info=1,
                                        add_new_data_source=1,
                                        update_data_source=1,
                                        delete_data_source=1,
                                        add_a_new_label=1,
                                        modify_label=1)
    proctor_capabilities = CapabilityList(role_id=2,
                                          view_data_source_information=1,
                                          view_action=1,
                                          delete_action=0,
                                          modify_action=0,
                                          execute_action=1,
                                          add_action=0,
                                          view_alert=1,
                                          delete_alert=0,
                                          modify_alert=0,
                                          add_alert=0,
                                          view_solution=0,
                                          delete_solution=0,
                                          modify_solution=0,
                                          add_solution=0,
                                          create_new_incident_by_refinement=1,
                                          merge_by_refinement=1,
                                          change_to_closed=1,
                                          set_to_open=1,
                                          modify_severity=1,
                                          set_severity=1,
                                          merge_by_labelling=1,
                                          create_account=0,
                                          update_account=0,
                                          delete_account=0,
                                          create_role=0,
                                          delete_role=0,
                                          get_roles=0,
                                          set_permissions=0,
                                          update_billing_info=0,
                                          view_billing_info=0,
                                          reset_password=1,
                                          view_account_info=1,
                                          add_new_data_source=0,
                                          update_data_source=0,
                                          delete_data_source=0,
                                          add_a_new_label=1,
                                          modify_label=1)
    _db.session.add(admin_capabilities)
    _db.session.add(proctor_capabilities)
    data_source = DataSource(display_name="Montreal Ormuco",
                             es_host="1.1.1.1",
                             es_password="testtest",
                             es_port=9201,
                             es_schema='http',
                             es_user="cerebro",
                             mapping_blocked=False,
                             uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf",
                             owner='1',
                             public=False,
                             shared=False,
                             source_type='elastic')
    _db.session.add(data_source)
    _db.session.commit()
    response_slack = {
        "ok": True,
        "access_token": "my access token",
        "scope": "identify,incoming-webhook",
        "user_id": "my_user",
        "team_id": "T08U7GS8K",
        "enterprise_id": None,
        "team_name": "Ormuco Cloud",
        "incoming_webhook": {
            "channel": "#dev-cerebro-alerts",
            "channel_id": "my_channel",
            "configuration_url": "my_url",
            "url": "my_other_url"
        }
    }
    response_slack = json.dumps(response_slack).encode()
    slack_entry_1 = SlackIntegration(slack_id=1,
                                     channel="#dev-cerebro-alerts",
                                     channel_id='my_channel',
                                     webhook_url='my_other_url',
                                     activated=True,
                                     response=response_slack)
    _db.session.add(slack_entry_1)
    _db.session.commit()

    rule_1 = IncidentRule(
        rule="logger_series['Logger'] == 'openstack.ceilometer'",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    rule_2 = IncidentRule(
        rule="logger_series['Logger'] == 'openstack.glance'",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(rule_1)
    _db.session.add(rule_2)
    _db.session.commit()

    features = ["incidents"]
    environment = Environment(display_name="mtl Ormuco",
                              features=json.dumps(features),
                              datasource_type_id=1,
                              index_name="kolla_logging:flog-*")

    _db.session.add(environment)
    _db.session.commit()

    environment_2 = Environment(display_name="beeline Ormuco",
                                features=json.dumps(features),
                                datasource_type_id=1,
                                index_name="veon_logging:flog-*")

    _db.session.add(environment_2)
    _db.session.commit()

    signature_1 = Signature(signature_id=1, count={}, position_offset=[])
    signature_2 = Signature(signature_id=2, count={}, position_offset=[])
    _db.session.add(signature_1)
    _db.session.add(signature_2)
    _db.session.commit()

    fingerprint_1 = Fingerprint(fingerprint_type='email',
                                regex='[\w\.-]+@[\w\.-]+\.\w+',
                                generic_template='X@X.X')
    fingerprint_2 = Fingerprint(fingerprint_type='ip',
                                regex='(?:[0-9]{1,3}\.){3}[0-9]{1,3}',
                                generic_template='X.X.X.X')
    _db.session.add(fingerprint_1)
    _db.session.add(fingerprint_2)
    _db.session.commit()

    proctor_model_data = json.dumps("test").encode()
    datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
    proctor_model = ProctorModel(data=proctor_model_data,
                                 datasource_uuid=datasource_uuid)
    _db.session.add(proctor_model)
    _db.session.commit()


    datasource_uuid_2 = "e199ac5c-ee7d-4d73-bb61-ab2b48425ada"
    proctor_model_2 = ProctorModel(data=proctor_model_data,
                                 datasource_uuid=datasource_uuid_2)
    _db.session.add(proctor_model_2)
    _db.session.commit()

    datasource_uuid_3 = "e199ac5c-ee7d-4d73-bb61-ab2b48425adb"
    proctor_model_3 = ProctorModel(data=proctor_model_data,
                                 datasource_uuid=datasource_uuid_3)
    _db.session.add(proctor_model_3)
    _db.session.commit()

    datasource_uuid_4 = "e199ac5c-ee7d-4d73-bb61-ab2b48425adc"
    proctor_model_4 = ProctorModel(data=proctor_model_data,
                                 datasource_uuid=datasource_uuid_4)
    _db.session.add(proctor_model_4)

    _db.session.commit()
    df = [3, 1, 4, 5, 6]
    input_df = json.dumps(df).encode()

    # incident type 1
    incident_type = IncidentType(
        it_id=1,
        incidenttype_id=1,
        cluster_id=1,
        proctormodel_id=1,
        input_df=input_df,
        label_prediction=input_df,
        labeled=False,
        logcategories="[1]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")

    incident_label_event = IncidentTypeLabelEvent(
        incident_type=incident_type,
        label="Unknown",
        created_date=datetime(2014, 10, 19, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event = IncidentTypeSeverityEvent(
        incident_type=incident_type,
        severity="Unknown",
        created_date=datetime(2014, 10, 19, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event = IncidentTypeRefinementEvent(
        incident_type=incident_type,
        refinement="cerebro",
        created_date=datetime(2014, 10, 19, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type)
    _db.session.add(incident_label_event)
    _db.session.add(incident_type_severity_event)
    _db.session.add(incident_type_refinement_event)
    _db.session.commit()

    # incident type 2
    incident_type_2 = IncidentType(
        it_id=2,
        incidenttype_id=2,
        cluster_id=1,
        proctormodel_id=2,
        input_df=input_df,
        label_prediction=input_df,
        labeled=False,
        logcategories="[2, 4, 6]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_2 = IncidentTypeLabelEvent(
        incident_type=incident_type_2,
        label="Unknown",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_2 = IncidentTypeSeverityEvent(
        incident_type=incident_type_2,
        severity="Unknown",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_2 = IncidentTypeRefinementEvent(
        incident_type=incident_type_2,
        refinement="cerebro",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_2)
    _db.session.add(incident_label_event_2)
    _db.session.add(incident_type_severity_event_2)
    _db.session.add(incident_type_refinement_event_2)
    _db.session.commit()

    # incident type 3
    incident_type_3 = IncidentType(
        it_id=3,
        incidenttype_id=3,
        cluster_id=2,
        proctormodel_id=2,
        input_df=input_df,
        label_prediction=input_df,
        labeled=False,
        logcategories="[3]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_3 = IncidentTypeLabelEvent(
        incident_type=incident_type_3,
        label="somethingwrong",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_3 = IncidentTypeSeverityEvent(
        incident_type=incident_type_3,
        severity="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_3 = IncidentTypeRefinementEvent(
        incident_type=incident_type_3,
        refinement="cerebro",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_3)
    _db.session.add(incident_label_event_3)
    _db.session.add(incident_type_severity_event_3)
    _db.session.add(incident_type_refinement_event_3)
    _db.session.commit()

    # incident type 4
    incident_type_4 = IncidentType(
        it_id=4,
        incidenttype_id=4,
        cluster_id=3,
        proctormodel_id=3,
        input_df=input_df,
        label_prediction=input_df,
        labeled=False,
        logcategories="[99,100,111]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_4 = IncidentTypeLabelEvent(
        incident_type=incident_type_4,
        label="Unknown",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_4 = IncidentTypeSeverityEvent(
        incident_type=incident_type_4,
        severity="Unknown",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_4 = IncidentTypeRefinementEvent(
        incident_type=incident_type_4,
        refinement="cerebro",
        created_date=datetime(2014, 10, 18, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_4)
    _db.session.add(incident_label_event_4)
    _db.session.add(incident_type_severity_event_4)
    _db.session.add(incident_type_refinement_event_4)
    _db.session.commit()

    # incident type 5
    incident_type_5 = IncidentType(
        it_id=5,
        incidenttype_id=5,
        cluster_id=5,
        proctormodel_id=4,
        input_df=input_df,
        label_prediction=input_df,
        labeled=True,
        logcategories="[5]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_5 = IncidentTypeLabelEvent(
        incident_type=incident_type_5,
        label="My label",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_5 = IncidentTypeSeverityEvent(
        incident_type=incident_type_5,
        severity="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_5 = IncidentTypeRefinementEvent(
        incident_type=incident_type_5,
        refinement="cerebro",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_5)
    _db.session.add(incident_label_event_5)
    _db.session.add(incident_type_severity_event_5)
    _db.session.add(incident_type_refinement_event_5)
    _db.session.commit()

    # incident type 6
    incident_type_6 = IncidentType(
        it_id=6,
        incidenttype_id=6,
        cluster_id=6,
        proctormodel_id=4,
        input_df=input_df,
        label_prediction=input_df,
        labeled=False,
        logcategories="[5]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_6 = IncidentTypeLabelEvent(
        incident_type=incident_type_6,
        label="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_6 = IncidentTypeSeverityEvent(
        incident_type=incident_type_6,
        severity="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_6 = IncidentTypeRefinementEvent(
        incident_type=incident_type_6,
        refinement="cerebro",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_6)
    _db.session.add(incident_label_event_6)
    _db.session.add(incident_type_severity_event_6)
    _db.session.add(incident_type_refinement_event_6)
    _db.session.commit()

    df = [7, 8]
    input_df_2 = json.dumps(df).encode()
    # incident type 7
    incident_type_7 = IncidentType(
        it_id=7,
        incidenttype_id=7,
        cluster_id=7,
        proctormodel_id=3,
        input_df=input_df_2,
        label_prediction=input_df_2,
        labeled=False,
        logcategories="[7]",
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    incident_label_event_7 = IncidentTypeLabelEvent(
        incident_type=incident_type_7,
        label="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_severity_event_7 = IncidentTypeSeverityEvent(
        incident_type=incident_type_7,
        severity="Unknown",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    incident_type_refinement_event_7 = IncidentTypeRefinementEvent(
        incident_type=incident_type_7,
        refinement="cerebro",
        created_date=datetime(2014, 10, 20, 10, 10, 10),
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_type_7)
    _db.session.add(incident_label_event_7)
    _db.session.add(incident_type_severity_event_7)
    _db.session.add(incident_type_refinement_event_7)
    _db.session.commit()

    type_history_1 = IncidenttypeHistory(name="test-ticket-1",
                                         history_datetime=datetime(
                                             2013, 3, 3, 10, 10, 10),
                                         it_id=1,
                                         datasource_uuid=datasource_uuid)

    type_history_5 = IncidenttypeHistory(name="test-ticket-5",
                                         history_datetime=datetime(
                                             2014, 3, 3, 10, 10, 10),
                                         it_id=5,
                                         datasource_uuid=datasource_uuid)

    type_history_6 = IncidenttypeHistory(name="test-ticket-6",
                                         history_datetime=datetime(
                                             2015, 3, 3, 10, 10, 10),
                                         it_id=5,
                                         datasource_uuid=datasource_uuid)
    _db.session.add(type_history_1)
    _db.session.add(type_history_5)
    _db.session.add(type_history_6)
    _db.session.commit()

    # Ticket 1
    myhost = json.dumps(['compute001', 'ormuco002'])
    mylogger = json.dumps(['neutron'])
    incident = Incident(
        incident_id=1,
        i_id=1,
        name="test-ticket-1",
                        is_read=False,
                        occurrences=2,
                        number_solutions=1,
                        environment=1,
                        host=myhost,
                        logger=mylogger,
                        occurrence_date=datetime(2012, 3, 3, 10, 10, 10),
                        last_occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
                        created_date=datetime(2013, 3, 3, 10, 10, 10),
                        it_id=1,
                        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident)
    _db.session.commit()

    incident_state_event = IncidentStateEvent(i_id=1,
                                              created_date=datetime(
                                                  2013, 3, 3, 10, 10, 10),
                                              state="DISCOVERED",
                                              datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event)
    _db.session.commit()

    # Ticket 2
    myhost_2 = json.dumps(['compute002', 'ormuco003'])
    incident_2 = Incident(
        incident_id=2,
        i_id=2,
        name="test-ticket-2",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=1,
        host=myhost_2,
        logger=mylogger,
        occurrence_date=datetime(2012, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=2,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_2)
    _db.session.commit()

    incident_state_event_2 = IncidentStateEvent(
        i_id=2,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_2)
    _db.session.commit()

    # Ticket 3
    myhost_3 = json.dumps(['compute002', 'ormuco003'])
    mylogger_3 = json.dumps(['manilla'])
    incident_3 = Incident(
        incident_id=3,
        i_id=3,
        name="test-ticket-3",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=1,
        host=myhost_3,
        logger=mylogger_3,
        occurrence_date=datetime(2012, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=3,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_3)
    _db.session.commit()

    incident_state_event_3 = IncidentStateEvent(
        i_id=3,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_3)
    _db.session.commit()

    # Ticket 4
    myhost_4 = json.dumps(['controller001', 'ormuco003'])
    incident_4 = Incident(
        incident_id=4,
        i_id=4,
        name="test-ticket-4",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=1,
        host=myhost_4,
        logger=mylogger_3,
        occurrence_date=datetime(2012, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=4,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_4)
    _db.session.commit()

    incident_state_event_4 = IncidentStateEvent(
        i_id=4,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_4)
    _db.session.commit()

    myhost_5 = json.dumps(['compute001', 'ormuco002'])
    incident_5 = Incident(
        incident_id=5,
        i_id=5,
        name="test-ticket-5",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=1,
        host=myhost_5,
        logger=mylogger,
        occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 5, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=5,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_5)
    _db.session.commit()

    incident_state_event_5 = IncidentStateEvent(
        i_id=5,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_5)
    _db.session.commit()

    myhost_6 = json.dumps(['myTesthost'])
    mylogger_6 = json.dumps(['openstack.swift'])
    incident_6 = Incident(
        incident_id=6,
        i_id=6,
        name="test-ticket-6",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=2,
        host=myhost_6,
        logger=mylogger_6,
        occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 5, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=7,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_6)
    _db.session.commit()

    incident_state_event_6 = IncidentStateEvent(
        i_id=6,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_6)
    _db.session.commit()

    myhost_7 = json.dumps(['mytestHost2'])
    mylogger_7 = json.dumps(['openstack.test'])
    incident_7 = Incident(
        incident_id=7,
        i_id=7,
        name="test-ticket-7",
        is_read=False,
        occurrences=2,
        number_solutions=1,
        environment=8,
        host=myhost_7,
        logger=mylogger_7,
        occurrence_date=datetime(2013, 3, 3, 10, 10, 10),
        last_occurrence_date=datetime(2013, 5, 3, 10, 10, 10),
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        it_id=1,
        datasource_uuid="e199ac5c-ee7d-4d73-bb61-ab2b48425adf")
    _db.session.add(incident_7)
    _db.session.commit()

    incident_state_event_7 = IncidentStateEvent(
        i_id=7,
        created_date=datetime(2013, 3, 3, 10, 10, 10),
        state="DISCOVERED",
        datasource_uuid=datasource_uuid)
    _db.session.add(incident_state_event_7)
    _db.session.commit()

    # Training data for incident type 1 , ticket 1
    log_category = LogCategory(lc_id=1,
                               logcategory_id=1,
                               log_archetype="No compute node record for host",
                               logger="openstack.nova",
                               signature_id=1,
                               datasource_uuid=datasource_uuid)
    _db.session.add(log_category)
    _db.session.commit()
    data = [{
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 725,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }, {
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 725,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }, {
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 725,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }, {
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 725,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }, {
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'controller003.prd001.srv.hyp.yul.ormuco.i3k',
        'Logger': 'openstack.mesh',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 725,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }]
    data_encoded = json.dumps(data).encode()
    proctor_training_data = ProctorTrainingData(
        ptd_id=1,
        proctortrainingdata_id=1,
        data=data_encoded,
        end_date=datetime(2012, 3, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=1,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data)
    _db.session.commit()

    training_data_category_amount = CategoryOccurrences(
        lc_id=1,
        ptd_id=1,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount)
    _db.session.commit()

    # Training data for incident type 2 , ticket 2
    log_category_2 = LogCategory(
        lc_id=2,
        logcategory_id=2,
        log_archetype="No compute node record for host",
        logger="openstack.neutron",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_2)
    _db.session.commit()
    proctor_training_data_2 = ProctorTrainingData(
        ptd_id=2,
        proctortrainingdata_id=2,
        data=data_encoded,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=2,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_2)
    _db.session.commit()

    training_data_category_amount_2 = CategoryOccurrences(
        lc_id=2,
        ptd_id=2,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_2)
    _db.session.commit()

    # Training data for incident type 3 , ticket 3

    log_category_3 = LogCategory(
        lc_id=3,
        logcategory_id=3,
        log_archetype="Error during ShareManager",
        logger="openstack.manilla",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_3)
    _db.session.commit()
    proctor_training_data_3 = ProctorTrainingData(
        ptd_id=3,
        proctortrainingdata_id=3,
        data=data_encoded,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=3,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_3)
    _db.session.commit()

    training_data_category_amount_3 = CategoryOccurrences(
        lc_id=3,
        ptd_id=3,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_3)
    _db.session.commit()

    # Training data for incident type 4 , ticket 4

    log_category_4 = LogCategory(
        lc_id=4,
        logcategory_id=4,
        log_archetype="IPMI Error while attempting",
        logger="openstack.ironic",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_4)
    _db.session.commit()
    proctor_training_data_4 = ProctorTrainingData(
        ptd_id=4,
        proctortrainingdata_id=4,
        data=data_encoded,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=4,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_4)
    _db.session.commit()

    training_data_category_amount_4 = CategoryOccurrences(
        lc_id=4,
        ptd_id=4,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_4)
    _db.session.commit()

    #  Training data for incident type 5

    log_category_5 = LogCategory(
        lc_id=5,
        logcategory_id=5,
        log_archetype="No compute node record for host",
        logger="openstack.mesh",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_5)
    _db.session.commit()
    proctor_training_data_5 = ProctorTrainingData(
        ptd_id=5,
        proctortrainingdata_id=5,
        data=data_encoded,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=5,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_5)
    _db.session.commit()

    training_data_category_amount_5 = CategoryOccurrences(
        lc_id=5,
        ptd_id=5,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_5)
    _db.session.commit()

    # Training data for log category 6
    log_category_6 = LogCategory(
        lc_id=6,
        logcategory_id=6,
        log_archetype="Error during ShareManager",
        logger="openstack.daniel",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_6)
    _db.session.commit()

    proctor_training_data_6 = ProctorTrainingData(
        ptd_id=6,
        proctortrainingdata_id=6,
        data=data_encoded,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df,
        label_prediction=input_df,
        i_id=2,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_6)
    _db.session.commit()

    training_data_category_amount_6 = CategoryOccurrences(
        lc_id=6,
        ptd_id=6,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_6)
    _db.session.commit()

    data_2 = [{
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'myTesthost',
        'Logger': 'openstack.swift',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 7,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }, {
        '@timestamp': '2019-06-04T19:37:41.000000000+00:00',
        'Hostname': 'myTesthost',
        'Logger': 'openstack.swift',
        'Payload': 'ProviderLogin args kwargs: not found',
        'Pid': '7',
        'environment': 1,
        'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
        'log_level': 'ERROR',
        'logcategory_id': 7,
        'path': '/var/lib/docker/volumes/kolla_logs/_data/mesh/mesh',
        'programname': 'mesh',
        'tid': 'error'
    }]

    data_encoded_2 = json.dumps(data_2).encode()

    log_category_7 = LogCategory(
        lc_id=7,
        logcategory_id=7,
        log_archetype="ProviderLogin args kwargs: not found",
        logger="openstack.swift",
        signature_id=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(log_category_7)
    _db.session.commit()

    proctor_training_data_7 = ProctorTrainingData(
        ptd_id=7,
        proctortrainingdata_id=7,
        data=data_encoded_2,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df_2,
        label_prediction=input_df_2,
        i_id=6,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_7)
    _db.session.commit()

    training_data_category_amount_7 = CategoryOccurrences(
        lc_id=7,
        ptd_id=7,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_7)
    _db.session.commit()

    proctor_training_data_8 = ProctorTrainingData(
        ptd_id=8,
        proctortrainingdata_id=8,
        data=data_encoded_2,
        end_date=datetime(2012, 5, 3, 10, 10, 10),
        predicted_label="Unknown",
        input_df=input_df_2,
        label_prediction=input_df_2,
        i_id=7,
        open_incident=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(proctor_training_data_8)
    _db.session.commit()

    training_data_category_amount_8 = CategoryOccurrences(
        lc_id=7,
        ptd_id=8,
        occurrences=1,
        datasource_uuid=datasource_uuid)
    _db.session.add(training_data_category_amount_8)
    _db.session.commit()

    hd_category_1 = HelpdeskCategory(
        hd_c_id=1,
        c_name='Billing'
    )
    _db.session.add(hd_category_1)
    _db.session.commit()

    hd_subcategory_1 = HelpdeskSubCategory(
        hd_sc_id=1,
        sc_name='Missing bill',
        hd_c_id=1
    )
    _db.session.add(hd_subcategory_1)
    _db.session.commit()

    yield _db  # this is where the testing happens!

    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(init_database):
    connection = init_database.engine.connect()
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session_ = init_database.create_scoped_session(options=options)

    init_database.session = session_

    yield session_

    transaction.commit()
    connection.close()
    session_.remove()