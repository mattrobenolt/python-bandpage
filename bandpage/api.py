"""
bandpage.api
~~~~~~~~~~~~

:copyright: (c) 2012 by Matt Robenolt, see AUTHORS for more details.
:license: BSD, see LICENSE for more details.
"""

import requests

try:
    import simplejson as json
except ImportError:
    import json  #noqa

# Optional Django support
try:
    from django.conf import settings as django_settings
except ImportError:
    django_settings = {}  #noqa


__all__ = (
    'Bandpage', 'BandpageError', 'BandpageUnauthorized',
    'BandpageNotFound', 'get', 'get_access_token', 'conf', 'search',
)


class conf(object):
    "Global configuration settings"
    CLIENT_ID = None
    SECRET_KEY = None
    ENDPOINT = 'https://api-read.bandpage.com'


class BandpageError(Exception):
    "Generic error response from Bandpage API"
    def __init__(self, status_code):
        self.status_code = status_code
        Exception.__init__(self, 'HTTP Status Code {0}'.format(status_code))


class BandpageUnauthorized(BandpageError):
    "401 or 403 status code response"
    pass


class BandpageNotFound(BandpageError):
    "404 NOT FOUND"
    def __init__(self):
        super(BandpageNotFound, self).__init__(404)


def make_response(response):
    "Wrapper to dynamically construct a response type class"
    if response.status_code in (401, 403):
        raise BandpageUnauthorized(response.status_code)

    if response.status_code == 404:
        raise BandpageNotFound()

    if response.status_code != 200:
        raise BandpageError(response.status_code)

    return json.loads(response.text)


class Bandpage(object):
    def __init__(self, client_id=None, secret_key=None, access_token=None):
        self.client_id = client_id or conf.CLIENT_ID or getattr(django_settings, 'BANDPAGE_CLIENT_ID', None)
        self.secret_key = secret_key or conf.SECRET_KEY or getattr(django_settings, 'BANDPAGE_SECRET_KEY', None)
        self.access_token = access_token
        try:
            # Try to normalize access_token.
            # access_token may either be None, a string, or a dict
            # containing an "access_token" key
            self.access_token = self.access_token['access_token']
        except (TypeError, KeyError):
            pass

    def get_access_token(self, grant_type='client_credentials'):
        "Grab an OAuth access_token"
        return json.loads(self.request('POST', '/token',
            data={'client_id': self.client_id,
                  'grant_type': grant_type},
            auth=(self.client_id, self.secret_key)).text)

    def get(self, endpoint, **kwargs):
        "Make a GET request to the Bandpage API"
        return self._request('GET', '/{0}'.format(endpoint), **kwargs)

    def search(self, query):
        "Query for a Band"
        return self.get('search/band', params={'name': query})

    def request(self, method, endpoint, **kwargs):
        "Make a generic request to the Bandpage API"
        method = method.lower()
        if not method in ('get', 'post'):
            raise TypeError('Invalid method, must be either GET or POST')
        return getattr(requests, method)(conf.ENDPOINT + endpoint, **kwargs)

    def _request(self, *args, **kwargs):
        "Wrapper around response to wrap it in a class"
        kwargs.setdefault('params', {})
        kwargs['params']['access_token'] = kwargs['params'].get('access_token', self.access_token)
        return make_response(self.request(*args, **kwargs))


##############################
# Public convenience methods #
##############################

def get(endpoint, access_token=None):
    "Make a GET request to the Bandpage API using default auth"
    return Bandpage(access_token=access_token).get(endpoint)


def search(query, access_token=None):
    "Query for a Band"
    return Bandpage(access_token=access_token).search(query)


def get_access_token(client_id=None, secret_key=None):
    "Grab an OAuth access_token using default auth"
    return Bandpage(client_id=client_id, secret_key=secret_key).get_access_token()
