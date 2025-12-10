# Template-based views for the Student Management System
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from students.models import Student, Enrollment, EnrollmentRequest
from teachers.models import Teacher
from courses.models import Course
from django.utils import timezone
from functools import wraps
from activity_logger import ActivityLogger


def get_user_type(user):
    """Determine user type: 'admin', 'teacher', or 'student'"""
    if user.is_superuser:
        return 'admin'
    try:
        Teacher.objects.get(user=user)
        return 'teacher'
    except Teacher.DoesNotExist:
        pass
    try:
        Student.objects.get(user=user)
        return 'student'
    except Student.DoesNotExist:
        pass
    return None


def student_required(view_func):
    """Decorator to restrict access to students only"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_type = get_user_type(request.user)
        if user_type == 'admin':
            # Admins have access to everything
            return view_func(request, *args, **kwargs)
        elif user_type == 'student':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Access denied. Students only.')
            return redirect('/')
    return wrapper


def teacher_required(view_func):
    """Decorator to restrict access to teachers only"""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        user_type = get_user_type(request.user)
        if user_type == 'admin':
            # Admins have access to everything
            return view_func(request, *args, **kwargs)
        elif user_type == 'teacher':
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, 'Access denied. Teachers only.')
            return redirect('/')
    return wrapper


def home_view(request):
    """Home page"""
    return render(request, 'home.html')


def login_view(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        # Get IP address and user agent
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')

        if user:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Log successful login
            ActivityLogger.log_login(user, success=True, ip_address=ip_address, user_agent=user_agent)

            # Redirect based on user type
            user_type = get_user_type(user)
            if user_type == 'admin':
                return redirect('/admin/')
            elif user_type == 'teacher':
                return redirect('/teacher-dashboard/')
            elif user_type == 'student':
                return redirect('/student-dashboard/')
            else:
                messages.error(request, 'No profile found for this user')
                logout(request)
                return redirect('/login/')
        else:
            messages.error(request, 'Invalid username or password')
            # Log failed login attempt
            ActivityLogger.log_login(None, success=False, ip_address=ip_address, user_agent=user_agent)

    return render(request, 'login.html')


def logout_view(request):
    """User logout"""
    # Get IP address and user agent before logout
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT')
    user = request.user if request.user.is_authenticated else None
    
    # Log logout
    if user:
        ActivityLogger.log_logout(user, ip_address=ip_address, user_agent=user_agent)
    
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('/')


def register_student_view(request):
    """Student registration"""
    if request.method == 'POST':
        try:
            # Create user
            user = User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password']
            )

            # Create student profile (no GPA - it will be calculated)
            Student.objects.create(
                user=user,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                age=int(request.POST['age'])
            )

            # Log registration
            ActivityLogger.log_registration(user, 'student')

            messages.success(request, 'Registration successful! Please login.')
            return redirect('/login/')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'register_student.html')


def register_teacher_view(request):
    """Teacher registration"""
    if request.method == 'POST':
        try:
            # Create user with staff privileges
            user = User.objects.create_user(
                username=request.POST['username'],
                email=request.POST['email'],
                password=request.POST['password']
            )
            user.is_staff = True
            user.save()

            # Create teacher profile
            Teacher.objects.create(
                user=user,
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                subject=request.POST['subject']
            )

            # Log registration
            ActivityLogger.log_registration(user, 'teacher')

            messages.success(request, 'Teacher registration successful! Please login.')
            return redirect('/login/')
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'register_teacher.html')


def courses_list_view(request):
    """List all courses"""
    courses = Course.objects.all()
    return render(request, 'courses_list.html', {'courses': courses})


def course_detail_view(request, course_id):
    """Course detail page"""
    course = get_object_or_404(Course, id=course_id)
    teachers = course.teachers.all()
    enrollments = Enrollment.objects.filter(course=course).select_related('student')

    return render(request, 'course_detail.html', {
        'course': course,
        'teachers': teachers,
        'enrollments': enrollments
    })


@student_required
def request_enrollment_view(request, course_id):
    """Request course enrollment - Students only"""
    course = get_object_or_404(Course, id=course_id)

    # Get student profile
    try:
        student = request.user.student_profile
    except:
        messages.error(request, 'Only students can request enrollment')
        return redirect('/course-detail/' + str(course_id) + '/')

    if request.method == 'POST':
        try:
            # Check if deadline has passed
            if course.enrollment_deadline and timezone.now() > course.enrollment_deadline:
                messages.error(request, 'Enrollment deadline has passed')
                return redirect('/course-detail/' + str(course_id) + '/')

            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course=course).exists():
                messages.error(request, 'You are already enrolled in this course')
                return redirect('/student-dashboard/')

            # Check if already requested
            existing_request = EnrollmentRequest.objects.filter(
                student=student,
                course=course
            ).first()

            if existing_request and existing_request.status == 'pending':
                messages.warning(request, 'You already have a pending request for this course')
                return redirect('/student-dashboard/')

            # Create enrollment request
            status = 'waitlisted' if course.is_full else 'pending'

            enrollment_request = EnrollmentRequest.objects.create(
                student=student,
                course=course,
                enrollment_deadline=course.enrollment_deadline,
                notes=request.POST.get('notes', ''),
                status=status
            )

            # Log enrollment request
            ActivityLogger.log_enrollment_request(student, course, 'created')

            if status == 'waitlisted':
                messages.warning(request, f'Course is full. You have been added to the waitlist.')
            else:
                messages.success(request, 'Enrollment request submitted successfully!')

            return redirect('/student-dashboard/')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return render(request, 'request_enrollment.html', {'course': course})


@student_required
def student_dashboard_view(request):
    """Student dashboard - Students only"""
    # For admins, show the first student or create a message
    if request.user.is_superuser:
        student = Student.objects.first()
        if not student:
            messages.info(request, 'No students in the system yet. This is an admin view.')
            return render(request, 'student_dashboard.html', {
                'student': None,
                'enrollments': [],
                'requests': [],
                'pending_requests': 0
            })
    else:
        try:
            student = request.user.student_profile
        except:
            messages.error(request, 'Student profile not found')
            return redirect('/')

    enrollments = Enrollment.objects.filter(student=student).select_related('course', 'enrolled_by')
    requests = EnrollmentRequest.objects.filter(student=student).select_related('course', 'reviewed_by')
    pending_requests = requests.filter(status='pending').count()

    return render(request, 'student_dashboard.html', {
        'student': student,
        'enrollments': enrollments,
        'requests': requests,
        'pending_requests': pending_requests
    })


@teacher_required
def teacher_dashboard_view(request):
    """Teacher dashboard - Teachers only"""
    # For admins, show the first teacher or create a message
    if request.user.is_superuser:
        teacher = Teacher.objects.first()
        if not teacher:
            messages.info(request, 'No teachers in the system yet. This is an admin view.')
            return render(request, 'teacher_dashboard.html', {
                'teacher': None,
                'courses': [],
                'pending_requests': [],
                'pending_count': 0,
                'total_students': 0
            })
    else:
        try:
            teacher = request.user.teacher_profile
        except:
            messages.error(request, 'Teacher profile not found')
            return redirect('/')

    courses = teacher.courses.all()

    # Get all pending requests for teacher's courses
    pending_requests = EnrollmentRequest.objects.filter(
        course__in=courses,
        status__in=['pending', 'waitlisted']
    ).select_related('student', 'course')

    # Calculate total students
    total_students = Enrollment.objects.filter(course__in=courses).count()

    return render(request, 'teacher_dashboard.html', {
        'teacher': teacher,
        'courses': courses,
        'pending_requests': pending_requests,
        'pending_count': pending_requests.count(),
        'total_students': total_students
    })


@teacher_required
def approve_request_view(request, request_id):
    """Approve enrollment request - Teachers only"""
    if request.method == 'POST':
        try:
            # Get teacher profile (or first teacher for admin)
            if request.user.is_superuser:
                teacher = Teacher.objects.first()
                if not teacher:
                    messages.error(request, 'No teachers in system. Create a teacher first.')
                    return redirect('/teacher-dashboard/')
            else:
                teacher = request.user.teacher_profile

            enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

            # Verify teacher teaches this course (skip for admin)
            if not request.user.is_superuser:
                if not enrollment_request.course.teachers.filter(id=teacher.id).exists():
                    messages.error(request, 'You are not assigned to this course')
                    return redirect('/teacher-dashboard/')

            # Check if course is full
            if enrollment_request.course.is_full:
                messages.error(request, 'Cannot approve - course is full')
                return redirect('/teacher-dashboard/')

            # Use the model's approve method (handles enrollment creation, email, and waitlist)
            enrollment_request.approve(teacher)

            # Log approval
            ActivityLogger.log_enrollment_request(
                enrollment_request.student, 
                enrollment_request.course, 
                'approved', 
                teacher
            )

            messages.success(request, f'Approved enrollment for {enrollment_request.student.first_name} {enrollment_request.student.last_name}')


        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('/teacher-dashboard/')


@teacher_required
def reject_request_view(request, request_id):
    """Reject enrollment request - Teachers only"""
    if request.method == 'POST':
        try:
            # Get teacher profile (or first teacher for admin)
            if request.user.is_superuser:
                teacher = Teacher.objects.first()
                if not teacher:
                    messages.error(request, 'No teachers in system. Create a teacher first.')
                    return redirect('/teacher-dashboard/')
            else:
                teacher = request.user.teacher_profile

            enrollment_request = get_object_or_404(EnrollmentRequest, id=request_id)

            # Verify teacher teaches this course (skip for admin)
            if not request.user.is_superuser:
                if not enrollment_request.course.teachers.filter(id=teacher.id).exists():
                    messages.error(request, 'You are not assigned to this course')
                    return redirect('/teacher-dashboard/')

            # Use the model's reject method (handles status update and email)
            reason = request.POST.get('reason', 'Rejected by instructor')
            enrollment_request.reject(teacher, reason)

            # Log rejection
            ActivityLogger.log_enrollment_request(
                enrollment_request.student, 
                enrollment_request.course, 
                'rejected', 
                teacher,
                reason
            )

            messages.warning(request, f'Rejected enrollment request from {enrollment_request.student.first_name} {enrollment_request.student.last_name}')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('/teacher-dashboard/')


@teacher_required
def teacher_course_students_view(request, course_id):
    """View students in a course - Teachers only"""
    try:
        # Get teacher profile (or first teacher for admin)
        if request.user.is_superuser:
            teacher = Teacher.objects.first()
        else:
            teacher = request.user.teacher_profile

        course = get_object_or_404(Course, id=course_id)

        # Verify teacher teaches this course (skip for admin)
        if not request.user.is_superuser and teacher:
            if not course.teachers.filter(id=teacher.id).exists():
                messages.error(request, 'You are not assigned to this course')
                return redirect('/teacher-dashboard/')

        students = Enrollment.objects.filter(course=course).select_related('student', 'enrolled_by')

        return render(request, 'teacher_course_students.html', {
            'course': course,
            'students': students
        })

    except Exception as e:
        messages.error(request, f'Error: {str(e)}')
        return redirect('/teacher-dashboard/')


@teacher_required
def update_grade_view(request, enrollment_id):
    """Update student grade - Teachers only"""
    enrollment = get_object_or_404(Enrollment, id=enrollment_id)

    if request.method == 'POST':
        try:
            # Get teacher profile (or first teacher for admin)
            if request.user.is_superuser:
                teacher = Teacher.objects.first()
            else:
                teacher = request.user.teacher_profile

            # Verify teacher teaches this course (skip for admin)
            if not request.user.is_superuser and teacher:
                if not enrollment.course.teachers.filter(id=teacher.id).exists():
                    messages.error(request, 'You are not assigned to this course')
                    return redirect('/teacher-dashboard/')

            # Update grade - must be numeric (0-100)
            grade_str = request.POST.get('grade')
            if grade_str and grade_str.strip():
                try:
                    grade = float(grade_str)
                    if 0 <= grade <= 100:
                        old_grade = enrollment.grade
                        enrollment.grade = grade
                        enrollment.save()
                        
                        # Log grade update
                        ActivityLogger.log_grade_update(enrollment, old_grade, grade, teacher)
                        
                        messages.success(request, f'Updated grade for {enrollment.student.first_name} {enrollment.student.last_name} to {grade} ({enrollment.letter_grade})')
                    else:
                        messages.error(request, 'Grade must be between 0 and 100')
                except ValueError:
                    messages.error(request, 'Grade must be a valid number')
            elif grade_str == '':
                # Clear grade
                old_grade = enrollment.grade
                enrollment.grade = None
                enrollment.save()
                
                # Log grade clearing
                ActivityLogger.log_grade_update(enrollment, old_grade, None, teacher)
                
                messages.success(request, f'Cleared grade for {enrollment.student.first_name} {enrollment.student.last_name}')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('/teacher-course-students/' + str(enrollment.course.id) + '/')


def students_list_view(request):
    """List all students"""
    students = Student.objects.all().select_related('user')
    return render(request, 'students_list.html', {'students': students})


def student_detail_view(request, student_id):
    """Student detail page"""
    student = get_object_or_404(Student, id=student_id)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')

    return render(request, 'student_detail.html', {
        'student': student,
        'enrollments': enrollments
    })


def teachers_list_view(request):
    """List all teachers"""
    teachers = Teacher.objects.all().select_related('user')
    return render(request, 'teachers_list.html', {'teachers': teachers})


@teacher_required
def direct_enroll_view(request, course_id):
    """Direct enrollment form - Teachers only"""
    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = request.user.teacher_profile

    course = get_object_or_404(Course, id=course_id)

    # Verify teacher teaches this course (skip for admin)
    if not request.user.is_superuser and teacher:
        if not course.teachers.filter(id=teacher.id).exists():
            messages.error(request, 'You are not assigned to this course')
            return redirect('/teacher-dashboard/')

    if request.method == 'POST':
        try:
            student_id = request.POST.get('student_id')
            student = get_object_or_404(Student, id=student_id)

            # Check if course is full
            if course.is_full:
                messages.error(request, f'Cannot enroll - course is full ({course.enrolled_count}/{course.openings})')
                return redirect('/teacher-course-students/' + str(course_id) + '/')

            # Check if already enrolled
            if Enrollment.objects.filter(student=student, course=course).exists():
                messages.error(request, f'{student.first_name} {student.last_name} is already enrolled')
                return redirect('/teacher-course-students/' + str(course_id) + '/')

            # Create enrollment
            enrollment = Enrollment.objects.create(
                student=student,
                course=course,
                enrolled_by=teacher,
                enrollment_deadline=course.enrollment_deadline
            )
            
            # Log direct enrollment
            ActivityLogger.log_enrollment(student, course, teacher, "direct_enroll")

            messages.success(request, f'Successfully enrolled {student.first_name} {student.last_name} in {course.name}')
            return redirect('/teacher-course-students/' + str(course_id) + '/')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    # Get all students not enrolled in this course
    enrolled_student_ids = Enrollment.objects.filter(course=course).values_list('student_id', flat=True)
    available_students = Student.objects.exclude(id__in=enrolled_student_ids).select_related('user')

    return render(request, 'direct_enroll.html', {
        'course': course,
        'available_students': available_students
    })


@teacher_required
def update_deadline_view(request, course_id):
    """Update course enrollment deadline - Teachers only"""
    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = request.user.teacher_profile

    course = get_object_or_404(Course, id=course_id)

    # Verify teacher teaches this course (skip for admin)
    if not request.user.is_superuser and teacher:
        if not course.teachers.filter(id=teacher.id).exists():
            messages.error(request, 'You are not assigned to this course')
            return redirect('/teacher-dashboard/')

    if request.method == 'POST':
        try:
            deadline_str = request.POST.get('enrollment_deadline')

            if deadline_str:
                from django.utils.dateparse import parse_datetime
                deadline = parse_datetime(deadline_str)
                if not deadline:
                    messages.error(request, 'Invalid date format')
                    return redirect('/manage-course/' + str(course_id) + '/')
            else:
                deadline = None

            old_deadline = course.enrollment_deadline
            course.enrollment_deadline = deadline
            course.save()

            # Log deadline update
            ActivityLogger.log_course_deadline_update(course, old_deadline, deadline, teacher)

            # Update pending enrollment requests
            EnrollmentRequest.objects.filter(
                course=course,
                status='pending'
            ).update(enrollment_deadline=deadline)

            if deadline:
                messages.success(request, f'Enrollment deadline updated to {deadline.strftime("%B %d, %Y %I:%M %p")}')
            else:
                messages.success(request, 'Enrollment deadline removed')

            return redirect('/manage-course/' + str(course_id) + '/')

        except Exception as e:
            messages.error(request, f'Error: {str(e)}')

    return redirect('/manage-course/' + str(course_id) + '/')


@teacher_required
def manage_course_view(request, course_id):
    """Course management page - Teachers only"""
    if request.user.is_superuser:
        teacher = Teacher.objects.first()
    else:
        teacher = request.user.teacher_profile

    course = get_object_or_404(Course, id=course_id)

    # Verify teacher teaches this course (skip for admin)
    if not request.user.is_superuser and teacher:
        if not course.teachers.filter(id=teacher.id).exists():
            messages.error(request, 'You are not assigned to this course')
            return redirect('/teacher-dashboard/')

    # Get course statistics
    enrollments = Enrollment.objects.filter(course=course).select_related('student')
    pending_requests = EnrollmentRequest.objects.filter(
        course=course,
        status__in=['pending', 'waitlisted']
    ).select_related('student')

    # Get all students not enrolled
    enrolled_student_ids = enrollments.values_list('student_id', flat=True)
    available_students = Student.objects.exclude(id__in=enrolled_student_ids).select_related('user')

    return render(request, 'manage_course.html', {
        'course': course,
        'enrollments': enrollments,
        'pending_requests': pending_requests,
        'available_students': available_students,
        'teacher': teacher
    })
