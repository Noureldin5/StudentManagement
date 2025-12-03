from django.contrib import admin
from .models import Student, Enrollment, EnrollmentRequest
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age', 'gpa', 'user']
    search_fields = ['first_name', 'last_name']

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_by', 'enrollment_date', 'grade']
    list_filter = ['enrollment_date', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']

@admin.register(EnrollmentRequest)
class EnrollmentRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'requested_at', 'reviewed_by', 'priority']
    list_filter = ['status', 'requested_at', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']
    actions = ['approve_requests', 'reject_requests']
    readonly_fields = ['requested_at', 'reviewed_at']

    def approve_requests(self, request, queryset):
        approved_count = 0
        failed_count = 0
        errors = []

        for enrollment_request in queryset.filter(status='pending'):
            try:
                # Use the proper approve method which checks capacity
                enrollment_request.approve(teacher=None)
                approved_count += 1
            except Exception as e:
                failed_count += 1
                errors.append(f"{enrollment_request.student} - {enrollment_request.course}: {str(e)}")

        if approved_count:
            self.message_user(request, f"Successfully approved {approved_count} request(s).")
        if failed_count:
            error_message = f"Failed to approve {failed_count} request(s). Errors: " + "; ".join(errors[:5])
            if len(errors) > 5:
                error_message += f" and {len(errors) - 5} more..."
            self.message_user(request, error_message, level='warning')

    approve_requests.short_description = "Approve selected requests (checks capacity)"

    def reject_requests(self, request, queryset):
        rejected_count = 0
        for enrollment_request in queryset.exclude(status='rejected'):
            try:
                enrollment_request.reject(teacher=None, reason='Rejected by admin')
                rejected_count += 1
            except Exception as e:
                self.message_user(request, f"Error rejecting {enrollment_request}: {str(e)}", level='error')

        if rejected_count:
            self.message_user(request, f"Successfully rejected {rejected_count} request(s).")

    reject_requests.short_description = "Reject selected requests"
