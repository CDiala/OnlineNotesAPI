from django.http import HttpResponse
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.apps import apps
from django.conf import settings
from django.db.models import Q
from django.views import View
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
        print('meta request\n', request.COOKIES.get('jwt'))
        print('request.query_params', request.query_params)

        notes_queryset = Note.objects.select_related(
            'owner').all()
        note_status = request.query_params.get('status')

        query_param_keys = list(dict.keys(request.query_params))
        # print('is there query params?:', query_param_keys)
        query_param_keys = [key.lower() for key in query_param_keys]

        if 'status' in query_param_keys:
            note_status = request.query_params.get('status')
            notes_queryset = filter_by_status(note_status)
        elif 'ordering' in query_param_keys:
            note_status = request.query_params.get('ordering')
            print('ordering', note_status)
            notes_queryset = order_notes(note_status)

        serializer = NoteSerializer(notes_queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # # insert owner_id into owner table, then insert note data into note table
        if 'title' not in request.data or 'content' not in request.data or 'slug' not in request.data or 'owner' not in request.data:
            return Response('Bad request', status=status.HTTP_400_BAD_REQUEST)

        # serializer = NoteSerializer(data=request.data)
        # serializer.is_valid(raise_exception=True)

        # print('raw request', request.data['owner'])
        # serializer.save()
        # return Response(serializer.data, status=status.HTTP_201_CREATED)

        note_owner_id = request.data['owner']
        print('note owner id', note_owner_id)
        # note_owner_id = serializer.validated_data
        note_owner = Owner.objects.filter(pk=note_owner_id).first()
        pk_value = note_owner.user_id if note_owner is not None else note_owner_id

        user = get_object_or_404(apps.get_model(
            settings.AUTH_USER_MODEL).objects.filter(pk=pk_value))

        try:
            # transaction goes here
            # with transaction.atomic():
            # part 1
            owner = Owner()
            owner.is_email_valid = 1
            owner.user = user
            if note_owner is None:
                owner.save()

            # part 2
            # serializer.save()
            note = Note()
            note.title = request.data['title']
            note.content = request.data['content']
            note.slug = request.data['slug'] or '-'
            # note.due_date = request.data['due_date'] or datetime.datetime.utcnow(
            # ) + datetime.timedelta(hours=48)
            note.owner = note_owner or owner
            # note.category = request.data['category'] or 'N'
            # note.status = request.data['status'] or 'N'
            # note.priority = request.data['priority'] or 'M'
            note.save()

            print('note owner', request.data)

            return Response({"response": "record created successfully."}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'info': 'Unable to execute request:'}, status=status.HTTP_400_BAD_REQUEST)


class NoteDetail(APIView):
    """
    This class is used to retrieve, update or delete notes based on ID.
    """

    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, note_id):
        """
        This method retrieves the specific note details of the given id and 
        returns it in json format if found else raises 404 error code.
        """
        note = get_object_or_404(Note, pk=note_id)
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    def put(self, request, note_id):
        """
        This method updates a note using the specific note details of the given id 
        and returns it in json format if found else raises 404 error code.
        """
        note = get_object_or_404(Note, pk=note_id)
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
        note = get_object_or_404(Note, pk=note_id)
        note.delete()
        return Response({'response': 'deleted'}, status=status.HTTP_204_NO_CONTENT)


def filter_by_status(value: str):
    if value.title() == 'Unfinished':
        return Note.objects.select_related('owner').all().filter(Q(status='N') | Q(status='P'))
    elif value.title() == 'Overdue':
        return Note.objects.select_related('owner').all().filter(due_date__lte=datetime.utcnow())
    elif value.title() == 'Done':
        return Note.objects.select_related('owner').all().filter(status='C')


def order_notes(value: str):
    # return Note.objects.select_related('owner').all().order_by(value) or []

    note = get_list_or_404(Note, order_by=value)

    return note

    # return get_list_or_404(
    #     Note.objects.select_related('owner').all().order_by(value))

    # return notes

    # try:
    #     order_by = self.request.GET.get('ordering', None)
    #     order_qs = Note.objects.select_related(
    #         'owner').all().order_by(order_by)
    #     # return order_qs
    # except Exception as e:
    #     return Response(f'no field named {value.replace("-", "")}', status=status.HTTP_400_BAD_REQUEST)

    # {
    #     "title": "welcome back",
    #     "slug": "welcome-back",
    #     "owner": 1,
    #     "content": "..."
    #     "due_date": "2023-10-02",
    #     "priority": "L",
    #     "status": "P",
    #     "category": "B"
    # }


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


def DownloadCSV(request):
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
