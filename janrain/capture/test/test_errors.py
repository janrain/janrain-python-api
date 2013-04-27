import unittest
from janrain.capture import Api, config
from janrain.capture.exceptions import *

class TestErrors(unittest.TestCase):
    def setUp(self):
        client = config.unittest_client()
        self.api = Api(client['apid_uri'], {
            'client_id': client['client_id'],
            'client_secret': client['client_secret']
        })
                           
    def test_invalid_api_call_error(self):
        with self.assertRaises(InvalidApiCallError):
            self.api.call('/foobar')
    
    def test_invalid_url_error(self):
        with self.assertRaises(JanrainInvalidUrlError):
            orig_url = self.api.api_url
            self.api.api_url = "https://foobar.janraincapture.com"
            self.api.call("/entity")
            self.api.api_url = orig_url
            
    def test_api_response_error(self):
        with self.assertRaises(ApiResponseError):
            self.api.call('/entity')

    
