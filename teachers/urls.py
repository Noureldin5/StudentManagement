"""
Teacher app URL configuration
"""
from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # Teacher management endpoints
    path('', views.teacher_list, name='teacher_list'),
    path('<int:teacher_id>/', views.teacher_detail, name='teacher_detail'),
    path('<int:teacher_id>/courses/', views.my_courses, name='my_courses'),
    
    # Enrollment request management
    path('<int:teacher_id>/requests/', views.pending_requests, name='pending_requests'),
    path('request/<int:request_id>/approve/', views.approve_request, name='approve_request'),
    path('request/<int:request_id>/reject/', views.reject_request, name='reject_request'),
    
    # Direct enrollment
    path('enroll/', views.direct_enroll, name='direct_enroll'),
    
    # Course management
    path('<int:teacher_id>/courses/<int:course_id>/students/', views.course_students, name='course_students'),
    
    # Grade management
    path('enrollment/<int:enrollment_id>/grade/', views.update_grade, name='update_grade'),
]
