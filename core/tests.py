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

        # print('\n\n\nlogout resp', response.content, '\n\n\n')

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


''' NOT WORKING. TROUBLESHOOT LATER '''


# class TestViews(unittest.TestCase):

#     def setUp(self):
#         self.client = Client()

#         # Create a user for testing
#         response = self.client.post('/api/v1/register/', {
#             'first_name': 'John',
#             'last_name': 'Doe',
#             'email': 'john@example.com',
#             'password': 'testpassword'
#         })

#         self.user = json.loads(response.content)

#     def test_verify_email(self):
#         print('\n\n\n\nself.user', self.user)

#         # Generate a valid test token
#         refresh_token = RefreshToken.for_user(self.user)
#         valid_test_token = str(refresh_token.access_token)

#         # Make a GET request with the valid test token
#         response = self.client.get(
#             f'/api/v1/verify-email/?token={valid_test_token}')

#         self.assertEqual(response.status_code, status.HTTP_200_OK)


''''''
# def test_valid_token_activation(self):
#     # Assuming 'verify-email' is the URL name
#     url = reverse('verify-email')

#     # Make a GET request with a valid token
#     response = self.client.get(f'{url}?token={self.valid_token}')

#     # Check if the response status code is 200 OK
#     self.assertEqual(response.status_code, status.HTTP_200_OK)

#     # Check if the email is activated
#     owner = Owner.objects.get(user=self.user)
#     self.assertTrue(owner.is_email_valid)

# def test_expired_token_activation(self):
#     # Assuming 'verify-email' is the URL name
#     url = reverse('verify-email')

#     # sleep for 3 minutes before proceeding to next line
#     print('\n\n\n\nsleep for 3 minutes to expire valid token')
#     sleep(100)
#     print('\n\n\n\nresume execution with invalid token')

#     # Make a GET request with an expired token
#     response = self.client.get(f'{url}?token={self.valid_token}')

#     # print('\n\n\n\n\nresponse', response.content, '\n\n\n\n\n\n')

#     # Check if the response status code is 400 BAD REQUEST
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     self.assertIn(b'Activation link expired', response.content)

# def test_invalid_token_activation(self):
#     # Assuming 'verify-email' is the URL name
#     url = reverse('verify-email')

#     # Make a GET request with an invalid token
#     response = self.client.get(f'{url}?token={self.invalid_token}')

#     # Check if the response status code is 400 BAD REQUEST
#     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#     self.assertIn(b'Invalid token, request new one.', response.content)


if __name__ == '__main__':
    unittest.main()
