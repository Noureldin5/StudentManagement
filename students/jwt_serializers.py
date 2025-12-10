"""
Custom JWT serializers for authentication with user type information
"""
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT serializer that adds user type and profile information to the token response
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims to the token
        token['username'] = user.username
        token['email'] = user.email

        # Determine user type and add to token
        if hasattr(user, 'teacher_profile'):
            token['user_type'] = 'teacher'
            token['profile_id'] = user.teacher_profile.id
            token['first_name'] = user.teacher_profile.first_name
            token['last_name'] = user.teacher_profile.last_name
        elif hasattr(user, 'student_profile'):
            token['user_type'] = 'student'
            token['profile_id'] = user.student_profile.id
            token['first_name'] = user.student_profile.first_name
            token['last_name'] = user.student_profile.last_name
        else:
            token['user_type'] = 'admin'
            token['profile_id'] = None

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        # Add extra responses to the token response
        user = self.user

        user_type = None
        profile_id = None
        first_name = ''
        last_name = ''

        if hasattr(user, 'teacher_profile'):
            user_type = 'teacher'
            profile_id = user.teacher_profile.id
            first_name = user.teacher_profile.first_name
            last_name = user.teacher_profile.last_name
        elif hasattr(user, 'student_profile'):
            user_type = 'student'
            profile_id = user.student_profile.id
            first_name = user.student_profile.first_name
            last_name = user.student_profile.last_name

        data.update({
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'user_type': user_type,
            'profile_id': profile_id,
            'first_name': first_name,
            'last_name': last_name,
        })

        return data

