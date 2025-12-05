"""
Authentication views for student and teacher registration/login
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from students.models import Student
from teachers.models import Teacher
import json


@require_http_methods(["GET"])
def home(request):
    """API home page with all available endpoints"""
    return JsonResponse({
        'message': 'Welcome to Student Management System API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register_student': '/auth/register/student/ [POST]',
                'register_teacher': '/auth/register/teacher/ [POST]',
                'login': '/auth/login/ [POST]',
                'logout': '/auth/logout/ [POST]',
                'get_token': '/auth/token/ [POST]',
                'refresh_token': '/auth/token/refresh/ [POST]'
            },
            'students': {
                'list': '/students/ [GET]',
                'detail': '/students/<id>/ [GET]',
                'add': '/students/add/ [POST]',
                'update': '/students/<id>/update/ [PUT]',
                'delete': '/students/<id>/delete/ [DELETE]'
            },
            'courses': {
                'list': '/courses/ [GET]',
                'detail': '/courses/<id>/ [GET]'
            },
            'enrollment': {
                'request': '/enrollment/request/ [POST]',
                'my_courses': '/enrollment/my-courses/ [GET]'
            },
            'teachers': {
                'list': '/teachers/ [GET]',
                'pending_requests': '/teachers/<teacher_id>/requests/ [GET]',
                'approve_request': '/teachers/request/<request_id>/approve/ [POST]',
                'reject_request': '/teachers/request/<request_id>/reject/ [POST]',
                'enroll_student': '/teachers/enroll/ [POST]',
                'course_students': '/teachers/<teacher_id>/courses/<course_id>/students/ [GET]',
                'update_grade': '/teachers/enrollment/<enrollment_id>/grade/ [PUT]'
            }
        },
        'admin_panel': '/admin/'
    })


@csrf_exempt
@require_http_methods(["POST"])
def register_student(request):
    try:
        data = json.loads(request.body)

        # Create User
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password')
        )

        student = Student.objects.create(
            user=user,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gpa=data.get('gpa', 0.0)
        )

        return JsonResponse({
            'message': 'Student registered successfully',
            'student_id': student.id,
            'user_id': user.id,
            'username': user.username
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def register_teacher(request):
    try:
        data = json.loads(request.body)

        # Create User with staff privileges
        user = User.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password')
        )
        user.is_staff = True
        user.save()

        # Create Teacher profile
        teacher = Teacher.objects.create(
            user=user,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            subject=data.get('subject')
        )

        return JsonResponse({
            'message': 'Teacher registered successfully',
            'teacher_id': teacher.id,
            'user_id': user.id,
            'username': user.username
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    try:
        data = json.loads(request.body)
        user = authenticate(
            request,
            username=data.get('username'),
            password=data.get('password')
        )

        if user is not None:
            login(request, user)

            user_type = None
            profile_id = None

            if hasattr(user, 'teacher_profile'):
                user_type = 'teacher'
                profile_id = user.teacher_profile.id
            elif hasattr(user, 'student_profile'):
                user_type = 'student'
                profile_id = user.student_profile.id

            return JsonResponse({
                'message': 'Login successful',
                'user_type': user_type,
                'user_id': user.id,
                'profile_id': profile_id,
                'username': user.get_username()
            })
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

