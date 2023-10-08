import django_filters
from .models import Note


class NoteFilter(django_filters.FilterSet):
    class Meta:
        model = Note
        fields = ['due_date', 'priority', 'created_at']


# # Sort all the notes list by due-date, priority, and created-time
#     filter_backends = [DjangoFilterBackend, OrderingFilter]
#     filterset_fields = ['due_date', 'priority', 'created_at']
#     # ordering_fields = ['due_date', 'priority', 'created_at']

#     # queryset = Note.objects.all()
#     # serializer_class = NoteSerializer
#     # filter_backends = (filters.DjangoFilterBackend,)
#     # # filterset_fields = ('due_date', 'priority', 'created_at')
#     # # ordering_fields = ('due_date', 'priority', 'created_at')
#     # filterset_class = NoteFilter
