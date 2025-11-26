from django.urls import path
from . import views

urlpatterns = [
    path('files', views.upload_files),
    path('bot', views.getData),
]
