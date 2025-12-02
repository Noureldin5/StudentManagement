from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Student, Teacher, Course, Enrollment, EnrollmentRequest
import json

@require_http_methods(["GET"])
def home(request):
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
                'add': '/students/add/ [POST]',
                'update': '/students/update/<id>/ [PUT]',
                'delete': '/students/delete/<id>/ [DELETE]'
            },
            'courses': {
                'list': '/courses/ [GET]'
            },
            'enrollment': {
                'request': '/enrollment/request/ [POST]'
            },
            'teacher': {
                'pending_requests': '/teacher/requests/<teacher_id>/ [GET]',
                'approve_request': '/teacher/request/<request_id>/approve/ [POST]',
                'reject_request': '/teacher/request/<request_id>/reject/ [POST]',
                'enroll_student': '/teacher/enroll/ [POST]',
                'course_students': '/teacher/<teacher_id>/course/<course_id>/students/ [GET]',
                'update_grade': '/teacher/enrollment/<enrollment_id>/grade/ [PUT]'
            }
        },
        'admin_panel': '/admin/'
    })

@csrf_exempt
@require_http_methods(["POST"])
def register_student(request):
    data = json.loads(request.body)

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
        'user_id': user.id
    }, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def register_teacher(request):
    data = json.loads(request.body)

    user = User.objects.create_user(
        username=data.get('username'),
        email=data.get('email'),
        password=data.get('password')
    )
    user.is_staff = True
    user.save()

    teacher = Teacher.objects.create(
        user=user,
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        subject=data.get('subject')
    )

    return JsonResponse({
        'message': 'Teacher registered successfully',
        'teacher_id': teacher.id,
        'user_id': user.id
    }, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def user_login(request):
    data = json.loads(request.body)
    user = authenticate(
        request,
        username=data.get('username'),
        password=data.get('password')
    )

    if user is not None:
        login(request, user)
        user_type = 'teacher' if hasattr(user, 'teacher_profile') else 'student'
        return JsonResponse({
            'message': 'Login successful',
            'user_type': user_type,
            'user_id': user.id
        })
    else:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

@require_http_methods(["POST"])
def user_logout(request):
    logout(request)
    return JsonResponse({'message': 'Logout successful'})

@require_http_methods(["GET"])
def get_students(request):
    students = Student.objects.all().values(
        'id', 'first_name', 'last_name', 'age', 'gpa',
        'user__username', 'user__email', 'created_at'
    )
    return JsonResponse(list(students), safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def add_student(request):
    data = json.loads(request.body)
    student = Student.objects.create(
        first_name=data.get('first_name'),
        last_name=data.get('last_name'),
        age=data.get('age'),
        gpa=data.get('gpa')
    )
    student.save()
    return HttpResponse("Student added successfully")

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return HttpResponse("Student deleted successfully")

@csrf_exempt
@require_http_methods(["PUT"])
def update_student(request, id):
    student = Student.objects.get(id=id)
    data = json.loads(request.body)
    student.first_name = data.get('first_name')
    student.last_name = data.get('last_name')
    student.age = data.get('age')
    student.gpa = data.get('gpa')
    student.save()
    return HttpResponse("Student updated successfully")

@require_http_methods(["GET"])
def get_courses(request):
    courses = Course.objects.all().values()
    return JsonResponse(list(courses), safe=False)

@csrf_exempt
@require_http_methods(["POST"])
def student_request_enrollment(request):
    data = json.loads(request.body)

    student = get_object_or_404(Student, id=data.get('student_id'))
    course = get_object_or_404(Course, id=data.get('course_id'))

    enrollment_request, created = EnrollmentRequest.objects.get_or_create(
        student=student,
        course=course,
        defaults={'notes': data.get('notes', '')}
    )

    if not created:
        return JsonResponse({'error': 'Request already exists'}, status=400)

    return JsonResponse({
        'message': 'Enrollment request submitted',
        'request_id': enrollment_request.id
    }, status=201)

@csrf_exempt
@require_http_methods(["POST"])
def teacher_approve_request(request, request_id):
    data = json.loads(request.body)

    teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
    enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

    if enrollment_request.course not in teacher.courses.all():
        return JsonResponse({'error': 'Teacher does not teach this course'}, status=403)

    enrollment_request.status = 'approved'
    enrollment_request.reviewed_by = teacher
    enrollment_request.reviewed_at = timezone.now()
    enrollment_request.save()

    Enrollment.objects.create(
        student=enrollment_request.student,
        course=enrollment_request.course,
        enrolled_by=teacher
    )

    return JsonResponse({'message': 'Request approved and student enrolled'})

@csrf_exempt
@require_http_methods(["POST"])
def teacher_reject_request(request, request_id):
    data = json.loads(request.body)

    teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
    enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

    if enrollment_request.course not in teacher.courses.all():
        return JsonResponse({'error': 'Teacher does not teach this course'}, status=403)

    enrollment_request.status = 'rejected'
    enrollment_request.reviewed_by = teacher
    enrollment_request.reviewed_at = timezone.now()
    enrollment_request.notes = data.get('notes', enrollment_request.notes)
    enrollment_request.save()

    return JsonResponse({'message': 'Request rejected'})

@csrf_exempt
@require_http_methods(["POST"])
def teacher_enroll_student(request):
    data = json.loads(request.body)

    teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
    student = get_object_or_404(Student, id=data.get('student_id'))
    course = get_object_or_404(Course, id=data.get('course_id'))

    if course not in teacher.courses.all():
        return JsonResponse({'error': 'Teacher does not teach this course'}, status=403)

    enrollment, created = Enrollment.objects.get_or_create(
        student=student,
        course=course,
        defaults={'enrolled_by': teacher}
    )

    if not created:
        return JsonResponse({'error': 'Student already enrolled'}, status=400)

    return JsonResponse({
        'message': 'Student enrolled successfully',
        'enrollment_id': enrollment.id
    }, status=201)

@require_http_methods(["GET"])
def teacher_pending_requests(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    pending_requests = EnrollmentRequest.objects.filter(
        course__in=teacher.courses.all(),
        status='pending'
    ).select_related('student', 'course').values(
        'id', 'student__first_name', 'student__last_name',
        'course__name', 'course__code', 'requested_at', 'notes'
    )

    return JsonResponse(list(pending_requests), safe=False)

@require_http_methods(["GET"])
def teacher_course_students(request, teacher_id, course_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    course = get_object_or_404(Course, id=course_id)

    if course not in teacher.courses.all():
        return JsonResponse({'error': 'Teacher does not teach this course'}, status=403)

    enrollments = Enrollment.objects.filter(course=course).select_related('student').values(
        'id', 'student__id', 'student__first_name', 'student__last_name',
        'student__gpa', 'enrollment_date', 'grade'
    )

    return JsonResponse(list(enrollments), safe=False)

@csrf_exempt
@require_http_methods(["PUT"])
def teacher_update_grade(request, enrollment_id):
    data = json.loads(request.body)

    teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if enrollment.course not in teacher.courses.all():
        return JsonResponse({'error': 'Teacher does not teach this course'}, status=403)

    enrollment.grade = data.get('grade')
    enrollment.save()

    return JsonResponse({'message': 'Grade updated successfully'})




