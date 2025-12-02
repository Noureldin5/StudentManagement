from django.urls import path
from . import views, auth_views

app_name = 'students'

urlpatterns = [
    # Authentication endpoints
    path('', auth_views.home, name='home'),
    path('auth/register/student/', auth_views.register_student, name='register_student'),
    path('auth/register/teacher/', auth_views.register_teacher, name='register_teacher'),
    path('auth/login/', auth_views.user_login, name='login'),
    path('auth/logout/', auth_views.user_logout, name='logout'),

    # Student CRUD endpoints
    path('students/', views.student_list, name='student_list'),
    path('students/<int:student_id>/', views.student_detail, name='student_detail'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/<int:student_id>/update/', views.update_student, name='update_student'),
    path('students/<int:student_id>/delete/', views.delete_student, name='delete_student'),

    # Enrollment endpoints (student perspective)
    path('enrollment/request/', views.request_enrollment, name='request_enrollment'),
    path('students/<int:student_id>/enrollments/', views.my_enrollments, name='my_enrollments'),
    path('students/<int:student_id>/requests/', views.my_enrollment_requests, name='my_requests'),
]

