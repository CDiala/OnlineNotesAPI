from django.test import Client
from rest_framework import status
import unittest
from unittest.mock import patch
from dotenv import load_dotenv
import json
import os
import random

# Load variables from .env file
load_dotenv()

# Generate random test email:
random_id = int(random.random() * random.randint(0, 10000))
email = str.join('', ['kerry.hilson', str(random_id), '@example.com'])


class TestViews(unittest.TestCase):
    def setUp(self):
        self.client = Client()
        self.email_host = os.getenv('SMTP_HOST')
        self.email_port = int(os.getenv('SMTP_PORT', 587))

    @patch('rest_framework_simplejwt.tokens.RefreshToken.for_user')
    def test_laregister_api(self, mock_refresh_token):
        # Mocking the RefreshToken response
        mock_refresh_token.return_value.access_token = 'test_token'

        response = self.client.post(
            '/api/v1/register/',
            {
                "first_name": "Kerry",
                "last_name": "Hilson",
                "email": email,
                "password": "testpassword123"
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email', json.loads(response.content))

    # def test_verify_email(self):
    #     # Generate a valid test token
    #     refresh_token = RefreshToken.for_user(self)
    #     valid_test_token = str(refresh_token.access_token)

    #     # Make a GET request with the valid test token
    #     response = self.client.get(
    #         f'/api/v1/verify-email/?token={valid_test_token}'
    #     )
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_api(self):
        # resp = response.Response()
        response = self.client.post(
            '/api/v1/login/',
            {
                "email": email,
                "password": "testpassword123"
            },
            content_type='application/json'
        )

        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', json_response)

    def test_logjuser_api(self):
        # Login and authenticate user
        self.test_login_api()

        response = self.client.get('/api/v1/me/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_api(self):
        # Login and authenticate user
        self.test_login_api()

        response = self.client.post('/api/v1/logout/')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_password(self):
        response = self.client.patch(
            '/api/v1/update-password/',
            {
                "email": email,
                "password": "newtestpassword123"
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('django.core.mail.EmailMessage.send')
    def test_reset_password(self, mock_send_email):
        mock_send_email.return_value = 1

        response = self.client.post(
            '/api/v1/reset-password/',
            {
                "email": email
            },
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)


if __name__ == '__main__':
    unittest.main()
