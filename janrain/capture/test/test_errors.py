import unittest
from requests import Session
from requests.exceptions import HTTPError

try:
    from mock import patch
except ImportError:
    from unittest.mock import patch

from janrain.capture import Api, config
from janrain.capture.exceptions import *


class TestErrors(unittest.TestCase):
    """ Test error handling """
    def test_api_response_errors(self):
        """
        API errors with valid JSON responses raise ApiResponseError
        """
        defaults = {'client_id': 'foo', 'client_secret': 'bar'}
        domain = 'foo.janrain.com'
        api = Api(domain, defaults=defaults)

        with patch.object(Session, 'post') as mock_post:
            mock_post.return_value.status_code.return_value = 200
            mock_post.return_value.json.return_value = {
                "code": 999,
                "error_description": "mock API error",
                "error": "mock_error",
                "stat": "error"
            }
            with self.assertRaises(ApiResponseError) as cm:
                api.call('/entity')

            self.assertEqual(cm.exception.code, 999)
            self.assertEqual(cm.exception.error, "mock_error")


    def test_http_response_errors(self):
        """
        HTTP Errors without valid JSON responses raise HTTPError
        """
        defaults = {'client_id': 'foo', 'client_secret': 'bar'}
        domain = 'foo.janrain.com'
        api = Api(domain, defaults=defaults)

        with patch.object(Session, 'post') as mock_post:
            mock_post.return_value.status_code.return_value = 404
            mock_post.return_value.json.return_value = '404 Not Found'
            mock_post.return_value.raise_for_status.side_effect = HTTPError('Mock HTTP Error')
            with self.assertRaises(HTTPError):
                api.call('/foo')


    def test_oauth_4xx_status(self):
        """ HTTP 400 and 401 responses should not be handled as errors """
        defaults = {'client_id': 'foo', 'client_secret': 'bar'}
        domain = 'foo.janrain.com'
        api = Api(domain, defaults=defaults)

        with patch.object(Session, 'post') as mock_post:
            mock_post.return_value.status_code.return_value = 400
            mock_post.return_value.json.return_value = {"stat": "ok"}
            api.call('/entity')
            mock_post.return_value.status_code.return_value = 400
            api.call('/entity')
