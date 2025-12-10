"""
Custom JWT authentication views
"""
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .jwt_serializers import CustomTokenObtainPairSerializer


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that uses our custom serializer
    """
    serializer_class = CustomTokenObtainPairSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get the authenticated user's profile information
    Requires JWT token in Authorization header: Bearer <token>
    """
    user = request.user

    user_data = {
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'is_staff': user.is_staff,
    }

    if hasattr(user, 'teacher_profile'):
        teacher = user.teacher_profile
        user_data.update({
            'user_type': 'teacher',
            'profile_id': teacher.id,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'subject': teacher.subject,
            'courses': list(teacher.courses.values('id', 'name', 'code'))
        })
    elif hasattr(user, 'student_profile'):
        student = user.student_profile
        user_data.update({
            'user_type': 'student',
            'profile_id': student.id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'age': student.age,
            'gpa': student.gpa,
        })
    else:
        user_data['user_type'] = 'admin'

    return Response(user_data)


@api_view(['POST'])
def register_student_jwt(request):
    """
    Register a new student and return JWT tokens
    """
    from .serializers import StudentRegistrationSerializer
    from rest_framework_simplejwt.tokens import RefreshToken

    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(student.user)
        refresh['user_type'] = 'student'
        refresh['profile_id'] = student.id
        refresh['first_name'] = student.first_name
        refresh['last_name'] = student.last_name

        return Response({
            'message': 'Student registered successfully',
            'user_id': student.user.id,
            'username': student.user.username,
            'student_id': student.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': 'student',
            'profile_id': student.id,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def register_teacher_jwt(request):
    """
    Register a new teacher and return JWT tokens
    """
    from teachers.serializers import TeacherRegistrationSerializer
    from rest_framework_simplejwt.tokens import RefreshToken

    serializer = TeacherRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()

        # Generate JWT tokens for the new user
        refresh = RefreshToken.for_user(teacher.user)
        refresh['user_type'] = 'teacher'
        refresh['profile_id'] = teacher.id
        refresh['first_name'] = teacher.first_name
        refresh['last_name'] = teacher.last_name

        return Response({
            'message': 'Teacher registered successfully',
            'user_id': teacher.user.id,
            'username': teacher.user.username,
            'teacher_id': teacher.id,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_type': 'teacher',
            'profile_id': teacher.id,
        }, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

