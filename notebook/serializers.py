from rest_framework import serializers
from notebook.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = ['id', 'title', 'slug', 'owner', 'content',
                  'created_at', 'due_date', 'priority', 'status', 'category']
