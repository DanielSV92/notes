import datetime
import flask
import logging

from functools import wraps
import smarty.errors as error

HEADERS = {'Content-Type': 'application/json'}


class AbstractParam(object):
    """
    Abstract class that defines a decorator to get arbitrary values from
    an object and replace kwarg values on the decorated function

    :param str name: name used to search the collection
    :param str param: function kwarg name that will be set, uses value of
        ``name`` if not defined
    :param bool required: whether this param is mandatory

    :raises BadRequest: if required param is missing

    .. seealso::
        :class:`JsonParam`, :class:`SessionParam`, :class:`FormField`
    """
    def __init__(self, name, param=None, required=False):
        super(AbstractParam, self).__init__()
        self.name = name
        self.param = param
        self.param_name = param or name.replace('.', '_')
        self.required = required

    def get_value(self):
        """ getter to override
        :raises ValueError: If the name does not exist.
        :return: a value
        """
        raise NotImplementedError()

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                if self.param_name not in kwargs:
                    kwargs[self.param_name] = self.get_value()
            except ValueError:
                if self.required:
                    response = flask.make_response(
                        flask.jsonify({
                            'message':
                            "missing required parameter " + self.name,
                            'id':
                            'param_invalid',
                            'parameter':
                            self.name,
                            'title':
                            'Bad Request'
                        }), 400)
                    return response
            return f(*args, **kwargs)

        return wrapper


def datetime_to_epoch_micros(date: datetime.datetime) -> int:
    epoch_micros = int(date.timestamp() * 1000000)

    return epoch_micros


def epoch_millis_to_datetime(epoch_millis: int) -> datetime.datetime:
    if epoch_millis > 150000000000:
        date = datetime.datetime.fromtimestamp(epoch_millis / 1000)
    else:
        date = datetime.datetime.fromtimestamp(epoch_millis)

    return date


def datetime_to_epoch_millis(date: datetime.datetime) -> int:
    epoch_millis = int(date.timestamp() * 1000)

    return epoch_millis


def epoch_micros_to_datetime(epoch_micros: int) -> datetime.datetime:
    date = datetime.datetime.fromtimestamp(epoch_micros / 1000000)

    return date


def reformat_datetime(body) -> list:
    start_date_epoch_millis = body.get('start_date', None)
    start_date = None
    if start_date_epoch_millis:
        start_date_epoch_millis = int(start_date_epoch_millis)
        if start_date_epoch_millis < 1500000000000:
            start_date_epoch_millis = start_date_epoch_millis * 1000
        start_date = epoch_millis_to_datetime(start_date_epoch_millis)

    end_date_epoch_millis = body.get('end_date', None)
    end_date = None
    if end_date_epoch_millis:
        end_date_epoch_millis = int(end_date_epoch_millis)
        if end_date_epoch_millis < 1500000000000:
            end_date_epoch_millis = end_date_epoch_millis * 1000
        end_date = epoch_millis_to_datetime(end_date_epoch_millis)

    date_epoch_millis = body.get('date', None)
    date = None
    if date_epoch_millis:
        date_epoch_millis = int(date_epoch_millis)
        if date_epoch_millis < 1500000000000:
            date_epoch_millis = date_epoch_millis * 1000
        date = epoch_millis_to_datetime(date_epoch_millis)
        date = datetime.datetime(*date.timetuple()[:3])

    return [start_date, end_date, date]


def validate_datetime_format(body):
    start_date_epoch_millis = body.get('start_date', None)
    if start_date_epoch_millis:
        try:
            int(start_date_epoch_millis)
        except ValueError:
            raise error.BadRequest(
                message='Parameter "start_date" must be an integer.')

    end_date_epoch_millis = body.get('end_date', None)
    if end_date_epoch_millis:
        try:
            int(end_date_epoch_millis)
        except ValueError:
            raise error.BadRequest(
                message='Parameter "end_date" must be an integer.')

    date_epoch_millis = body.get('date', None)
    if date_epoch_millis:
        try:
            int(date_epoch_millis)
        except ValueError:
            raise error.BadRequest(
                message='Parameter "date" must be an integer.')
