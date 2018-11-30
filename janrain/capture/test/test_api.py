import sys
import time
import unittest
from requests import Session
import json

try:
    from mock import patch, Mock
except ImportError:
    from unittest.mock import patch, Mock

from janrain.capture import Api, config
from janrain.capture.api import api_encode, api_decode, generate_signature


class TestApi(unittest.TestCase):
    """ Test API module """
    def test_api_encode(self):
        """ Values are encoded as Janrain API expects """
        self.assertEqual(api_encode(True), b"true")
        self.assertEqual(api_encode(False), b"false")

        if sys.version_info[0] < 3:
            self.assertIsInstance(api_encode('foo'), str)
            self.assertIsInstance(api_encode(u'foo'), str)
            self.assertIsInstance(api_decode('foo'), unicode)
        else:
            self.assertIsInstance(api_encode('foo'), bytes)
            self.assertIsInstance(api_encode(b'foo'), bytes)
            self.assertIsInstance(api_decode(b'foo'), str)


    @patch('time.gmtime', return_value=(2000,1,1,1,1,1,1,1,0))
    def test_signature(self, time_mock):
        """ Signature generation for Authorization header """
        params = {
            'client_id': 'foo',
            'client_secret': 'bar',
            'param1': 'this is a string',
            'param2': 10,
            'param3': "one=1\ntwo=2,three=3"
        }
        expected_signature = 'Signature foo:G3N5RxCVc0d6rDLmBRGvcg2hCVY='

        signature = generate_signature('/entity', params)[0]['Authorization']
        self.assertEqual(signature, expected_signature)


    def test_url_transform(self):
        """ HTTP protocol is automatically added to domain """
        api = Api("foo.janrain.com")
        self.assertEqual(api.api_url, "https://foo.janrain.com")


    def test_user_agent(self):
        """ Custom User Agent header can be specified """
        api1 = Api("foo.janrain.com")
        self.assertIsNotNone(api1.user_agent)

        api2 = Api("foo.janrain.com", user_agent="foobar")
        self.assertEqual(api2.user_agent, "foobar")

    def test_timeounts(self):
        """ Connection, read, and API timeouts """
        defaults = {'client_id': 'foo', 'client_secret': 'bar'}
        domain = 'foo.janrain.com'

        # defaults are 10 seconds for both connect and read
        with patch.object(Session, 'post') as mock_post:
            mock_post.return_value.status_code.return_value = 200
            mock_post.return_value.json.return_value = {"stat": "ok"}
            api = Api(domain, defaults=defaults)
            api.call('/entity')
            self.assertEqual(mock_post.call_args[1]['timeout'], (10,10))

        with patch.object(Session, 'post') as mock_post:
            mock_post.return_value.status_code.return_value = 200
            mock_post.return_value.json.return_value = {"stat": "ok"}
            api = Api(domain, defaults=defaults, connect_timeout=15)
            api.call('/entity', timeout=30)
            self.assertEqual(mock_post.call_args[1]['timeout'], (15,30))
