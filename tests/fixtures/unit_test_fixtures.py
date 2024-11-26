
import datetime
import json
from collections import Counter

from section.settings import Config


class L(list):
    """
    A subclass of list that can accept additional attributes.
    Should be able to be used just like a regular list.

    The problem:
    a = [1, 2, 4, 8]
    a.x = "Hey!" # AttributeError: 'list' object has no attribute 'x'

    The solution:
    a = L(1, 2, 4, 8)
    a.x = "Hey!"
    """

    def __new__(self, *args, **kwargs):
        return super(L, self).__new__(self, args, kwargs)

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], '__iter__'):
            list.__init__(self, args[0])
        else:
            list.__init__(self, args)
        self.__dict__.update(kwargs)

    def __call__(self, **kwargs):
        self.__dict__.update(kwargs)
        return self


datetime_datetime = datetime.datetime.fromtimestamp(1514764800)
epoch_millis = 1514764800000
epoch_millis2 = 1535977247112
epoch_micros = 1514764800000000
end_date = 1557939668245
end_date2 = datetime.datetime.fromtimestamp(1514833200)

incident_response = L('incident_response')
incident_response.delete = L()
incident_response.update = L()
incident_response.closed = datetime_datetime
incident_response.first_unreplied = datetime_datetime
incident_response.last_replied = datetime_datetime
incident_response.last_unreplied = datetime_datetime
incident_response.first_replied = datetime_datetime

incident_report = L('incident_report')
incident_report.delete = L()
incident_report.update = L()
incident_report.url_location = 'localhost'
incident_report.incident_name = 'I1 - openstack.neutron'
incident_report.incident_occurrence_date_str = 'date'
incident_report.incident_current_label = 'Unknown'
incident_report.current_owner = None
incident_report.escalated = None
incident_report.current_state = 'Discovered'
incident_report.parent_id = None
incident_report.current_severity = 'Unknown'
incident_report.time_to_acknowledge_str = None
incident_report.response_time = None
incident_report.last_communication_date_str = None
incident_report.time_from_the_last_communication = None
incident_report.closed_date_str = None
incident_report.time_to_close = None
incident_report.incident_id = 1
incident_report.i_id = 1
incident_report.active_time = None
incident_report_dict = {
    'Active Time': None,
    'Title': 'I1 - openstack.neutron',
    'Case #': 'localhost',
    'Category': 'Unknown',
    'Closed': None,
    'Created': 'date',
    'Customer': 'Unknown',
    'Last Activity': None,
    'Owner': None,
    'Pending Survey': None,
    'Rating': None,
    'Escalated': None,
    'Severity': 'Unknown',
    'Status': 'Discovered',
    'Parent ID': None,
    'Subcategory': 'Unknown',
    'Last Activity Time': None,
    'Outside of SLA': False,
    'Response Time': None,
    'Time to close': None,
    'i_id': 1,
    'incident_id': 1
}

incident = L('incident')
incident.delete = L()
incident.update = L()
incident.i_id = 1
incident.incident_id = 1
incident.datasource_uuid = "e199ac5c-ee7d-4d73-bb61-ab2b48425adf"
incident.it_id = 1
incident.current_state = L()
incident.current_state.name = 'DISCOVERED'
incident.current_state._name_ = 'DISCOVERED'
incident.occurrence_date = datetime_datetime
incident.last_occurrence_date = datetime_datetime
incident.created_date = datetime_datetime
incident.end_date = datetime_datetime
incident.is_open = 1
incident.name = 'I1 - openstack.neutron'
incident.environment = 1
incident.host = json.dumps(['controller001'])
incident.logger = json.dumps(['openstack.nova', 'another.logger'])
incident.current_label = 'Unknown'
incident.current_severity = 'Discovered'
incident.current_owner = None
incident.is_read = 0
incident.occurrences = 1
incident.number_solutions = 0
incident.ownership_history = []
incident.state_history = [state_event]
state_history = [state_event_dict]
incident_dict = {
    'incident_id': incident.incident_id,
    'incidenttype_id': incident.it_id,
    'current_state': incident.current_state.name,
    'occurrence_date': incident.occurrence_date,
    'last_occurrence_date': incident.last_occurrence_date,
    'created_date': incident.created_date,
    'state_history': state_history,
    'end_date': incident.end_date,
    'is_open': incident.is_open,
    'name': incident.name,
    'environment': incident.environment,
    'host': incident.host,
    'logger': incident.logger,
    'current_label': incident.current_label,
    'current_severity': incident.current_severity,
    'is_read': incident.is_read,
    'occurrences': incident.occurrences,
    'number_solutions': incident.number_solutions,
    'logcategories': json.loads(json.dumps([1]).encode())
}

incident_info = {
    'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
    'environment_id': 1,
    'tickets': {
        'acknowledged': 0,
        'open': 1,
        'snoozed': 0,
        'total': 1,
        'unread': 1
    }
}

incident2 = L('incident')
incident2.delete = L()
incident2.i_id = 1
incident2.incident_id = 1
incident2.it_id = 1
incident2.current_state = L()
incident2.current_state.name = 'Discovered'
incident2.occurrence_date = datetime_datetime
incident2.last_occurrence_date = datetime_datetime
incident2.created_date = datetime_datetime
incident2.end_date = datetime_datetime
incident2.is_open = 0
incident2.name = 'I2 - openstack.smth'
incident2.environment = 2
incident2.host = json.dumps(['controller001']).encode()
incident2.logger = json.dumps(['openstack.nova']).encode()
incident2.current_label = 'Unknown'
incident2.current_severity = 'Discovered'
incident2.is_read = 0
incident2.occurrences = 1
incident2.number_solutions = 0
incident2.state_history = [state_event]
state_history2 = [state_event_dict]
incident_dict2 = {
    'incident_id': incident2.incident_id,
    'incidenttype_id': incident2.it_id,
    'current_state': incident2.current_state.name,
    'occurrence_date': incident2.occurrence_date,
    'last_occurrence_date': incident2.last_occurrence_date,
    'created_date': incident2.created_date,
    'state_history': state_history2,
    'end_date': incident2.end_date,
    'is_open': incident2.is_open,
    'name': incident2.name,
    'environment': incident2.environment,
    'host': json.loads(incident2.host.decode()),
    'logger': json.loads(incident2.logger.decode()),
    'current_label': incident2.current_label,
    'current_severity': incident2.current_severity,
    'is_read': incident2.is_read,
    'occurrences': incident2.occurrences,
    'number_solutions': incident2.number_solutions
}

close_incident = L()
close_incident.__dict__ = incident.__dict__.copy()
close_incident.is_open = 0

another_incident = L()
another_incident.__dict__ = incident.__dict__.copy()
another_incident.incident_id = 10

label_event = L('label_event')
label_event.delete = L()
label_event.filter = L()
label_event.it_id = 1
label_event.label = 'Unknown'
label_event.created_date = datetime_datetime
label_event_dict = {
    'id_field': 'incidenttype_id',
    'incidenttype_id': label_event.it_id,
    'created_date': epoch_micros,
    'field': 'label',
    'label': label_event.label
}


incident_solution = L('incident_solution')
incident_solution.delete = L()
incident_solution.update = L('incident_solution')
incident_solution.incidentsolution_id = 1
incident_solution.solution_script = 'This is a solution'.encode()
incident_solution.solution_actions = json.dumps(['api here']).encode()
incident_solution.it_id = 1
incident_solution.number_solutions = 1
incident_solution.user_likes = json.dumps([])
incident_solution.datasource_uuid = 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf'
incident_solution.solution_likes = 1
incident_solution.it_id_saio = 1

incident_solution_dict = {'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
                          'description': 'A short description',
                          'incidentsolution_id': 1,
                          'incidenttype_id': 1,
                          'liked': True,
                          'steps': 'This is a solution',
                          'total_likes': 1,
                          'user_id': 1}

incident_solution2 = L('incident_solution')
incident_solution2.incidentsolution_id = 2
incident_solution2.solution_script = 'the solution to all'.encode()
incident_solution2.solution_actions = json.dumps(['shell script here'
                                                  ]).encode()
incident_solution2.incidenttype_id = 2
incident_solution2.number_solutions = 1

incident_solution3 = L('incident_solution')
incident_solution3.incidentsolution_id = 3
incident_solution3.solution_script = ''.encode()
incident_solution3.solution_actions = json.dumps([]).encode
incident_solution3.incidenttype_id = 3
incident_solution3.number_solutions = 0

incident_liked_solution = L('incident_liked_solution')
incident_liked_solution.delete = L()
incident_liked_solution.update = L('incident__liked_solution')

incident_state_event = L('incident_state_event')
incident_state_event.incident_id = 1
incident_state = L('incident_state')
incident_state_event.state = 'DISCOVERED'
incident_state_event.created_date = datetime_datetime


response = L('response')
response.status_code = '200 OK'

response_200 = L('response_200')
response_200.status_code = 200

response_201 = L('response')
response_201.status_code = 201

response_204 = L('response')
response_204.status = '204 NO CONTENT'

response_403 = L('response')
response_403.status_code = 403
response_403.status = '403 Unauthorized user'

response_403_dict = {'Cause': 'Unauthorized user', 'Status code': 403}

empty_response = f'[]'
empty_list = {}
none_response = None

auth_token = L('auth_token')

user = L('user')
user.update = L()
user.id = 1
user.email = 'test@ormuco.com'
user.first_name = 'mr'
user.last_name = 'temp'
user.phone_number = 123456789
user.password = 'notsecurepassword'
user.account_picture_id = 1
user.confirmed_at = 123456789
user.active = True
user.encode_auth_token = auth_token
user.account_picture_id = 0
user.disabled_notifications = json.dumps([])
user.is_root = True

user_dict = {
    'id': user.id,
    'email': user.email,
    'first_name': user.first_name,
    'last_name': user.last_name,
    'phone_number': user.phone_number
}

user_short_dict = {
    'id': user.id,
    'email': user.email,
    'first_name': user.first_name,
    'last_name': user.last_name,
}


check_sequence_response = {'model_id': str(1), 'cluster_id': str(1)}

report = {'Status code': 200}
report_202 = {'Status code': 202}
status_code_201 = {'status_code': 201}

auth_response = {
    "token": {
        "is_domain":
        False,
        "methods": ["password"],
        "roles": [{
            "id": "9fe2ff9ee4384b1894a90878d3e92bab",
            "name": "_member_"
        }, {
            "id": "dcf016d8f1694d80b51410888016e042",
            "name": "projectadmin"
        }],
        "expires_at":
        "2018-09-11T12:40:45.000000Z",
        "project": {
            "domain": {
                "id": "aa8401fbce05440f9c7c1943d0e4226e",
                "name": "genieeee@mailinator.com-domain"
            },
            "id": "dc16e499cced435ab71cf1cc16e3ae4b",
            "name": "genieeee@mailinator.com-SuperUATisNumberOne-project"
        },
        "catalog": [{
            "endpoints": [{
                "url":
                "http://10.128.150.100:8004/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "6ad396d3c46645389a9172ee1fbe8285"
            }, {
                "url":
                "http://10.128.150.100:8004/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "c0c7fcd8eac4432abf4d4bc9d8a84bcf"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8004/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "fbbaab8dfb5f4b25ac862747037077e9"
            }],
            "type":
            "orchestration",
            "id":
            "02bd0b81a5ae4892bcc182f20a533043",
            "name":
            "heat"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:9311",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "0fb9134181f24cdebad5a81c1615890a"
            }, {
                "url": "http://10.128.150.100:9311",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "100c55dff208451195711047625f1cb5"
            }, {
                "url": "http://10.128.150.100:9311",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "31509a3bdc50417f9c0f5ab2d03490a8"
            }],
            "type":
            "key-manager",
            "id":
            "0f18e65ff27e4bf39849a0c6a36d99c0",
            "name":
            "barbican"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:8776/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "2721d7aac9eb49c59f9609a27f2d31ae"
            }, {
                "url":
                "http://10.128.150.100:8776/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "73b667d611b841acbe1a8e3ad6b4be6b"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8776/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "d6174644097244eb98e26e60c5b04818"
            }],
            "type":
            "volumev2",
            "id":
            "194fab1853524584af1a1b1bb6b71d05",
            "name":
            "cinderv2"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:9511/v1",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "554bdf26971f4f4bbd19f64ebb00a68c"
            }, {
                "url": "http://10.128.150.100:9511/v1",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "70351a65891140c5bce7c0c122ad7e6b"
            }, {
                "url": "http://10.128.150.100:9511/v1",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "73d0cfaae8b54f4bb393bbb6fd289204"
            }],
            "type":
            "container-infra",
            "id":
            "1e6f08ed9e354ff59bf2a808863e4e7d",
            "name":
            "magnum"
        }, {
            "endpoints": [{
                "url": "http://10.128.150.100:9696",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "201239e785514fccbcba959f880a908a"
            }, {
                "url": "http://10.128.150.100:9696",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "4c11cde14a784696910949c63fa4e508"
            }, {
                "url": "https://api-mtl-uat001.ormuco.com:9696",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "abd946a0bbea49f4a69a54566946962a"
            }],
            "type":
            "network",
            "id":
            "22d21bb50b76429886ac511122d50fb4",
            "name":
            "neutron"
        }, {
            "endpoints": [{
                "url": "http://10.128.150.100:9292",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "3f16ae20423b40a4a6431d5d0891b19c"
            }, {
                "url": "http://10.128.150.100:9292",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "5982e122df2b49b4b74f400717464c27"
            }, {
                "url": "https://api-mtl-uat001.ormuco.com:9292",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "f291a959c16b48c789566857ce7c574d"
            }],
            "type":
            "image",
            "id":
            "2aec186fb224486bb069fef6afe96b3e",
            "name":
            "glance"
        }, {
            "endpoints": [{
                "url": "http://10.128.150.100:9090",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "1f5b293adfd04a9c8ad9d558c5b69da9"
            }, {
                "url": "https://api-mtl-uat001.ormuco.com:9090",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "65c514879349492480beb555b664bc47"
            }, {
                "url": "http://10.128.150.100:9090",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "e535a0d2ec7b4dd9b347805f0c9e4e81"
            }],
            "type":
            "backup",
            "id":
            "3e582be45d55408aabf725204c84ccc1",
            "name":
            "freezer"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:8780",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "86ae2015fb5042b3ad0c5c6fd13517d4"
            }, {
                "url": "http://10.128.150.100:8780",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "9b0e48fbe70146a4a1a1f04c6e2bd90e"
            }, {
                "url": "http://10.128.150.100:8780",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "ef52832d441d4dd897fa2c0ef06de8e6"
            }],
            "type":
            "placement",
            "id":
            "4867d7f8dc7740b8bac76263f99810dd",
            "name":
            "placement"
        }, {
            "endpoints": [{
                "url": "http://10.128.150.100:8000/v1",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "58cebc2e2abf425eabc772c63f228ae4"
            }, {
                "url": "https://api-mtl-uat001.ormuco.com:8000/v1",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "72eee009ccb94c83b07637f454b91c35"
            }, {
                "url": "http://10.128.150.100:8000/v1",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "b37900ee6bc8451e82b57be36f976c54"
            }],
            "type":
            "cloudformation",
            "id":
            "4b662f159a774dc895e0484e3bbc9ca7",
            "name":
            "heat-cfn"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:6780/swift/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "20857a06e5c04aae997dfaaa2b768410"
            }, {
                "url":
                "http://10.128.150.100:6780/swift/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "b6b65463010b4541a529dfd3549ca023"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:6780/swift/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "f7855865248c4e48a618d8f591ad0fe4"
            }],
            "type":
            "object-store",
            "id":
            "6210a29b5e374fb2adbfa388b3154c37",
            "name":
            "swift"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:9001",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "0484b81ab5e34bb19b74508f0a5cc386"
            }, {
                "url": "http://10.128.150.100:9001",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "528c7b15286545cab948cd00604606f4"
            }, {
                "url": "http://10.128.150.100:9001",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "7bacbc62efcd48c686eb5e3c5c8fcf83"
            }],
            "type":
            "dns",
            "id":
            "6253b3f6f48c4fe2a69380329567d273",
            "name":
            "designate"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:8041",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "45b0e50f2af745b4962675615ad37074"
            }, {
                "url": "http://10.128.150.100:8041",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "6080cb08983545b48e72bd9e9da6bb47"
            }, {
                "url": "http://10.128.150.100:8041",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "c13fa09a88124e4fb8b93dc3398c387c"
            }],
            "type":
            "metric",
            "id":
            "6321eacf469f45a6ab412e32427f80d2",
            "name":
            "gnocchi"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:5050",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "6014268b2b7440cc93b219fbdfaa1cd7"
            }, {
                "url": "http://10.128.150.100:5050",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "c7d137fb7abe4e2aacb80a27a005e9d3"
            }, {
                "url": "http://10.128.150.100:5050",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "f54197101c39407391f8ed372e5fe862"
            }],
            "type":
            "baremetal-introspection",
            "id":
            "6c58aca2e4fd400b87963b1beda97077",
            "name":
            "ironic-inspector"
        }, {
            "endpoints": [{
                "url":
                "https://api-mtl-uat001.ormuco.com:8774/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "8ee521ddc9bc4ecd9bf4f4a7bdeee167"
            }, {
                "url":
                "http://10.128.150.100:8774/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "cb4ed586249749d8aed2be05a64857ac"
            }, {
                "url":
                "http://10.128.150.100:8774/v2/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "d3c6de1936214387bd77e386241def56"
            }],
            "type":
            "compute_legacy",
            "id":
            "71cd52d75fdd4cf3a44555591f39505f",
            "name":
            "nova_legacy"
        }, {
            "endpoints": [{
                "url": "http://10.128.150.100:6385",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "53b377ba9d3f45ba9ac86df384880acc"
            }, {
                "url": "https://api-mtl-uat001.ormuco.com:6385",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "5d2aee4e24f44a86b5e847559b114374"
            }, {
                "url": "http://10.128.150.100:6385",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "8d4d8da2118e469b82e91524a89fa08b"
            }],
            "type":
            "baremetal",
            "id":
            "757d9772a7a24813b986efdccfd64ac2",
            "name":
            "ironic"
        }, {
            "endpoints": [{
                "url":
                "https://api-mtl-uat001.ormuco.com:8799/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "2f4447f1073e4fdf9954756e1c4f5bea"
            }, {
                "url":
                "http://10.128.150.100:8799/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "5d5a80d606e3460b92d5be5638f35de0"
            }, {
                "url":
                "http://10.128.150.100:8799/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "980b0a3e76b447b4906d6e528719b164"
            }],
            "type":
            "data-protect",
            "id":
            "9c4cf2135d4c45039e4ff88d81219509",
            "name":
            "karbor"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:5000",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "0f302ac3a46043c7a956937cd78f1fd2"
            }, {
                "url": "http://10.128.150.100:35357",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "b6c5de3cc72546859ef2ccebdc152f8a"
            }, {
                "url": "http://10.128.150.100:5000",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "cc8c2edc7aff46d6b573789b538aac14"
            }],
            "type":
            "identity",
            "id":
            "adb96dfc72e4447fb520d5a2400ae4da",
            "name":
            "keystone"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:8386/v1.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "6f0d08d829184b16ac0455d553b44a48"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8386/v1.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "918118f393494d68af1f8951e8f0bb4f"
            }, {
                "url":
                "http://10.128.150.100:8386/v1.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "c1130a671c984874bf1558736b1554a8"
            }],
            "type":
            "data-processing",
            "id":
            "b29902f8266b44d6b12522e9b1c422a2",
            "name":
            "sahara"
        }, {
            "endpoints": [{
                "url":
                "https://api-mtl-uat001.ormuco.com:8774/v2.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "8776e0b6fdea471a83cec1f95a891afa"
            }, {
                "url":
                "http://10.128.150.100:8774/v2.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "a5e23ebe711d47f4bb32ca6609a6082a"
            }, {
                "url":
                "http://10.128.150.100:8774/v2.1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "d54f1db868be40f9bdbff965ca0c5115"
            }],
            "type":
            "compute",
            "id":
            "bcda5fbdb28f433bbdd25a6ca30c756d",
            "name":
            "nova"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:8779/v1.0/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "8f8bdd635619433d92184c01b87bbb61"
            }, {
                "url":
                "http://10.128.150.100:8779/v1.0/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "91cb3d25c509411ea6cb122c0b898c42"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8779/v1.0/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "bad801856e884ae6a5c53bf863ec2f1f"
            }],
            "type":
            "database",
            "id":
            "be687d1cda9f4f7fa486beb9221e1edf",
            "name":
            "trove"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:9876",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "18ae29bcdb6047d3b9abe11daf156aa8"
            }, {
                "url": "http://10.128.150.100:9876",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "b42761620ecf40efa5e697f3e99f75dd"
            }, {
                "url": "http://10.128.150.100:9876",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "d60e5137bb9b4da4823f430daac315c1"
            }],
            "type":
            "load-balancer",
            "id":
            "c5c695c0b23b499bac4c38af37972085",
            "name":
            "octavia"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:8776/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "535643d8795d43e8ab78b29705f34d76"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8776/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "74770d6a2ad74ad1b0be9051ffcd2170"
            }, {
                "url":
                "http://10.128.150.100:8776/v1/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "e285056f34bb43acb09ff08699795827"
            }],
            "type":
            "volume",
            "id":
            "dd3566a4ce7a4f4499e714c156df08bd",
            "name":
            "cinder"
        }, {
            "endpoints": [{
                "url": "https://api-mtl-uat001.ormuco.com:8042",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "16eacb6307394a85a317c77c5eb4ae41"
            }, {
                "url": "http://10.128.150.100:8042",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "1ee52a23cd62418e9dce4b2f0ae121a8"
            }, {
                "url": "http://10.128.150.100:8042",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "a4047091fa3f4839b01891be9e2ebe63"
            }],
            "type":
            "alarming",
            "id":
            "ddd95a8f40964d24b512449c3ef326cb",
            "name":
            "aodh"
        }, {
            "endpoints": [{
                "url":
                "http://10.128.150.100:8776/v3/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "admin",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "38cf6cc7a7db40109beaddd0f80ff737"
            }, {
                "url":
                "https://api-mtl-uat001.ormuco.com:8776/v3/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "public",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "6d61c4ac2e2a44d4b7132c99fc12cbe9"
            }, {
                "url":
                "http://10.128.150.100:8776/v3/dc16e499cced435ab71cf1cc16e3ae4b",
                "interface": "internal",
                "region": "uat-ca-yul-1",
                "region_id": "uat-ca-yul-1",
                "id": "7b0b7473c5ab48559cb326b99006c91c"
            }],
            "type":
            "volumev3",
            "id":
            "ea196791b25b4befa59332a343944757",
            "name":
            "cinderv3"
        }],
        "user": {
            "password_expires_at": None,
            "domain": {
                "id": "aa8401fbce05440f9c7c1943d0e4226e",
                "name": "genieeee@mailinator.com-domain"
            },
            "id": "0f1a53afeeff4961a4dc80ecfc7e201c",
            "name": "genieeee@mailinator.com"
        },
        "audit_ids": ["GnyQs40NRuqzX_BVDEslBA", "n0gzKpu6Souwx7u0IQpqwg"],
        "issued_at":
        "2018-09-10T12:40:45.000000Z",
        "id":
        "gAAAAABblmZNbc22duIWldsxF6e0LfauMY16TRminnR10gShQrKu7CRBWhfeVcNHxXHCKj4LAu0n4I_PVu1JVWc58bSjmDF1Q4RrDidrx3e6ggwJ2L_DWT6LVUWmUbFMgTfEQvYEzvJCQDRsR1oDTDeN8QoGL-HfYHrtN0aYltsOmZDmh2ZSHFpj4MuI-Jegtop3kFWoMD89"
    }
}

headers = {"Content-Type": "application/json"}

data = {
    "auth": {
        "identity": {
            "methods": ["password"],
            "password": {
                "user": {
                    "name": "genieeee@mailinator.com",
                    "password": "testtesttest"
                }
            }
        },
        "scope": {
            "project": {
                "id": "dc16e499cced435ab71cf1cc16e3ae4b"
            }
        }
    }
}

headers_saio = {
    'user-agent': 'my-app/0.0.1',
    'X-Storage-User': '{}:{}'.format(Config.SAIO_ACCOUNT, Config.SAIO_NAME),
    'X-Storage-Pass': Config.SAIO_PASSWORD
}

token_saio = "AUTH_tk851a0d2b1ca14c0fb1fb2cff8c7444f9"
storage_url_saio = "http://swift-aio:8080/v1/AUTH_cerebro"
object_storage_list = [1, 2, 3]
datasource_uuid_saio = "a92c54c5-b1a5-4311-b476-f028171df345"

authorization_saio = L('authorization_saio')
authorization_saio.headers = {
    'X-Auth-Token': 'X-Auth-Token',
    'X-Storage-Url': 'X-Storage-Url'
}

file = L('file')
file.read = L('read')
file.filename = 'filex.txt'

img_jpeg = L('img_jpeg')
img_jpeg.filename = 'file.jpeg'

img_png = L('img_png')
img_png.filename = 'file.png'

img_svg = L('img_svg')
img_svg.filename = 'file.svg'

connection_status = {
    'datasource_uuid': 'e199ac5c-ee7d-4d73-bb61-ab2b48425adf',
    'datasource_status': 'online',
    'index_name': None,
    'environment_status': 'online'
}

users = [
    {
        "active": True,
        "confirmed": True,
        "email": "oleh.huzei@ormuco.com",
        "first_name": None,
        "id": "e5cf0fd7-2c19-485d-9694-1e35d98dc101",
        "last_name": None,
        "phone_number": None
    }
]

location = 'https://test.hayei.com'
