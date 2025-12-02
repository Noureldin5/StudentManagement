from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/student/', views.register_student, name='register_student'),
    path('auth/register/teacher/', views.register_teacher, name='register_teacher'),
    path('auth/login/', views.user_login, name='user_login'),
    path('auth/logout/', views.user_logout, name='user_logout'),

    path('students/', views.get_students, name='get_students'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/delete/<int:id>/', views.delete_student, name='delete_student'),
    path('students/update/<int:id>/', views.update_student, name='update_student'),

    path('courses/', views.get_courses, name='get_courses'),

    path('enrollment/request/', views.student_request_enrollment, name='student_request_enrollment'),

    path('teacher/requests/<int:teacher_id>/', views.teacher_pending_requests, name='teacher_pending_requests'),
    path('teacher/request/<int:request_id>/approve/', views.teacher_approve_request, name='teacher_approve_request'),
    path('teacher/request/<int:request_id>/reject/', views.teacher_reject_request, name='teacher_reject_request'),
    path('teacher/enroll/', views.teacher_enroll_student, name='teacher_enroll_student'),
    path('teacher/<int:teacher_id>/course/<int:course_id>/students/', views.teacher_course_students, name='teacher_course_students'),
    path('teacher/enrollment/<int:enrollment_id>/grade/', views.teacher_update_grade, name='teacher_update_grade'),
]