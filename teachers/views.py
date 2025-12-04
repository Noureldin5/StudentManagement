from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Teacher
from students.models import Student, Enrollment, EnrollmentRequest
from courses.models import Course
import json


@require_http_methods(["GET"])
def teacher_list(request):
    teachers = Teacher.objects.all().values(
        'id', 'first_name', 'last_name', 'subject',
        'user__username', 'user__email', 'created_at'
    )
    return JsonResponse(list(teachers), safe=False)



@require_http_methods(["GET"])
def teacher_detail(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    courses = teacher.courses.all().values('id', 'name', 'code', 'credits')

    data = {
        'id': teacher.id,
        'first_name': teacher.first_name,
        'last_name': teacher.last_name,
        'subject': teacher.subject,
        'user': {
            'id': teacher.user.id,
            'username': teacher.user.username,
            'email': teacher.user.email
        },
        'courses': list(courses),
        'created_at': teacher.created_at
    }

    return JsonResponse(data)


@require_http_methods(["GET"])
def pending_requests(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    requests = EnrollmentRequest.objects.filter(
        course__in=teacher.courses.all(),
        status='pending'
    ).select_related('student', 'course').values(
        'id',
        'student__id',
        'student__first_name',
        'student__last_name',
        'student__gpa',
        'course__id',
        'course__name',
        'course__code',
        'requested_at',
        'notes'
    ).order_by('-requested_at')

    return JsonResponse(list(requests), safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def approve_request(request, request_id):
    try:
        data = json.loads(request.body)
        teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
        enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

        # Permission check
        if enrollment_request.course not in teacher.courses.all():
            return JsonResponse({
                'error': 'You do not have permission to approve requests for this course'
            }, status=403)

        # Check if already approved
        if enrollment_request.status == 'approved':
            return JsonResponse({'error': 'Request already approved'}, status=400)

        # Check if course is full
        if enrollment_request.course.is_full:
            return JsonResponse({
                'error': f'Cannot enroll - course is full ({enrollment_request.course.enrolled_students}/{enrollment_request.course.openings})'
            }, status=400)
        enrollment = enrollment_request.approve(teacher)

        return JsonResponse({
            'message': 'Enrollment request approved successfully',
            'enrollment_id': enrollment.id,
            'student': f"{enrollment_request.student.first_name} {enrollment_request.student.last_name}",
            'course': enrollment_request.course.name
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def reject_request(request, request_id):
    try:
        data = json.loads(request.body)
        teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
        enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

        # Permission check
        if enrollment_request.course not in teacher.courses.all():
            return JsonResponse({
                'error': 'You do not have permission to reject requests for this course'
            }, status=403)

        # Update request
        enrollment_request.status = 'rejected'
        enrollment_request.reviewed_by = teacher
        enrollment_request.reviewed_at = timezone.now()
        enrollment_request.notes = data.get('notes', enrollment_request.notes)
        enrollment_request.save()

        return JsonResponse({
            'message': 'Enrollment request rejected',
            'student': f"{enrollment_request.student.first_name} {enrollment_request.student.last_name}",
            'course': enrollment_request.course.name,
            'notes': enrollment_request.notes
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def direct_enroll(request):
    try:
        data = json.loads(request.body)

        teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
        student = get_object_or_404(Student, id=data.get('student_id'))
        course = get_object_or_404(Course, id=data.get('course_id'))

        # Permission check
        if course not in teacher.courses.all():
            return JsonResponse({
                'error': 'You do not have permission to enroll students in this course'
            }, status=403)

        # if course is full
        if course.is_full:
            return JsonResponse({
                'error': f'Cannot enroll - course is full ({course.enrolled_students}/{course.openings})'
            }, status=400)

        # Create enrollment
        enrollment, created = Enrollment.objects.get_or_create(
            student=student,
            course=course,
            defaults={'enrolled_by': teacher}
        )

        if not created:
            return JsonResponse({
                'error': 'Student is already enrolled in this course'
            }, status=400)

        return JsonResponse({
            'message': 'Student enrolled successfully',
            'enrollment_id': enrollment.id,
            'student': f"{student.first_name} {student.last_name}",
            'course': course.name,
            'enrolled_by': f"{teacher.first_name} {teacher.last_name}"
        }, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def course_students(request, teacher_id, course_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    course = get_object_or_404(Course, id=course_id)

    # Permission check
    if course not in teacher.courses.all():
        return JsonResponse({
            'error': 'You do not have permission to view students in this course'
        }, status=403)

    enrollments = Enrollment.objects.filter(course=course).select_related('student').values(
        'id',
        'student__id',
        'student__first_name',
        'student__last_name',
        'student__age',
        'student__gpa',
        'enrollment_date',
        'grade',
        'enrolled_by__first_name',
        'enrolled_by__last_name'
    ).order_by('student__last_name')

    return JsonResponse({
        'course': {
            'id': course.id,
            'name': course.name,
            'code': course.code
        },
        'total_students': len(enrollments),
        'students': list(enrollments)
    }, safe=False)


@csrf_exempt
@require_http_methods(["PUT"])
def update_enrollment_deadline(request, course_id):
    try:
        data = json.loads(request.body)
        teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
        course = get_object_or_404(Course, id=course_id)
        if course not in teacher.courses.all():
            return JsonResponse({
                'error': 'You do not have permission to update enrollment deadline for this course'
            }, status=403)
        deadline_str = data.get('enrollment_deadline')
        if deadline_str:
            deadline = parse_datetime(deadline_str)
            if not deadline:
                return JsonResponse({'error': 'Invalid enrollment deadline'}, status=400)
        else:
            deadline = None
        old_deadline = course.enrollment_deadline
        course.enrollment_deadline = deadline
        course.save()

        EnrollmentRequest.objects.filter(
            course=course, status='pending'
        ).update(enrollment_deadline=deadline)

        return JsonResponse(
            {'message': 'Enrollment deadline updated successfully', 'course': course.name,
             'old_deadline': old_deadline,
             'new_deadline': deadline,
             'updated_by': f"{teacher.first_name} {teacher.last_name}"}
        )
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
@require_http_methods(["PUT"])
def update_grade(request, enrollment_id):
    try:
        data = json.loads(request.body)

        teacher = get_object_or_404(Teacher, id=data.get('teacher_id'))
        enrollment = get_object_or_404(Enrollment, id=enrollment_id)

        # Permission check
        if enrollment.course not in teacher.courses.all():
            return JsonResponse({
                'error': 'You do not have permission to update grades for this course'
            }, status=403)

        # Update grade
        old_grade = enrollment.grade
        enrollment.grade = data.get('grade')
        enrollment.save()

        return JsonResponse({
            'message': 'Grade updated successfully',
            'student': f"{enrollment.student.first_name} {enrollment.student.last_name}",
            'course': enrollment.course.name,
            'old_grade': old_grade,
            'new_grade': enrollment.grade
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["GET"])
def my_courses(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)

    courses = teacher.courses.all().values(
        'id', 'name', 'code', 'description', 'credits', 'created_at'
    )

    # Add student count for each course
    courses_list = []
    for course in courses:
        student_count = Enrollment.objects.filter(course_id=course['id']).count()
        course['student_count'] = student_count
        courses_list.append(course)

    return JsonResponse({
        'teacher': f"{teacher.first_name} {teacher.last_name}",
        'subject': teacher.subject,
        'total_courses': len(courses_list),
        'courses': courses_list
    })
