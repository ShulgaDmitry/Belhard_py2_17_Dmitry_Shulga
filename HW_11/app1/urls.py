from django.urls import path
from .views import *

app_name = "app1"
urlpatterns = [
    path('', index, name='index'),
    path('students/', StudentsView.as_view(), name='students'),
    path('students/<slug:name_slug>/', StudentView.as_view(), name='student'),
]