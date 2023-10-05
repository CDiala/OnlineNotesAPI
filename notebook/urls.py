from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.notes_list),
    path("notes/<int:note_id>/", views.note_details),
    # if this crashes when data is available, change owner_id to pk and reflect same change in view
]
