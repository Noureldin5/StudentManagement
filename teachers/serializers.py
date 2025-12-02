from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Teacher


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    courses = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id','user','first_name','last_name','subject','courses','created_at']
class TeacherRegistrationSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True,min_length=8)
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
