from django.shortcuts import render
from django.http import HttpResponse
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password

from .models import User, Note
import json

# Create your views here.

notes: list(Note.objects.all()) = [
    {
        "user": "d.c@yahoo.com",
        "title": "Get a drink",
        "content": "Buy coke from the store",
        "slug": "coke-from-store",
        "created_at": "2023-09-30",
        "updated_at": "",
        "due_date": "2023-09-30",
        "priority": "M",
        "status": "P",
        "category": "N"
    },
    {
        "user": "a.b@yahoo.com",
        "title": "Get pizza",
        "content": "Buy coke along with it",
        "slug": "pizza-plus-coke",
        "created_at": "2023-09-29",
        "updated_at": "",
        "due_date": "2023-09-29",
        "priority": "M",
        "status": "P",
        "category": "G"
    },
]


def get_notes(request):

    notes_query_set = Note.objects.all()

    print(request)

    return render(request, 'hello.html', {'title': 'hello world', 'greeter': 'buzz'})


def get_note_by_id(request, note_id):
    # try:

    # note = Note.objects.get(pk=1)

    # Update existing user
    user = User.objects.filter(pk=1).first()  # use user = User for new user
    user.first_name = 'Jon'
    user.last_name = 'Bellion'
    validate_email(user.email)
    user.email = 'jb@yahoo.com'
    user.password = make_password('user123')
    user.is_email_valid = True
    user.save()

    resp = HttpResponse()
    resp.status_code = 200
    resp.content = user
    print('note by id:', resp.content)

    # resp = HttpResponse()
    # resp.status_code = 200
    # resp.content = {json.dumps(
    #     notes[note_id]), resp.status_code}
    # print('note by id:', resp)

    return resp

    # except TypeError as exType:
    #     return render(request, 'page_not_found.html', {'error': 'unexpected keyword argument'})

    # except IndexError as exIndex:
    #     return render(request, 'page_not_found.html', {'error': 'provided index not found'})
