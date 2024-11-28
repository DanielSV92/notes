import enum


class IncidentState(enum.Enum):
    # TODO define all actual states.
    # TODO define how to handle groups of related states.
    DISCOVERED = enum.auto()
    INVESTIGATING = enum.auto()
    REPRODUCING_ENVIRONMENT = enum.auto()
    SIMULATING_INCIDENT = enum.auto()
    RESOLVING_SIMULATED_INCIDENT = enum.auto()
    RESOLVING_PRODUCTION_INCIDENT = enum.auto()
    RESOLVED = enum.auto()
    REJECTED_BY_USER = enum.auto()
    AUTOMATICALLY_CLOSED = enum.auto()
    ARCHIVED = enum.auto()

    # For Help Desk
    NEW = enum.auto
    OPEN = enum.auto()
    PENDING_DEVELOPER = enum.auto()
    PENDING_REMINDER = enum.auto()
    PENDING_CUSTOMER = enum.auto()
    PENDING_DEPLOY = enum.auto()
    PENDING_CLOSE = enum.auto()
    BLOCKED = enum.auto()
    MERGED = enum.auto()
    CLOSED = enum.auto()

    @classmethod
    def closed_states(cls):
        return [
            cls.RESOLVED, cls.REJECTED_BY_USER, cls.AUTOMATICALLY_CLOSED,
            cls.ARCHIVED, cls.CLOSED, cls.MERGED
        ]

    @classmethod
    def closed_states_for_user(cls):
        return [
            {
                'Resolved': cls.RESOLVED
            },
            {
                'Rejected by User': cls.REJECTED_BY_USER
            },
            {
                'Archived': cls.ARCHIVED
            }
        ]

    @classmethod
    def open_states(cls):
        return [
            {
                'Discovered': cls.DISCOVERED
            },
            {
                'Investigating': cls.INVESTIGATING
            },
            {
                'Resolving Production Incident': cls.RESOLVING_PRODUCTION_INCIDENT
            },
            {
                'Resolving Simulated Incident': cls.RESOLVING_SIMULATED_INCIDENT
            },
            {
                'Simulating Incident': cls.SIMULATING_INCIDENT
            },
            {
                'Reproducing Environment': cls.REPRODUCING_ENVIRONMENT
            }
        ]

    @classmethod
    def closed_states_hd(cls):
        return [
            {
                'Closed': cls.CLOSED,
                'Merged': cls.MERGED
            }
        ]

    @classmethod
    def open_states_hd(cls):
        return [
            {
                'New': cls.NEW
            },
            {
                'Open': cls.OPEN
            },
            {
                'Pending developer': cls.PENDING_DEVELOPER
            },
            {
                'Pending reminder': cls.PENDING_REMINDER
            },
            {
                'Pending customer': cls.PENDING_CUSTOMER
            },
            {
                'Pending deploy': cls.PENDING_DEPLOY
            },
            {
                'Pending close': cls.PENDING_CLOSE
            },
            {
                'Blocked': cls.BLOCKED
            }
        ]


class IncidentSeverity(enum.Enum):
    critical = enum.auto()
    high = enum.auto()
    medium = enum.auto()
    low = enum.auto()
    healthy = enum.auto()


class AlertType(enum.Enum):
    email = enum.auto()
    slack = enum.auto()


class AlertScope(enum.Enum):
    data_source_type = enum.auto()
    environment = enum.auto()
    incident_type = enum.auto()
    logger = enum.auto()
    metric = enum.auto()
    service_up = enum.auto()
    deos_user = enum.auto()

    @classmethod
    def data_source_type_trigger(cls):
        return AlertTrigger.data_source_type_trigger()

    @classmethod
    def environment_trigger(cls):
        return AlertTrigger.environment_trigger()

    @classmethod
    def incident_type_trigger(cls):
        return AlertTrigger.incident_type_trigger()

    @classmethod
    def logger_trigger(cls):
        return AlertTrigger.logger_trigger()

    @classmethod
    def metric_trigger(cls):
        return AlertTrigger.metric_trigger()

    @classmethod
    def service_up_trigger(cls):
        return AlertTrigger.service_up_trigger()

    @classmethod
    def deos_user_trigger(cls):
        return AlertTrigger.deos_user_trigger()


class AlertTrigger(enum.Enum):
    new_incident_type = enum.auto()
    new_incident = enum.auto()
    incident_reopened = enum.auto()
    new_incident_with_incident_type = enum.auto()
    logger_combination = enum.auto()
    metric_value = enum.auto()
    service_up = enum.auto()
    deos_user = enum.auto()
    elk_fluentd_issue = enum.auto()
    unread_email = enum.auto()
    metric_issue = enum.auto

    @classmethod
    def data_source_type_trigger(cls):
        return [{
            'type': cls.new_incident_type.name,
            'description': 'New incident_type detected'
        }]

    @classmethod
    def environment_trigger(cls):
        return [
            {
                'type': cls.new_incident.name,
                'description': 'New ticket is open'
            }, {
                'type': cls.incident_reopened.name,
                'description': 'A ticket is re-open'
            }, {
                'type': cls.elk_fluentd_issue.name,
                'description': 'No logs from ELK'
            }, {
                'type': cls.unread_email.name,
                'description': 'Unread email from SERVER'
            }, {
                'type': cls.metric_issue.name,
                'description': 'No metrics from Prometheus'
            }
        ]

    @classmethod
    def incident_type_trigger(cls):
        return [{
            'type': cls.new_incident_with_incident_type.name,
            'description': 'New ticked from a known incident_type'
        }]

    @classmethod
    def logger_trigger(cls):
        return [{
            'type': cls.logger_combination.name,
            'description': 'A logger combination seen in a ticket'
        }]

    @classmethod
    def metric_trigger(cls):
        return [
            # {
            #     'type': cls.metric_value_below.name,
            #     'description': 'A metric value is below a threshold'
            # },
            {
                'type': cls.metric_value.name,
                'description': 'A metric value exceeds a threshold'
            }
        ]

    @classmethod
    def service_up_trigger(cls):
        return [
            {
                'type': cls.service_up.name,
                'description': 'A service goes down'
            }
        ]

    @classmethod
    def deos_user_trigger(cls):
        return [
            {
                'type': cls.deos_user.name,
                'description': 'A user exceed resource usage'
            }
        ]


class ReactionType(enum.Enum):
    api = enum.auto()
    ssh = enum.auto()


class ReactionRunType(enum.Enum):
    manual = enum.auto()
    automatic = enum.auto()


class ReactionScope(enum.Enum):
    incident_type = enum.auto()

    @classmethod
    def data_source_type_trigger(cls):
        return ReactionTrigger.data_source_type_trigger()

    @classmethod
    def environment_trigger(cls):
        return ReactionTrigger.environment_trigger()

    @classmethod
    def incident_type_trigger(cls):
        return ReactionTrigger.incident_type_trigger()


class ReactionTrigger(enum.Enum):
    new_incident_type = enum.auto()
    new_incident = enum.auto()
    incident_reopened = enum.auto()
    new_incident_with_incident_type = enum.auto()

    @classmethod
    def data_source_type_trigger(cls):
        return [{
            'type': cls.new_incident_type.name,
            'description': 'New incident_type detected'
        }]

    @classmethod
    def environment_trigger(cls):
        return [{
            'type': cls.new_incident.name,
            'description': 'New ticket is open'
        }, {
            'type': cls.incident_reopened.name,
            'description': 'A ticket is re-open'
        }]

    @classmethod
    def incident_type_trigger(cls):
        return [{
            'type': cls.new_incident_with_incident_type.name,
            'description': 'New ticked from a known incident_type'
        }]


class FlagStatus(enum.Enum):
    open = enum.auto()
    re_open = enum.auto()
    under_revision = enum.auto()
    closed = enum.auto()


class ActionType(enum.Enum):
    """Enumeration indicating different types of action which may be executed
    to reproduce contexts or incidents or resolve incidents.
    """
    shell = enum.auto()
