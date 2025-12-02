from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student, Teacher, Course, Enrollment, EnrollmentRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

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
    gpa = serializers.FloatField(default=0.0)

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
            age=validated_data['age'],
            gpa=validated_data.get('gpa', 0.0)
        )

        return student

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    courses = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'first_name', 'last_name', 'subject', 'courses', 'created_at']

class TeacherRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    subject = serializers.CharField(max_length=50)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        user.is_staff = True
        user.save()

        teacher = Teacher.objects.create(
            user=user,
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            subject=validated_data['subject']
        )

        return teacher

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'credits', 'created_at']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    enrolled_by = TeacherSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_by', 'enrollment_date', 'grade']

class EnrollmentRequestSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    reviewed_by = TeacherSerializer(read_only=True)

    class Meta:
        model = EnrollmentRequest
        fields = ['id', 'student', 'course', 'status', 'requested_at', 'reviewed_by', 'reviewed_at', 'notes']

