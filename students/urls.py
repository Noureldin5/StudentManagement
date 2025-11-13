from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from . import views

urlpatterns = [
    path('students/', views.get_students, name='get_students'),
    path('students/add/', views.add_student, name='add_student'),
]