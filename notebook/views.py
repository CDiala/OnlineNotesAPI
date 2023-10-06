from django.shortcuts import get_object_or_404, get_list_or_404
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Note, Owner
from .serializers import NoteSerializer

# Create your views here.


@api_view(['GET', 'POST'])
def notes_list(request):
    if request.method == 'GET':
        notes_queryset = Note.objects.select_related('owner').all()
        # if hyperlink for owners/id doesn't work, add context={'request': request} after many=True
        serializer = NoteSerializer(notes_queryset, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def note_details(request, note_id):
    note = get_object_or_404(Note, pk=note_id)
    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'DELETE':
        # # Allow this conditional check for records with on_delete=models.PROTECT
        # if note.owner_item.count > 0:
        #     return Response({'error': "Cannot delete record with an associated owner."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
