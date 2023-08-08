




from django.urls import path
from .views import *

urlpatterns = [
    path("upload/",documentUpload),
    path('download/<int:document_id>/', documentDownload),
    path('documentlist/',documentList),
    path('update/<int:document_id>/',documentUpdate),
    path('delete/<int:document_id>/',documentDelete),
    path('search/',searchDocument),

    path('<int:document_id>/sharewith/',documentShare),
]