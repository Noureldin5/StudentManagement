from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Student
import json

# Create your views here.

@require_http_methods(["GET"])
def get_students(request):
    students = Student.objects.all().values()
    return JsonResponse(list(students), safe=False)
@csrf_exempt
@require_http_methods(["POST"])
def add_student(request):
    data = json.loads(request.body)
    student = Student.objects.create(
    first_name = data.get('first_name'),
    last_name = data.get('last_name'),
    course = data.get('course'),
    age = data.get('age'),
    gpa = data.get('gpa')
    )
    student.save()
    return HttpResponse("Student added successfully")

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_student(request, id):
    student = Student.objects.get(id=id)
    student.delete()
    return HttpResponse("Student deleted successfully")



