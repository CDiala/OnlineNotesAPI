from django.urls import path
from . import views

urlpatterns = [
    path("notes/", views.NoteList.as_view()),
    path("notes/<int:note_id>/", views.NoteDetail.as_view()),
    path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
    path('csv_download/', views.DownloadCSV, name="pdf_download"),
    # if this crashes when data is available, change owner_id to pk and reflect same change in view
]
