from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Enrollment, EnrollmentRequest
from teachers.serializers import TeacherSerializer,UserSerializer
from courses.serializers import CourseSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    gpa = serializers.FloatField(read_only=True)  # Calculated property, read-only

    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'age', 'gpa', 'created_at']

class StudentRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    age = serializers.IntegerField()

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        student = Student.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            age=validated_data['age']
        )

        return student


class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    enrolled_by = TeacherSerializer(read_only=True)
    letter_grade = serializers.CharField(read_only=True)  # Calculated property

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_by', 'enrollment_date', 'grade', 'letter_grade']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    reviewed_by = TeacherSerializer(read_only=True)

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'course', 'status', 'requested_at', 'reviewed_by', 'reviewed_at', 'notes']

