import unittest
import json
from janrain.capture import Api, config
from janrain.capture.api import api_encode
from janrain.capture.exceptions import *

class TestApi(unittest.TestCase):
    """ Test the api module. """
    def setUp(self):
        client = config.unittest_client()
        self.api = Api(client['apid_uri'], {
            'client_id': client['client_id'],
            'client_secret': client['client_secret']
        })
        self.client = client
    
    def test_api_encode(self):
        # Python natives should be encoded into JSON
        self.assertEqual(api_encode(True), "true")
        self.assertEqual(api_encode(False), "false")
        json.loads(api_encode(['foo', 'bar']))
        json.loads(api_encode({'foo': True, 'bar': None}))
    
    def test_api_object(self):
        # should prepend https:// if protocol is missing
        api = Api("foo.janrain.com")
        self.assertEqual(api.api_url, "https://foo.janrain.com")
        
        # responses should have stat
        result = self.api.call("entity.count", type_name="user")
        self.assertTrue("stat" in result)
        
        # oauth/token returns 400 or 401 which should *not* be a URLError
        with self.assertRaises(ApiResponseError):
            self.api.call("/oauth/token")
        

