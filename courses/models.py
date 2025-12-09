
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    credits = models.IntegerField(default=3)
    openings = models.PositiveIntegerField(default=20)
    enrollment_deadline = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    @property
    def enrolled_students(self):
        return self.enrollments.count()

    @property
    def enrolled_count(self):
        return self.enrollments.count()

    @property
    def available_spots(self):
        return max(0, self.openings - self.enrolled_students)
    @property
    def is_full(self):
        return self.enrolled_students >= self.openings


    @property
    def is_enrollment_open(self):
        if not self.enrollment_deadline:
            return True
        return timezone.now() <= self.enrollment_deadline

    def can_enroll(self):
        return not self.is_full

    def process_waitlist(self):
        from students.models import Enrollment

        while not self.is_full:
            next_request = self.enrollment_requests.filter(
                status='waitlisted'
            ).order_by('-priority', 'requested_at').first()

            if not next_request:
                break

            try:
                # Try to approve
                next_request.status = 'pending'
                next_request.save()

                Enrollment.objects.create(
                    student=next_request.student,course=self,enrolled_by=None)

                next_request.status = 'approved'
                next_request.reviewed_at = timezone.now()
                next_request.notes = 'Auto-approved from waitlist'
                next_request.save()
            except ValidationError:
                break


    def __str__(self):
        return f'{self.code} - {self.name}'
