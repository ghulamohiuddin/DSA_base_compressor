from django.urls import path
from . import views

urlpatterns = [
    path('', views.compress_file, name='compress'),
    path('decompress/', views.decompress_file, name='decompress'),
    path('success/', views.success, name='success'),
]
