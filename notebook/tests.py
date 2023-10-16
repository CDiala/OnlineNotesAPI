import datetime
from django.conf import settings
from django.contrib.auth.models import User
import json
import random
from django.test import TestCase
from unittest.mock import patch
from django.test import Client
from django.urls import reverse
import jwt
from rest_framework import status
from core.models import User
from core.services import generate_token
from .models import Note, Owner


# Global variables
email = 'kerry.hilson@example.com'
password = 'testpassword123'
first_name = 'Kerry'
last_name = 'Hilson'
x = 0


def generate_note_info():
    '''Generate random title and slug fot test note'''
    random_id = int(random.random() * random.randint(0, 10000))
    title = str.join(' ', ['Note', str(random_id)])
    slug = str.join('-', ['Note', str(random_id)]).lower()
    return title, slug


def generate_expired_token(tkn: str, exp_hrs: float = 0, exp_days: float = 0, exp_seconds: float = 0,
                           exp_microseconds: float = 0, exp_milliseconds: float = 0,
                           exp_minutes: float = 0, exp_hours: float = 0,
                           exp_weeks: float = 0) -> str:
    '''
    Receives a valid token, expires it based on the additional parameters passed to it,
    then returns the new expired token.
    '''
    token_data = jwt.decode(tkn, settings.JWT_SECRET,
                            "HS256")

    token_data = {**token_data, "exp": datetime.datetime.utcnow()
                  + datetime.timedelta(
        hours=exp_hours, minutes=exp_minutes, seconds=exp_seconds,
        microseconds=exp_microseconds, days=exp_days, milliseconds=exp_milliseconds, weeks=exp_weeks)
    }

    token = jwt.encode(token_data, settings.JWT_SECRET,
                       algorithm="HS256")

    return token


def loginUser(self):
    '''
    Login the test user using the global variables
    '''
    response = self.client.post(
        '/api/v1/login/',
        {
            "email": email,
            "password": password
        },
        content_type='application/json'
    )

    json_response = json.loads(response.content)
    return json_response['id']


'''
Create Class to test the functionality of reading all notes created by the user
'''


class NoteListTests(TestCase):
    def setUp(self):
        ''' Setup client and test user, and login test user '''
        self.client = Client()

        # Create a user for testing
        self.user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create an owner
        self.owner = Owner.objects.get_or_create(
            is_email_valid=False,
            user_id=self.user.id,
        )

        # Log in the user
        self.client.login(email=email,
                          password=password)

        # Generate a token for the user
        self.token = generate_token(self.user.id)

        # Create headers
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_get_all_notes(self):
        ''' Test to get all notes created by user '''
        log_user = loginUser(self)

        response = self.client.get(
            f'/api/v1/notes/')

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the response contains the expected data (to be customized)
        # self.assertEqual(response.data, expected_data)

    def test_create_note(self):
        ''' Send a POST request to create a new note '''
        note_info = generate_note_info()
        data = {
            'owner': self.user.id,
            'title': note_info[0],
            'slug': note_info[1],
            'content': 'This is a test note.'
        }

        log_user = loginUser(self)

        response = self.client.post(
            reverse('note-list'), data, content_type='application/json')

        # Check if the response status code is 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check if the note was created in the database
        self.assertEqual(Note.objects.select_related('owner').filter(
            owner__user_id=log_user).count(), 1)
        self.assertEqual(Note.objects.get().title, note_info[0])


class NoteaDetailTests(TestCase):

    def setUp(self):
        ''' Create new user, owner and note, token and auth headers for testing '''
        self.user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Create an owner
        self.owner = Owner.objects.get_or_create(
            is_email_valid=False,
            user_id=self.user.id,
        )

        # Create a note associated with the user
        self.note_info = generate_note_info()
        self.note = Note.objects.create(
            owner=self.user.owner,
            title=self.note_info[0],
            slug=self.note_info[1],
            content='This is a test note.'
        )

        # Generate a token for the user
        self.token = generate_token(self.user.id)

        # Create headers
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.token}'}

    def test_get_note_detail_with_valid_token(self):
        ''' Send get request to retrieve a specific note with valid token '''

        response = self.client.get(
            f'/api/v1/notes/{self.note.id}/', **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertEqual(data['title'], self.note_info[0])

    def test_get_note_detail_without_token(self):
        ''' Send get request to retrieve a specific note without token '''
        response = self.client.get(f'/api/v1/notes/{self.note.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_note_detail_with_invalid_token(self):
        ''' Send get request to retrieve a specific note with invalid token '''
        headers = {'HTTP_AUTHORIZATION': 'Bearer invalid_token'}
        response = self.client.get(f'/api/v1/notes/{self.note.id}/', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_note_detail_with_expired_token(self):
        ''' Send get request to retrieve a specific note with expired token '''
        # Convert the valid token to an expired one
        expired_token = generate_expired_token(self.token, exp_hours=-100)
        headers = {'HTTP_AUTHORIZATION': f'Bearer {expired_token}'}
        response = self.client.get(f'/api/v1/notes/{self.note.id}/', **headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_note_details(self):
        ''' Send a PUT request to update the details of the note '''
        data = {
            'owner': self.user.owner.id,
            'title': f'Updated {self.note.title}',
            'slug': f'updated-{self.note.slug}',
            'content': 'This is the updated content.'
        }
        response = self.client.put(
            f'/api/v1/notes/{self.note.id}/', data, content_type='application/json', **self.headers)

        # Check if the response status code is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if the note details were updated in the database
        self.note.refresh_from_db()
        self.assertContains(response, 'Updated', 1)
        self.assertContains(response, 'updated', 2)
