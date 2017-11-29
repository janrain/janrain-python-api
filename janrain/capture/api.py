""" Base class for making API calls to the Janrain API. """
# pylint: disable=E0611
from __future__ import unicode_literals
from janrain.capture.exceptions import ApiResponseError
from janrain.capture.version import get_version
from json import dumps as to_json
from contextlib import closing
from base64 import b64encode
from hashlib import sha1
import hmac
import time
import logging
import sys

logger = logging.getLogger(__name__)

# Use a try/catch when importing requests so that the setup.py script can still
# import from __init__.py without failing.
try:
    import requests
except ImportError:
    logger.warn("Missing 'requests' module. Install using 'pip install " \
                "requests'.")


def api_encode(value):
    """
    Encodes a native Python value in a way that the API expects. Encodes lists
    and dicts to JSON and boolean values to 'true' or 'false'.

    Args:
        value - The Python value to encode.

    Returns:
        The value encoded for the Janrain API.
    """
    if isinstance(value, (dict, list, tuple)):
        value = to_json(value)
    elif value is True:
        value = 'true'
    elif value is False:
        value = 'false'
    if sys.version_info[0] < 3:
        if isinstance(value, unicode):
            value = value.encode('utf-8')
    else:
        if isinstance(value, str):
            value = value.encode('utf-8')
    return value


def api_decode(value):
    """
    Convert bytestrings from utf-8 to unicode.
    Anything else is returned untouched.

    Args:
        value - The Python value to decode.

    Returns:
        The value decoded into unicode if it was a bytestring
    """
    if sys.version_info[0] < 3:
        if isinstance(value, str):
            value = value.decode('utf-8')
    else:
        if isinstance(value, bytes):
            value = value.decode('utf-8')
    return value


def generate_signature(api_call, unsigned_params):
        """
        Sign the API call by generating an "Authentication" header.

        Args:
            api_call        - The API endpoint as a relative URL.
            unsigned_params - A dictionary of parameters in the POST to the API.

        Returns:
            A 2-tuple containing the HTTP headers needed to sign the request and
            the modified parameters which should be sent to the request.
        """
        params = unsigned_params.copy()
        params = {k: api_decode(v) for k, v in params.items()}

        # Do not POST authentication parameters. Use them to create an
        # authentication header instead.
        access_token = params.pop('access_token', None)
        client_id = params.pop('client_id', None)
        client_secret = params.pop('client_secret', None)

        headers = {}
        if access_token:
            # Simply use the access token if provided rather than id/secret
            headers['Authorization'] = "OAuth {}".format(access_token)
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            data = "{}\n{}\n".format(api_call, timestamp)
            if params:
                kv_str = ["{}={}".format(k, v)
                    for k, v in params.items()]
                kv_str.sort()
                data += "\n".join(kv_str) + "\n"
            sha1_str = hmac.new(
                client_secret.encode('utf-8'),
                data.encode('utf-8'),
                sha1
            ).digest()
            hash_str = b64encode(sha1_str)
            headers['Date'] = timestamp
            signature = "Signature {}:{}".format(
                client_id,
                hash_str.decode('utf-8'))
            headers['Authorization'] = signature
            logger.debug(signature)

        return headers, params


def raise_api_exceptions(response):
    """
    Parse the response from the API converting errors into exceptions.

    Args:
        response - The JSON response from the Janrain API.

    Raises:
        ApiResponseError
    """
    if response['stat'] == 'error':
        logger.debug("Response:\n" + to_json(response, indent=4))
        try:
            message = response['error_description']
        except KeyError:
            message = response['message']
        raise ApiResponseError(response['code'], response['error'], \
                               message, response)

class Api(object):
    """
    Base object for making API calls to the Janrain API.

    Args:
        api_url       - Absolute URL to API.
        defaults      - A dictionary of default params to pass to every call.
        compress      - A boolean indicating to use gzip compression.
        sign_requests - A boolean indicating to sign the requests.
        user_agent    - A string to use for the user agent header.
        request_timeout - Either an int or a tuple indicating how long to wait
                          for Janrain to respond to requests.

    Example:
        defaults = {'client_id': "...", 'client_secret': "..."}
        api = janrain.capture.Api("https://...", defaults)
        count = api.call("entity.count", type_name="user")
    """
    def __init__(self, api_url, defaults={}, compress=True, sign_requests=True,
                 user_agent=None, request_timeout=None):

        if api_url[0:4] == "http":
            self.api_url = api_url
        else:
            self.api_url = "https://" + api_url

        self.defaults = defaults
        self.sign_requests = sign_requests
        self.compress = compress
        self.request_timeout = request_timeout

        if not user_agent:
            self.user_agent = "janrain-python-api {}".format(get_version())
        else:
            self.user_agent = user_agent


    def call(self, api_call, **kwargs):
        """
        Low-level method for making API calls. It handles encoding the
        parameters, constructing authentication headers, decoding the response,
        and converting API error responses into Python exceptions.

        Args:
            api_call - The API endpoint as a relative URL.

        Keyword Args:
            Keyword arguments are specific to the api_call and can be found in
            the Janrain API documentation at:
            http://developers.janrain.com/documentation/capture/restful_api/

        Raises:
            ApiResponseError
        """
        # Encode values for the API (JSON, bools, nulls)
        params = self.defaults.copy()
        for key, value in kwargs.items():
            if value is not None:
                params[key] = value
        params = {k: api_encode(v) for k, v in params.items()}

        if api_call[0] !=  "/":
            api_call = "/" + api_call
        url = self.api_url + api_call
        logger.debug(url)

        # Signing the request modifies the request object and params in-place.
        # Sign the request *before* encoding and passing the params.
        if self.sign_requests:
            headers, params = generate_signature(api_call, params)
        else:
            headers = {}

        # Custom user agent string
        headers['User-Agent'] = self.user_agent

        # Print the parameters (for debugging)
        print_params = params.copy()
        if 'client_secret' in print_params:
            print_params['client_secret'] = "REDACTED"
        logger.debug(print_params)

        # Accept gzip compression
        if self.compress:
           headers['Accept-encoding'] = 'gzip'

        # Let any exceptions here get raised to the calling code. This includes
        # things like connection errors and timeouts.
        r = requests.post(url, headers=headers, data=params, timeout=self.request_timeout)

        try:
            raise_api_exceptions(r.json())
            if r.status_code not in (200, 400, 401):
                # /oauth/token returns 400 or 401
                r.raise_for_status()
            return r.json()
        except ValueError:
            # The response was not valid JSON (empty body, 5xx errors, etc.)
            r.raise_for_status()
