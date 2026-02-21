from django.urls import path
from . import views

urlpatterns = [
    path('', views.compress_file, name='compress'),
    path('download/<int:file_id>/', views.download_file, name='download'),
]
