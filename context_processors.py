# Context processors for templates
from students.models import Student
from teachers.models import Teacher


def user_type_processor(request):
    """Add user type to all template contexts"""
    context = {
        'is_student': False,
        'is_teacher': False,
        'is_admin': False,
    }

    if request.user.is_authenticated:
        if request.user.is_superuser:
            context['is_admin'] = True
        else:
            try:
                Student.objects.get(user=request.user)
                context['is_student'] = True
            except Student.DoesNotExist:
                pass

            try:
                Teacher.objects.get(user=request.user)
                context['is_teacher'] = True
            except Teacher.DoesNotExist:
                pass

    return context

