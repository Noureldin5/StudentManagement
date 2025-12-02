
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Course
from students.models import Enrollment


@require_http_methods(["GET"])
def course_list(request):
    courses = Course.objects.all().values(
        'id', 'name', 'code', 'description', 'credits', 'created_at'
    )

    courses_list = []
    for course in courses:
        enrollment_count = Enrollment.objects.filter(course_id=course['id']).count()
        course['enrolled_students'] = enrollment_count
        courses_list.append(course)

    return JsonResponse(courses_list, safe=False)


@require_http_methods(["GET"])
def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    teachers = course.teachers.all().values(
        'id', 'first_name', 'last_name', 'subject'
    )

    enrollment_count = Enrollment.objects.filter(course=course).count()

    data = {
        'id': course.id,
        'name': course.name,
        'code': course.code,
        'description': course.description,
        'credits': course.credits,
        'created_at': course.created_at,
        'enrolled_students': enrollment_count,
        'teachers': list(teachers)
    }

    return JsonResponse(data)


@require_http_methods(["GET"])
def course_enrollments(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    enrollments = Enrollment.objects.filter(course=course).select_related(
        'student', 'enrolled_by'
    ).values(
        'id',
        'student__id',
        'student__first_name',
        'student__last_name',
        'student__gpa',
        'enrollment_date',
        'grade',
        'enrolled_by__first_name',
        'enrolled_by__last_name'
    ).order_by('-enrollment_date')

    return JsonResponse({
        'course': {
            'id': course.id,
            'name': course.name,
            'code': course.code
        },
        'total_enrollments': len(enrollments),
        'enrollments': list(enrollments)
    })

