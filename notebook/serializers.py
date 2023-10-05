from rest_framework import serializers
from notebook.models import Note, User


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'slug', 'user', 'content',
                  'created_at', 'due_date', 'priority', 'status', 'category']
