from unittest.mock import patch, Mock

import requests
from django.core.exceptions import PermissionDenied
from django.test import SimpleTestCase
from requests import request
from utils.custom_requests import CustomSession

class TestCustom(SimpleTestCase):
    def setUp(self):
        self.custom_session = CustomSession()

    @patch.object(requests.Session, 'request')
    def test_custom_request_503(self, mock_request):
        # Create a mocked response for a 503 scenario
        mocked_response = Mock(status_code=503)
        mock_request.return_value = mocked_response

        # Call custom_request, PermissionDenied should be raised
        with self.assertRaises(PermissionDenied):
            self.custom_session.custom_request('GET', 'http://example.com')

    @patch.object(requests.Session, 'request')
    def test_custom_request_non_503(self, mock_request):
        # Create a mocked response for a non-503 scenario
        mocked_response = Mock(status_code=200)
        mock_request.return_value = mocked_response

        # Call custom_request, no exception should be raised
        try:
            self.custom_session.custom_request('GET', 'http://example.com')
        except PermissionDenied:
            self.fail("PermissionDenied should not be raised for non-503 response")
