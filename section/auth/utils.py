import datetime
import logging
import re
import requests

from flask_mail import Mail
from flask_mail import Message
import smarty.errors as error

from smarty.domain.models import AccountPicture
from smarty.domain.models import CapabilityList
from smarty.domain.models import DataSource
from smarty.domain.models import DSShare
from smarty.domain.models import Role
from smarty.domain.models import user_datastore
from smarty.extensions import db
from smarty.settings import Config


def user_to_dict(user):
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'active': user.active,
    }


def user_to_short_dict(user):
    return {
        'id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'phone_number': user.phone_number,
        'active': user.active,
    }


def encode_auth_token(user_id):
    """
    Generates the Auth Token
    :return: string
    """
    try:
        payload = {
            'exp':
            datetime.datetime.utcnow() +
            datetime.timedelta(days=0, seconds=3600),
            'iat':
            datetime.datetime.utcnow(),
            'sub':
            user_id,
        }
        return jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')
    except Exception as error:
        return error


def decode_auth_token(auth_token):
    """
    Decodes the auth token
    :param auth_token:
    :return: integer|string
    """
    try:
        payload = jwt.decode(auth_token, 'SECRET_KEY')
        return payload['sub']
    except jwt.ExpiredSignatureError:
        return 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return 'Invalid token. Please log in again.'

