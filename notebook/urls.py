from django.urls import path
from . import views, services

''' Setup endpoint routes '''
urlpatterns = [
    path("notes/", views.NoteList.as_view(), name="note-list"),
    path("notes/<int:note_id>/", views.NoteDetail.as_view(), name="note-detail"),
    path('pdf_view/', views.ViewPDF.as_view(), name="pdf_view"),
    path('pdf_download/', views.DownloadPDF.as_view(), name="pdf_download"),
    path('csv_download/', views.DownloadCSV.as_view(), name="csv_download"),
    path('send_attachment/', views.SendAttachment.as_view(), name="send_attachment"),
    path('', services.show_uploader, name="show_uploader"),
]
