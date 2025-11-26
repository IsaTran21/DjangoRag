from django.urls import path
from . import views
urlpatterns = [

    path('index/', views.index_view, name='index_view'),
    path('demo/', views.demo, name='demo')
]