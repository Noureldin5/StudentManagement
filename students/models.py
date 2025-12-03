from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from teachers.models import Teacher
from courses.models import Course


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    gpa = models.FloatField()
    enrolled_courses = models.ManyToManyField(Course, through='Enrollment', related_name='enrolled_students')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Student: {self.first_name} {self.last_name}'


class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='students_enrolled')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrollment_date']

    def clean(self):
        if self.course.is_full and not self.pk:  # Only check for new enrollments
            raise ValidationError(f'Course {self.course.code} is full ({self.course.openings} students)')

        if Enrollment.objects.filter(student=self.student, course=self.course).exists():
            raise ValidationError(f'Student is already enrolled in {self.course.code}')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.student} enrolled in {self.course}'


class EnrollmentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('waitlisted', 'Waitlisted'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollment_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment_requests')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    priority = models.IntegerField(default=0, help_text="Higher number = higher priority")

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-priority', '-requested_at']

    def clean(self):
        if Enrollment.objects.filter(student=self.student, course=self.course).exists():
            raise ValidationError(f'Student is already enrolled in {self.course.code}')

        # Check if there's already a pending request
        existing_request = EnrollmentRequest.objects.filter(
            student=self.student,
            course=self.course,
            status='pending'
        ).exclude(pk=self.pk)

        if existing_request.exists():
            raise ValidationError(f'Student already has a pending request for {self.course.code}')

    def save(self, *args, **kwargs):
        self.clean()

        if not self.pk and self.status == 'pending' and self.course.is_full:
            self.status = 'waitlisted'
            self.notes = f'Automatically waitlisted - course at capacity ({self.course.openings})'

        super().save(*args, **kwargs)

    def approve(self, teacher):
        if self.course.is_full:
            raise ValidationError(
                f'Cannot approve - course is full ({self.course.enrolled_students}/{self.course.openings})')

        # Create enrollment
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course,
            enrolled_by=teacher
        )

        self.status = 'approved'
        self.reviewed_by = teacher
        self.reviewed_at = timezone.now()
        self.save()

        self.course.process_waitlist()

        return enrollment

    def reject(self, teacher, reason=''):
        self.status = 'rejected'
        self.reviewed_by = teacher
        self.reviewed_at = timezone.now()
        if reason:
            self.notes = reason
        self.save()

    def __str__(self):
        return f'{self.student} - {self.course} ({self.status})'
