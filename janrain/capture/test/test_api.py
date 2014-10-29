import unittest
import json
from janrain.capture import Api, config
from janrain.capture.api import api_encode
from janrain.capture.exceptions import *
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
        result = self.api.call("entity.count", type_name="user")
        self.assertTrue("stat" in result)

        # oauth/token returns 400 or 401 which should *not* be a HTTPError
        with self.assertRaises(ApiResponseError):
            self.api.call("/oauth/token")
