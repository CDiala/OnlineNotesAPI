from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.views import View
from django.core.mail import EmailMessage
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions

from OnlineNotesAPI import renderers

from core import authentication
from core.models import User
from .models import Note, Owner
from .serializers import NoteSerializer
from datetime import datetime
import csv

# Create your views here.


class NoteList(APIView):
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        '''
        Get all notes created by the authenticated user.
        '''
        try:
            requester = request.user

            user = User.objects.get(email=requester)

            notes_queryset = Note.objects.select_related(
                'owner').filter(owner__user_id=user.id).all()

            note_status = request.query_params.get('status')

            query_param_keys = list(dict.keys(request.query_params))

            query_param_keys = [key.lower() for key in query_param_keys]

            if 'status' in query_param_keys:
                note_status = request.query_params.get('status')
                notes_queryset = filter_by_status(note_status, user.id)
            elif 'ordering' in query_param_keys:
                note_status = request.query_params.get('ordering')
                print('ordering', note_status)
                notes_queryset = order_notes(note_status, user.id)

            serializer = NoteSerializer(notes_queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0:]}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        '''
        Create a new note with title, slug and content provided as part of POST data.
        The method validates that the requester is a registered member, after
        which the note is saved. If user's email isn't validated, this endpoint creates 
        the user as the owner of the note and sets email valid to False.
        '''
        try:
            raw_user_data = request.user

            if raw_user_data:
                user = get_object_or_404(User, email=raw_user_data)

                new_note_owner = Owner.objects.select_related('user').filter(
                    user_id=user.id).first()

                # if new_note_owner is None, insert into owner table before creating note
                with transaction.atomic():
                    if new_note_owner is None:
                        new_note_owner = Owner()
                        new_note_owner.is_email_valid = False
                        new_note_owner.user = user
                        new_note_owner.save()

                    new_request_data = {**request.data,
                                        'owner': new_note_owner.id}

                    # save new note
                    serializer = NoteSerializer(
                        data=new_request_data)
                    serializer.is_valid(raise_exception=True)

                    validated_data = serializer.validated_data

                    new_note = Note(**validated_data)

                    new_note.save()

                return Response({"response": "record created successfully.", "data": serializer.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(data={'detail': e.args[0:]}, status=status.HTTP_400_BAD_REQUEST)


class NoteDetail(APIView):
    """
    This class is used to retrieve, update or delete a note based on ID.
    """

    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, note_id):
        """
        This method retrieves a specific note using the provided id and 
        returns it in json format if found else raises 404 error code. 
        Only notes created by the logged in user are returned.
        """
        try:
            requester = request.user
            user = User.objects.get(email=requester)

            notes_queryset = Note.objects.select_related(
                'owner').filter(owner__user_id=user.id).all()

            note = get_object_or_404(notes_queryset, pk=note_id)
            serializer = NoteSerializer(note)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': e.args[0:]}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, note_id):
        """
        This method updates a note using the specific note details of the given id 
        and returns it in json format if found else raises 404 error code.
        """
        requester = request.user
        user = User.objects.get(email=requester)

        notes_queryset = Note.objects.select_related(
            'owner').filter(owner__user_id=user.id).all()

        note = get_object_or_404(notes_queryset, pk=note_id)
        serializer = NoteSerializer(note, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, note_id):
        """
        This method deletes a particular note from database by its unique
        identifier i.e., Note Id provided as parameter. If not present then
        raises HTTP Not Found Error with appropriate message.
        """
        requester = request.user
        user = User.objects.get(email=requester)

        notes_queryset = Note.objects.select_related(
            'owner').filter(owner__user_id=user.id).all()

        note = get_object_or_404(notes_queryset, pk=note_id)
        note.delete()
        return Response({'response': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


def filter_by_status(value: str, user_id: int):
    if value.title() == 'Unfinished':
        return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().filter(Q(status='N') | Q(status='P'))
    elif value.title() == 'Overdue':
        return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().filter(due_date__lte=datetime.utcnow())
    elif value.title() == 'Done':
        return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().filter(status='C')


def order_notes(value: str, user_id: int):
    return Note.objects.select_related('owner').filter(owner__user_id=user_id).all().order_by(value) or []


''' FIX THIS HARDCODED DATA ASAP '''


def generate_user_notes():

    notes = Note.objects.select_related('owner').all().order_by('id')
    note_list = notes[0:]

    data = {
        "user": "Chibuzo Diala",
        "notes": note_list
    }

    return (data, note_list)

# Opens up page as PDF


class ViewPDF(View):
    def get(self, request, *args, **kwargs):

        pdf = renderers.render_to_pdf(
            'app/pdf_template.html', generate_user_notes()[0])
        return HttpResponse(pdf, content_type='application/pdf')


# Automaticly downloads to PDF file
class DownloadPDF(View):
    def get(self, request, *args, **kwargs):

        pdf = renderers.render_to_pdf(
            'app/pdf_template.html', generate_user_notes()[0])

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Note_%s.pdf" % ("12341231")
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response


def index(request):
    context = {}
    return render(request, 'app/index.html', context)


'''
Utility code to export note list to csv
'''


def downloadCSV(request):
    notes = generate_user_notes()[1]

    print('csv data', notes)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="notes.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'title', 'slug', 'owner', 'content', 'created_at',
                    'due_date', 'priority', 'status', 'category'])

    for note in notes:
        writer.writerow([note.id, note.title, note.slug, note.owner, note.content,
                        note.created_at, note.due_date, note.priority, note.status, note.category])

    return response


@csrf_exempt
def sendEmail(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        print(f"files:", file)

        email = EmailMessage(
            "Hello",
            "Dear user, here is a mail for you. Reply using the available email. Thanks",
            settings.EMAIL_HOST_USER,
            ["dialachibuzo@yahoo.com", "ketu04life@yahoo.com"],
            ["expowengenerator@gmail.com"],
            reply_to=[settings.EMAIL_HOST_USER],
            headers={"Message-ID": "foo"},
        )

        email.attach(
            file.name,
            file.read(),
            file.content_type
        )

        message_response = email.send()

        if message_response == 1:
            return HttpResponse(f'{message_response} mails sent successfully', status=status.HTTP_200_OK)
        else:
            return HttpResponse(f'Failed to deliver email to recipients.')

    return HttpResponse('Method not allowed', status=status.HTTP_403_FORBIDDEN)


def show_uploader(request):
    context = {}
    return render(request, 'file_upload.html', context)


def page_not_found():
    return Response({'detail': 'page not found.'})
