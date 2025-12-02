from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Course endpoints
    path('', views.course_list, name='course_list'),
    path('<int:course_id>/', views.course_detail, name='course_detail'),
    path('<int:course_id>/enrollments/', views.course_enrollments, name='course_enrollments'),
]

