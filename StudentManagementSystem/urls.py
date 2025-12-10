
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from students.jwt_views import CustomTokenObtainPairView, get_user_profile, register_student_jwt, register_teacher_jwt
from templates.template_views import (
    home_view, login_view, logout_view,
    register_student_view, register_teacher_view,
    courses_list_view, course_detail_view,
    request_enrollment_view, student_dashboard_view,
    teacher_dashboard_view, approve_request_view,
    reject_request_view, teacher_course_students_view,
    update_grade_view, students_list_view,
    student_detail_view, teachers_list_view,
    direct_enroll_view, update_deadline_view, manage_course_view
)
from activity_views import (
    get_activity_logs, get_activity_stats,
    get_my_activity_logs, activity_logs_view
)

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # JWT Token endpoints (API)
    path('api/auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/profile/', get_user_profile, name='user_profile'),
    path('api/auth/register/student/', register_student_jwt, name='api_register_student'),
    path('api/auth/register/teacher/', register_teacher_jwt, name='api_register_teacher'),

    # Template-based views
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register-student/', register_student_view, name='register_student'),
    path('register-teacher/', register_teacher_view, name='register_teacher'),
    path('courses-list/', courses_list_view, name='courses_list'),
    path('course-detail/<int:course_id>/', course_detail_view, name='course_detail'),
    path('request-enrollment/<int:course_id>/', request_enrollment_view, name='request_enrollment'),
    path('student-dashboard/', student_dashboard_view, name='student_dashboard'),
    path('teacher-dashboard/', teacher_dashboard_view, name='teacher_dashboard'),
    path('approve-request/<int:request_id>/', approve_request_view, name='approve_request'),
    path('reject-request/<int:request_id>/', reject_request_view, name='reject_request'),
    path('teacher-course-students/<int:course_id>/', teacher_course_students_view, name='teacher_course_students'),
    path('update-grade/<int:enrollment_id>/', update_grade_view, name='update_grade'),
    path('students-list/', students_list_view, name='students_list'),
    path('student-detail/<int:student_id>/', student_detail_view, name='student_detail'),
    path('teachers-list/', teachers_list_view, name='teachers_list'),
    path('manage-course/<int:course_id>/', manage_course_view, name='manage_course'),
    path('direct-enroll/<int:course_id>/', direct_enroll_view, name='direct_enroll'),
    path('update-deadline/<int:course_id>/', update_deadline_view, name='update_deadline'),

    # Activity Logs (Template view)
    path('activity-logs/', activity_logs_view, name='activity_logs'),

    # Activity Logs API endpoints
    path('api/activity-logs/', get_activity_logs, name='api_activity_logs'),
    path('api/activity-logs/stats/', get_activity_stats, name='api_activity_stats'),
    path('api/activity-logs/my-logs/', get_my_activity_logs, name='api_my_activity_logs'),

    # API URLs
    path('api/students/', include('students.urls')),
    path('api/teachers/', include('teachers.urls')),
    path('api/courses/', include('courses.urls')),
]
