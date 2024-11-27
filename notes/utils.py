import datetime
import flask

from functools import wraps
import notes.errors as error

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
