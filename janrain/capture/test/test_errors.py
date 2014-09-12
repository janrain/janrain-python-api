import unittest
from janrain.capture import Api, config
from janrain.capture.exceptions import *
from requests import HTTPError
from os.path import exists
from os.path import expanduser
from os import environ

class TestErrors(unittest.TestCase):
    def setUp(self):
        client = config.get_client('janrain-capture-api-unittest')
        self.api = Api(client['apid_uri'], {
            'client_id': client['client_id'],
            'client_secret': client['client_secret']
        })

    @unittest.skipUnless(
        exists(expanduser('~/.janrain-capture')) or environ.get('JANRAIN_CONFIG'), 
        "Config file or enviroment variable is required")
    def test_api_response_error(self):
        with self.assertRaises(ApiResponseError):
            self.api.call('/foobar')

        with self.assertRaises(ApiResponseError):
            self.api.call('/entity')

        # HTTP errors come from requests library
        self.api.api_url = self.api.api_url.replace('https:', 'http:')
        with self.assertRaises(HTTPError):
            self.api.call('/entity')
        self.api.api_url = self.api.api_url.replace('http:', 'https:')
