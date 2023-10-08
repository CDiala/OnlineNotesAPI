from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.NoteList.as_view()),
    path("notes/<int:note_id>/", views.NoteDetail.as_view()),
    # if this crashes when data is available, change owner_id to pk and reflect same change in view
]
