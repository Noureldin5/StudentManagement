from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'credits', 'created_at','openings', 'enrolled_students', 'available_spots', 'is_full']
