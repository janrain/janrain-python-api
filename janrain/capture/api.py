""" Base class for making API calls to the Janrain API. """
# pylint: disable=E0611
from janrain.capture.exceptions import ApiResponseError
from json import dumps as to_json
from contextlib import closing
from base64 import b64encode
from hashlib import sha1
import hmac
import time
import logging

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
    if type(value) in (dict, list):
        return to_json(value).encode('utf-8')
    if type(value) == bool:
        return str(value).lower().encode('utf-8')
    try: 
        if isinstance(value, basestring):
            return value.encode('utf-8')
    except NameError:
        if isinstance(value, str):
            return value.encode('utf-8')
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
                data = data + "\n".join(kv_str) + "\n"
            sha1_str = hmac.new(
                client_secret,
                data, 
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

    Example:
        defaults = {'client_id': "...", 'client_secret': "..."}
        api = janrain.capture.Api("https://...", defaults)
        count = api.call("entity.count", type_name="user")
    """
    def __init__(self, api_url, defaults={}, compress=True, sign_requests=True):
        if api_url[0:4] == "http":
            self.api_url = api_url
        else:
            self.api_url = "https://" + api_url
        self.defaults = defaults
        self.sign_requests = sign_requests
        self.compress = compress


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
        params = dict((key, api_encode(value))
            for key, value in kwargs.items() if value is not None)
        params.update(self.defaults)

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

        # Print the parameters (for debugging)
        print_params = params.copy()
        if 'client_secret' in print_params:
            print_params['client_secret'] = "CLIENT_SECRET_REMOVED"
        logger.debug(print_params)

        # Accept gzip compression
        if self.compress:
           headers['Accept-encoding'] = 'gzip'

        # Let any exceptions here get raised to the calling code. This includes
        # things like connection errors and timeouts.
        r = requests.post(url, headers=headers, data=params)

        try:
            raise_api_exceptions(r.json())
            if r.status_code not in (200, 400, 401):
                # /oauth/token returns 400 or 401
                r.raise_for_status()
            return r.json()
        except ValueError:
            # The response was not valid JSON (empty body, 5xx errors, etc.)
            r.raise_for_status()
