from datetime import datetime
from django.shortcuts import render
from core.models import User
from notebook.models import Note
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q


def generate_user_notes(user_email):
    '''
    This function generates a list of all notes for a given user email address
    :param user_email: The email address of the user
    :return: A tuple of list of note objects associated with the specified user
    as well as basic user information
    '''
    user = User.objects.get(email=user_email)
    notes = Note.objects.select_related('owner').filter(
        owner__user_id=user.id).all().order_by('id')
    note_list = notes[0:]

    refined_notes = [note.get_display_info()
                     for note in notes]

    data = {
        "user": f"{user.first_name.title()} {user.last_name.title()}",
        "created_date": datetime.utcnow(),
        "notes": refined_notes,
        "last_login": user.last_login
    }

    return (data, note_list)


def show_uploader(request):
    '''
    Display html template for testing email delivery with attachment
    '''
    context = {}
    return render(request, 'file_upload.html', context)


def redirect_noexist(request):
    """
    This function based view displays a 404-error page to anyone trying to 
    access a non-configured URL.
    """

    context = {'detail': 'page not found.'}
    return render(request, '404.html', context)


def order_notes(value: str, user_id: int):
    """
    Function that orders notes based on: 
    * due date, 
    * priority 
    * created date
    """
    try:
        return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().order_by(value)
    except Exception as e:
        return Response({'detail': e.args[0:]}, status=status.HTTP_404_NOT_FOUND)


def categorize_notes(value: str, user_id: int):
    """
    Function that groups notes into one of the following categories:
    * None
    * Blue
    * Green
    * Orange
    * Purple
    * Red
    * Yellow
    """
    return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().filter(category=value[0])


def filter_by_status(value: str, user_id: int):
    """
    Function that filters notes based on the following status:
    'Unfinished': Tasks yet to be completed.
    'Overdue': All tasks (completed or not) whose due dates are more than the current date.
    'Done': Tasks that have been completed
    """

    try:
        notes_queryset = Note.objects.select_related(
            'owner').filter(owner__user_id=user_id).all()

        if value.title() == 'Unfinished':
            return notes_queryset.filter(Q(status='N') | Q(status='P'))
        elif value.title() == 'Overdue':
            return notes_queryset.filter(due_date__lte=datetime.utcnow())
        elif value.title() == 'Done':
            return notes_queryset.filter(status='C')
    except Exception as e:
        return Response({'detail': e.args[0:]}, status=status.HTTP_404_NOT_FOUND)
