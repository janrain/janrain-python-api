""" Base class for making API calls to the Janrain API. """
# pylint: disable=E0611
from janrain.capture.exceptions import InvalidApiCallError, ApiResponseError, \
                                       JanrainInvalidUrlError
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError, URLError
from json import loads as json_decode
from json import dumps as json_encode
from contextlib import closing
from base64 import b64encode
from hashlib import sha1
import hmac
import time
import logging

#logging.basicConfig()

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
        return json_encode(value)
    elif type(value) == bool:
        return str(value).lower()
    return value

class Api(object):
    """
    Base object for making API calls to the Janrain API.

    Args:
        api_url  - Absolute URL to API.
        defaults - A dictionary of default parameters to pass to every API call.

    Example:
        defaults = {'client_id': "...", 'client_secret': "..."}
        api = janrain.capture.Api("https://...", defaults)
        count = api.call("entity.count", type_name="user")
    """
    def __init__(self, api_url, defaults={}):
        self.logger = logging.getLogger(__name__)
        if api_url[0:4] == "http":
            self.api_url = api_url
        else:
            self.api_url = "https://" + api_url
        self.defaults = defaults
        self.sign_requests = True

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
            InvalidApiCallError, ApiResponseError
        """
        # Encode values for the API (JSON, bools, nulls)
        params = dict((key, api_encode(value))
            for key, value in kwargs.iteritems() if value is not None)
        params.update(self.defaults)

        if api_call[0] !=  "/":
            api_call = "/" + api_call
        url = self.api_url + api_call
        self.logger.debug(url)

        # Signing the request modifies the request object and params in-place.
        # Sign the request *before* encoding and passing the params.
        request = Request(url)
        if self.sign_requests:
            self.sign_request(request, api_call, params)
        request.add_data(urlencode(params))

        try:
            with closing(urlopen(request)) as response:
                body = response.read()
        except HTTPError as error:
            if error.code in (400, 401): # /oauth/token returns 400 or 401
                body = error.fp.read()
            elif error.code == 404:
                raise InvalidApiCallError(api_call, error.code)
            else:
                raise error
        except URLError as error:
            if error.reason.errno == -2:
                raise JanrainInvalidUrlError("Invalid API URL: " + url)
            else:
                raise error

        return self.parse_response(body)

    def parse_response(self, response):
        """
        Parse the response from the API, decoding the JSON and converting errors
        into exceptions.

        Args:
            response - The JSON response from the Janrain API.

        Returns:
            The response from the API decoded into Python native types.

        Raises:
            ApiResponseError
        """
        data = json_decode(response)

        if data['stat'] == 'error':
            self.logger.debug("Response:\n" + json_encode(data, indent=4))
            try:
                message = data['error_description']
            except KeyError:
                message = data['message']
            raise ApiResponseError(data['code'], data['error'], message, data)
        return data

    def sign_request(self, request, api_call, params):
        """
        Sign the API call by generating an "Authentication" header. This method
        will add headers to the request object and remove auth_token, client_id,
        and client_secret from the parameters if they exist.

        Args:
            request  - A urllib2.Request instance.
            api_call - The API endpoint as a relative URL.
            params   - A dictionary of parameters in the POST to the API.
        """
        # Do not POST authentication parameters. Use them to create an
        # authentication header instead.
        access_token = params.pop('access_token', None)
        client_id = params.pop('client_id', None)
        client_secret = params.pop('client_secret', None)

        self.logger.debug(params)

        # create the authorization header
        if access_token:
            request.add_header("Authorization", "OAuth {}".format(access_token))
        else:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
            data = "{}\n{}\n".format(api_call, timestamp)
            if params:
                kv_str = ["{}={}".format(k, v) for k, v in params.iteritems()]
                kv_str.sort()
                data = data + "\n".join(kv_str) + "\n"
            sha1_str = hmac.new(client_secret, data, sha1).digest()
            hash_str = b64encode(sha1_str)
            request.add_header("Date", timestamp)
            request.add_header("Authorization",
                               "Signature {}:{}".format(client_id, hash_str))

