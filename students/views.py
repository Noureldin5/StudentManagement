
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import Student, Enrollment, EnrollmentRequest
from courses.models import Course
import json


@require_http_methods(["GET"])
def student_list(request):
    students = Student.objects.all().values(
        'id', 'first_name', 'last_name', 'age', 'gpa',
        'user__username', 'user__email', 'created_at'
    )
    return JsonResponse(list(students), safe=False)


@require_http_methods(["GET"])
def student_detail(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    data = {
        'id': student.id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'age': student.age,
        'gpa': student.gpa,
        'user': {
            'id': student.user.id,
            'username': student.user.username,
            'email': student.user.email
        },
        'created_at': student.created_at
    }

    return JsonResponse(data)


@csrf_exempt
@require_http_methods(["POST"])
def add_student(request):
    try:
        data = json.loads(request.body)

        student = Student.objects.create(
            user_id=data.get('user_id'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            gpa=data.get('gpa', 0.0)
        )

        return JsonResponse({
            'message': 'Student added successfully',
            'student_id': student.id
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["PUT"])
def update_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        data = json.loads(request.body)

        student.first_name = data.get('first_name', student.first_name)
        student.last_name = data.get('last_name', student.last_name)
        student.age = data.get('age', student.age)
        student.gpa = data.get('gpa', student.gpa)
        student.save()

        return JsonResponse({
            'message': 'Student updated successfully',
            'student': {
                'id': student.id,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'age': student.age,
                'gpa': student.gpa
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        student_name = f"{student.first_name} {student.last_name}"
        student.delete()

        return JsonResponse({
            'message': f'Student {student_name} deleted successfully'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_enrollment(request):
    """
    Request enrollment in a course (requires JWT authentication)
    """
    try:
        data = request.data

        student = get_object_or_404(Student, id=data.get('student_id'))

        # Verify the authenticated user owns this student profile
        if request.user != student.user:
            return Response({'error': 'You can only request enrollment for yourself'},
                          status=status.HTTP_403_FORBIDDEN)

        course = get_object_or_404(Course, id=data.get('course_id'))

        if course.enrollment_deadline and timezone.now() > course.enrollment_deadline:
            return Response({'error': 'Enrollment request deadline has passed'},
                          status=status.HTTP_400_BAD_REQUEST)

        if Enrollment.objects.filter(student=student, course=course).exists():
            return Response({'error': 'Already enrolled in this course'},
                          status=status.HTTP_400_BAD_REQUEST)

        enrollment_request, created = EnrollmentRequest.objects.get_or_create(
            student=student,
            course=course,
            enrollment_deadline= course.enrollment_deadline,
            defaults={'notes': data.get('notes', '')}
        )

        if not created:
            if enrollment_request.status == 'pending':
                return Response({'error': 'Request already pending'},
                              status=status.HTTP_400_BAD_REQUEST)
            elif enrollment_request.status == 'approved':
                return Response({'error': 'Request already approved'},
                              status=status.HTTP_400_BAD_REQUEST)
            else:
                enrollment_request.status = 'pending'
                enrollment_request.notes = data.get('notes', enrollment_request.notes)
                enrollment_request.save()

        return Response({
            'message': 'Enrollment request submitted successfully',
            'request_id': enrollment_request.id,
            'status': enrollment_request.status,
            'deadline' : course.enrollment_deadline.isoformat() if course.enrollment_deadline else None
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@require_http_methods(["GET"])
def my_enrollments(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'enrolled_by').values(
        'id',
        'course__id',
        'course__name',
        'course__code',
        'course__credits',
        'enrollment_date',
        'grade',
        'enrolled_by__first_name',
        'enrolled_by__last_name'
    )

    return JsonResponse(list(enrollments), safe=False)


@require_http_methods(["GET"])
def my_enrollment_requests(request, student_id):
    student = get_object_or_404(Student, id=student_id)

    requests = EnrollmentRequest.objects.filter(student=student).select_related(
        'course', 'reviewed_by'
    ).values(
        'id',
        'course__name',
        'course__code',
        'status',
        'requested_at',
        'reviewed_at',
        'reviewed_by__first_name',
        'reviewed_by__last_name',
        'notes'
    )

    return JsonResponse(list(requests), safe=False)

