import mock
import requests
import unittest
import json
from janrain.capture import Api, config
from janrain.capture.api import api_encode
from janrain.capture.exceptions import *
from janrain.capture import version
from os.path import exists
from os.path import expanduser
from os import environ


class TestApi(unittest.TestCase):
    """ Test the api module. """
    def setUp(self):
        try:
            client = config.get_client('janrain-capture-api-unittest')
            apid_uri = client['apid_uri']
            client_id = client['client_id']
            client_secret = client['client_secret']
        except:
            apid_uri = environ['APID_URI']
            client_id = environ['CLIENT_ID']
            client_secret = environ['CLIENT_SECRET']

        self.api = Api(apid_uri, {
            'client_id': client_id,
            'client_secret': client_secret,
        })

    def test_api_encode(self):
        # Python natives should be encoded into JSON
        self.assertEqual(api_encode(True), b"true")
        self.assertEqual(api_encode(False), b"false")
        json.loads(api_encode(['foo', 'bar']).decode('utf-8'))
        json.loads(api_encode({'foo': True, 'bar': None}).decode('utf-8'))

    def test_api_object(self):
        # should prepend https:// if protocol is missing
        api = Api("foo.janrain.com")
        self.assertEqual(api.api_url, "https://foo.janrain.com")

        # responses should have stat
        result = self.api.call("clients/list", has_features=["owner"])
        self.assertTrue("stat" in result)

        # oauth/token returns 400 or 401 which should *not* be a HTTPError
        with self.assertRaises(ApiResponseError):
            self.api.call("/oauth/token")

    def test_user_agent(self):
        # default user agent string will be used if not defined when object is
        # instantiated
        api1 = Api("foo.janrain.com")
        self.assertIsNotNone(api1.user_agent)

        api2 = Api("foo.janrain.com", user_agent="foobar")
        self.assertEqual(api2.user_agent, "foobar")

    def test_request_timeout(self):
        # The request_timeout should be passed to requests.post
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"stat": "ok"}'

        api = Api("foo.janrain.com", {'client_id': 123, 'client_secret': '456'}, request_timeout=5)

        with mock.patch('janrain.capture.api.requests.post', return_value=response) as mock_post:
            api.call("clients/list", has_features=["owner"])
            self.assertEqual(mock_post.call_args[1]['timeout'], 5)
