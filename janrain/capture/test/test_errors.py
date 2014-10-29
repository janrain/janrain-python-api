import unittest
from janrain.capture import Api, config
from janrain.capture.exceptions import *
from requests import HTTPError
from os.path import exists
from os.path import expanduser
from os import environ

class TestErrors(unittest.TestCase):
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
