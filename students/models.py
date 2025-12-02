from django.db import models
from django.contrib.auth.models import User
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
    enrolled_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='students_enrolled')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    grade = models.CharField(max_length=2, blank=True, null=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f'{self.student} enrolled in {self.course}'

class EnrollmentRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollment_requests')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollment_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    requested_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_requests')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-requested_at']
    
    def __str__(self):
        return f'{self.student} - {self.course} ({self.status})'


