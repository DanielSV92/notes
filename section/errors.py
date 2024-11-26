import logging
import logging.config
from uuid import uuid4

from typing import Dict, Union, Type
from builtins import super
from builtins import str

try:
    from requests.exceptions import RequestException
    imported_requests = True
except ImportError:
    imported_requests = False

try:
    from werkzeug.exceptions import HTTPException
    imported_werkzeug = True
except ImportError:
    imported_werkzeug = False

import ujson

error_logger = logging.getLogger("ormuco_oh_no")


class InvalidError(Exception):
    pass


class BasicHTTPError(Exception):
    """
    Basic Exception class that represents an Http Response
    with response text and status
    """

    def __init__(self, text='', status=500):
        """
        :param str text: the response's body text
        :param int status: the response status
        """

        self.text = text
        self.status = status


class BaseError(Exception):
    """
        Base Error class for exceptions.
    """

    def __init__(self, code, title, message, private_message=None, key=None,
                 public=False):
        """
        :param int code: HTTP status code related to this error.
        :param str title: Short name for the error.
        :param str message: Descriptive message of the error.
        :param str private_message: Descriptive message of the error.
        :param str key: Optional unique slugified key to help translate
            error messages.
        :param bool public: Is this error public
        """

        self.code = code
        self.error_id = str(uuid4())
        self.title = title
        self.message = message
        self.private_message = private_message
        self.key = key
        self.public = public

    __init__.__annotations__ = {
        'code': int,
        'error_id': str,
        'message': str,
        'private_message': str,
        'key': str,
        'public': bool
    }

    def __str__(self):
        return '[{}] {}'.format(self.code, self.message)

    __str__.__annotations__ = {'return': str}

    def __repr__(self):
        return ujson.dumps(self.to_dict())

    __repr__.__annotations__ = {'return': str}

    def to_dict(self, omit_error_id=False):
        """
        Generates the representation of the Error as a Dict.

        :param bool omit_error_id: if true it would not include the error_id

        :return Dict[str, Union[int, str]]: Dict with ``code``, ``title``,
            ``message`` and ``key`` keys.
        """
        dic = {
            'error_id': self.error_id,
            'code': self.code,
            'title': self.title,
            'message': self.message,
            'key': self.key,
            'public': self.public
        }

        if omit_error_id:
            dic.pop('error_id')

        return dic

    to_dict.__annotations = {
        'omit_error_id': bool,
        'return': Dict[str, Union[int, str]]
    }


class Error(BaseError):
    """
    Base Error Class: All the concrete error Exception class should inherits
    this class
    """

    def __init__(self, message=None, code=None, title=None,
                 private_message=None, key=None, public=None):
        """
        Initialize error

        :param str message:
        :param int code:
        :param str private_message:
        :param str key:
        :param bool public:
        """
        super().__init__(code or self.code, title or self.title, message or
                         self.message, private_message=private_message,
                         key=key or self.key, public=public or self.public)

    __init__.__annotations__ = {
        'message': str,
        'code': int,
        'private_message': str,
        'key': str,
        'public': bool
    }

    def log_error(self, logger=None, message='', private_message=''):
        """
        Log the error

        :param Logger logger: Logger object
        :param str message: Message to append to the exception message
        :param str private_message: Private Message to append to the exception
            private message
        """
        private_msg = self.private_message if self.private_message else ''
        if private_message:
            private_msg += '\n' + private_message
        msg = self.message if self.message else ''
        if message:
            msg += '\n' + message

        error_msg = '{} \n {} \n {}'.format(msg, private_msg, repr(self))

        extra = {'tags': self.to_dict()}

        if logger:
            logger.exception(error_msg, extra=extra)
        else:
            logging.exception(error_msg, extra=extra)

    log_error.__annotations__ = {
        'logger': logging.Logger,
        'message': str,
        'private_message': str
    }


class MultipleChoice(Error):
    code = 300
    title = 'Error'
    message = 'Multiple options for the resource found'
    key = 'multiple_choice'
    public = True


class MovedPermanently(Error):
    code = 301
    title = 'Error'
    message = 'The requested resource has been assigned a new permanent URI '
    key = 'moved'
    public = True


class Found(Error):
    code = 302
    title = 'Found'
    message = 'The requested resource resides temporarily under a ' \
              'different URI. '
    key = 'found'
    public = True


class BadRequest(Error):
    code = 400
    title = 'Bad Request'
    message = 'The request can\'t be processed'
    key = 'bad_request'
    public = True


class Unauthorized(Error):
    code = 401
    title = 'Unauthorized'
    message = 'Authentication failed'
    key = 'unauthorized'
    public = True


class Forbidden(Error):
    code = 403
    title = 'Forbidden'
    message = 'Permission denied'
    key = 'forbidden'
    public = True


class CreditCardCheck(Error):
    code = 403
    title = 'Credit card validation error'
    message = 'Failed to validate credit card'
    key = 'credit_card_check'
    public = True


class MethodNotAllowed(Error):
    code = 405
    title = 'Method not Allowed'
    message = 'A request was made of a resource using a request method not ' \
              'supported by that resource'
    key = 'not_allowed'
    public = True


class NotFound(Error):
    code = 404
    title = 'Not found'
    message = 'Resource not found'
    key = 'not_found'
    public = True


class NotAcceptable(Error):
    code = 406
    title = 'Not acceptable'
    message = 'Content-Type must be application/json'
    key = 'not_acceptable'
    public = True


class RequestTimeout(Error):
    code = 408
    title = 'Request Timeout'
    message = 'The server timed out waiting for the request'
    key = 'request_timeout'
    public = True


class Conflict(Error):
    code = 409
    title = 'Conflict'
    message = 'The request could not be completed due to a conflict with the '\
              'current state of the target resource'
    key = 'conflict'
    public = True


class PayloadTooLarge(Error):
    code = 413
    title = 'Payload Too Large'
    message = 'The request payload is larger than the server is willing or ' \
              'able to process.'
    key = 'payload_too_large'
    public = True


class ContentRangeError(Error):
    code = 416
    title = 'Content Range Error'
    message = 'The server cannot serve the requested Content-Range'
    key = 'payload_too_large'
    public = True


class TooManyRequests(Error):
    code = 429
    title = 'Too Many Requests'
    message = 'The user has sent too many requests in a given amount of time.'
    key = 'too_many_requests'
    public = True


class TokenRequired(Error):
    code = 499
    title = 'TokenRequired'
    message = 'Token Required'
    key = 'token_required'
    public = True


class ServerError(Error):
    code = 500
    title = 'Internal Server Error'
    message = 'Something wrong happened...'
    key = 'server_error'
    public = False


class MultipleResultsFound(Error):
    """
    Error raised when we try to query for one specific row using function
        ``find_one`` and receive no result.

    Match SQLAlchemy exception ``sqlalchemy.orm.exc.MultipleResultsFound``.
    """
    code = 500
    title = 'Multiple results found'
    message = ('A single database result was required but more than one were '
               'found')
    key = 'sql_multiple_results_found'
    public = False


class MissingDefaultValue(Error):
    """
    Error raised when a default value is missing for a Model.
    """
    code = 500
    title = 'Default Value Missing'
    message = 'Missing default value when querying object.'
    key = 'missing_defaul_value'
    public = False


class GenericError(Error):
    """
    Error raised when a default value is missing for a Model.
    """
    code = 500
    title = 'Error'
    message = 'An Error has occurred'
    key = 'generic_error'
    public = False


class BadGateway(Error):
    code = 502
    title = 'Bad Gateway'
    message = 'The server was acting as a gateway or proxy and received an' \
              ' invalid response from the upstream server.'
    key = 'bad_gateway'
    public = True


class ServiceUnavailable(Error):
    code = 503
    title = 'Service Unavailable'
    message = 'The server is currently unavailable'
    key = 'service_unavailable'
    public = True


class GatewayTimeout(Error):
    code = 504
    title = 'Gateway Timeout'
    message = 'The server was acting as a gateway or proxy and did not ' \
              'receive a timely response from the upstream server.'
    key = 'gateway_timeout'
    public = True


class NoSuchObject(Exception):
    pass


class DeletionFail(Exception):
    pass


code_error_map = {
    300: MultipleChoice,
    301: MovedPermanently,
    302: Found,
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
    406: NotAcceptable,
    408: RequestTimeout,
    409: Conflict,
    413: PayloadTooLarge,
    416: ContentRangeError,
    429: TooManyRequests,
    499: TokenRequired,
    500: ServerError,
    502: BadGateway,
    504: GatewayTimeout
}

key_error_map = {
    'bad_request': BadRequest,
    'unauthorized': Unauthorized,
    'forbidden': Forbidden,
    'not_found': NotFound,
    'not_acceptable': NotAcceptable,
    'conflict': Conflict,
    'token_required': TokenRequired,
    'server_error': ServerError,
    'credit_card_check': CreditCardCheck,
    'sql_multiple_results_found': MultipleResultsFound,
    'missing_defaul_value': MissingDefaultValue,
}


def code_to_error(http_error_code, error_message=None):
    """
    Translates an error code to the corresponding subclass of :class:`Error`
    and defaults to :class:`ServerError` if error code is not defined.

    :param int http_error_code: HTTP status code.
    :param error_message: Custom message to describe the error.

    :return BaseError: Instance of a subclass of :class:`Error`.
    """
    error_class = code_error_map.get(http_error_code, None)
    if error_class:
        return error_class(message=error_message)
    return GenericError(code=http_error_code, message=error_message)


code_to_error.__annotations__ = {
    'http_error_code': int,
    'error_message': str,
    'return': BaseError
}


def response_to_error(response_text, response_status):
    """
    Get the corresponding Error object given a response text and status

    :param str response_text: response text body
    :param int response_status: response status code
    :return Error: The corresponding Error Object
    """

    try:
        error_response = ujson.loads(response_text)
    except Exception:
        error_response = {'code': response_status}

    if 'code' not in error_response:
        error_response['code'] = response_status

    return dict_to_error(error_response, cannot_fail=True)


def dict_to_error(error_dict, cannot_fail=True):
    """
    Reconstruct an error. It takes an Error representation in a dictionary
    format and returns Error object

    :param Dict[str, str] error_dict: error dictionary representation
    :param bool cannot_fail: If true it would return a general ServerError in
        the case something goes wrong, and if false if something goes wrong it
        would raise an InvalidError exception

    :return Type(Error): An object of subtype Error that match the given error
        representation
    """

    try:

        code = error_dict.get('code')
        key = error_dict.get('key')

        if key in key_error_map.keys():
            # known key
            error = key_error_map[key](message=error_dict.get('message'))

        elif code in code_error_map.keys():
            # match status code
            error_code = error_dict.get('code', 500)
            error = code_error_map[error_code](
                message=error_dict.get('message'))
        elif code:
            error = GenericError(**error_dict)
        else:
            error = ServerError(**error_dict)

        return error

    except Exception as e:

        error_logger.exception("dict_to_error()")
        if cannot_fail:
            return ServerError(private_message=str(e))
        else:
            raise InvalidError()


dict_to_error.__annotations__ = {
    'error_dict': Dict[str, str],
    'cannot_fail': bool,
    'return': Type[Error]
}


def get_unknow_exception_status(e):

    if hasattr(e, "response") and hasattr(e.response, "status_code"):
        # Like a requests RequestException
        try:
            return e.response.status_code
        except Exception:
            pass

    if hasattr(e, "status_code"):
        try:
            return int(e.status_code)
        except Exception:
            pass
    elif hasattr(e, "code"):
        try:
            return int(e.code)
        except Exception:
            pass
    elif hasattr(e, "http_status"):
        try:
            return int(e.http_status)
        except Exception:
            pass

    return None


def get_unknown_exception_text(e):

    try:
        text = str(e)
        if text:
            return text

        if hasattr(e, "response"):
            if hasattr(e.response, "description"):
                text = e.response.description
            elif hasattr(e.response, "message"):
                text = e.response.message
            else:
                text = None
        elif hasattr(e, "message"):
            text = e.message
        elif hasattr(e, "description"):
            text = e.description
        elif hasattr(e, "text"):
            text = e.text
        else:
            text = None
    except Exception:
        text = None

    return text


def handle_unknown_exception(e):
    """
    To try to handle an unknown exception by guessing its attributes.
    :param e: Exception
    :return:
    """

    status = get_unknow_exception_status(e)
    text = get_unknown_exception_text(e)

    if status:
        return code_to_error(status, error_message=text)

    return ServerError(message=text)


def handle_exception(e, log_exception=True, logger=None, message="",
                     private_message=""):
    """
    Handle exceptions, sends the logging message and return an exception
    representation as a dictionary

    :param Exception e: The Exception Error. It could be an instance of Error
        or Exception class
    :param bool log_exception: Boolean to send error to log (default to True)
    :param Logger logger: Logger handling the log messages
    :param str message: Message to append to the exception message
    :param str private_message: Private Message to append to the exception
        private message

    :return Dict: A dictionary representation of the error message
    """

    try:
        text = ''
        status = 500
        error = None

        if issubclass(type(e), Error):
            error = e

        elif imported_requests and issubclass(type(e), RequestException):
            text, status = handle_response(e, text, status)

        elif imported_werkzeug and issubclass(type(e), HTTPException):
            text, status = handle_description(e, text, status)

        elif issubclass(type(e), BasicHTTPError):
            text, status = handle_basic_hhtp(e, text, status)

        else:
            error = handle_unknown_exception(e)

        if not error:
            error = response_to_error(response_text=text,
                                      response_status=status)

    except Exception as e:
        error = ServerError()

    if log_exception:
        error.log_error(logger=logger, message=message,
                        private_message=private_message)
    return error


def handle_response(e, text, status):
    if hasattr(e, "response") and e.response is not None:
        if hasattr(e.response, "text"):
            text = e.response.text
        if hasattr(e.response, "status_code"):
            status = e.response.status_code

    return text, status


def handle_description(e, text, status):
    if hasattr(e, "description"):
        text = e.description
    if hasattr(e, "code"):
        status = e.code

    return text, status


def handle_basic_hhtp(e, text, status):
    if hasattr(e, "text"):
        text = e.text
    if hasattr(e, "status"):
        status = e.status

    return text, status


handle_exception.__annotations__ = {
    'e': Exception,
    'log_exception': bool,
    'logger': logging.Logger,
    'message': str,
    'private_message': str
}
