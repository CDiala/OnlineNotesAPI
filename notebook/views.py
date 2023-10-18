from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, permissions
from OnlineNotesAPI import renderers
from core import authentication, services
from core.models import User
from notebook.services import categorize_notes, filter_by_status, generate_user_notes, order_notes
from .models import Note, Owner
from .serializers import NoteSerializer
from datetime import datetime
import csv


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
                notes_queryset = order_notes(note_status, user.id)
            elif 'category' in query_param_keys:
                note_status = request.query_params.get('category')
                notes_queryset = categorize_notes(note_status, user.id)

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


class ViewPDF(APIView):
    '''
    API view to render PDF file from HTML template and send it in response
    '''
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        try:
            pdf = renderers.render_to_pdf(
                'app/pdf_template.html', generate_user_notes(request.user)[0])
            return HttpResponse(pdf, content_type='application/pdf')
        except Exception as e:
            return Response({'detail': e.args[0:]})


# Automatically downloads to PDF file
class DownloadPDF(APIView):
    '''
    This class downloads notes list as PDF.
    '''
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):

        pdf = renderers.render_to_pdf(
            'app/pdf_template.html', generate_user_notes(request.user)[0])

        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Notes List_%s.pdf" % (
            datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S"))
        content = "attachment; filename=%s" % (filename)
        response['Content-Disposition'] = content
        return response


class DownloadCSV(APIView):
    '''
    This class downloads notes list as PDF.
    '''
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    def get(self, request):
        '''
        Utility code that builds a list of user's notes into a CSV and downloads the file to their machine.
        '''

        notes = generate_user_notes(request.user)[1]

        note_list = notes[0:]

        note_fields = [
            field.name for field in note_list.first()._meta.get_fields()]

        note_values = [
            [value for key, value in note.items() if key != 'id'] for note in note_list.values()]

        current_timestamp = datetime.strftime(
            datetime.now(), "%Y-%m-%d %H:%M:%S")

        response = HttpResponse(content_type='text/csv')
        response[
            'Content-Disposition'] = f'attachment; filename={"Notes list_%s.csv" % (current_timestamp)}'

        writer = csv.writer(response)
        writer.writerow(note_fields)

        for index, note in enumerate(note_values):
            writer.writerow([index + 1, *note])

        return response


class SendAttachment(APIView):
    '''
    This class downloads notes list as PDF.
    '''
    authentication_classes = (authentication.CustomUserAuthentication, )
    permission_classes = (permissions.IsAuthenticated, )

    @csrf_exempt
    def post(self, request):
        '''
        Send email with attachment to logged in user. 
        File attachment is required.
        '''
        try:

            requester = request.user
            file = request.FILES.get('file')

            user = get_object_or_404(User, email=requester)

            email_subject = "Online Note Manager - Notes Summary"

            email_body = f'''
Hi {user.first_name.title()} {user.last_name.title()},

The attached document contains all notes you have saved on our platform.

Look out for the high-priority notes and close them out as soon as possible.

Don't forget to update their status as things change.

Stay safe!

Best regards,
The Team
            '''

            data = {
                "email_body": email_body,
                "email_subject": email_subject,
                "email_address": user.email,
                "file": file
            }

            message_response = services.Util.send_verifyEmail(data)

            if message_response == 1:
                return Response({'detail': '1 mail sent successfully'}, status=status.HTTP_200_OK)

            return Response({'detail': 'Failed to deliver email to recipients.'})
        except Exception as e:
            return Response({'detail': e.args[0:]}, status=status.HTTP_400_BAD_REQUEST)
