
from rest_framework import serializers
from .models import Course


class CourseSerializer(serializers.ModelSerializer):
    enrolled_students = serializers.IntegerField(read_only=True)
    available_spots = serializers.IntegerField(read_only=True)
    is_enrollment_open = serializers.BooleanField(read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'credits', 'openings',
                  'enrollment_deadline', 'enrolled_students', 'available_spots',
                  'is_enrollment_open', 'created_at']
