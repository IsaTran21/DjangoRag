from django.urls import path
from . import views

urlpatterns = [
    path('bot', views.getData),
    path('files', views.upload_files),
]
