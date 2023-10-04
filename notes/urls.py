from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.get_notes),
    path("notes/<int:note_id>/", views.get_note_by_id),
]
