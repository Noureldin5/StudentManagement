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
    list_display = ['student', 'course', 'status', 'requested_at', 'reviewed_by']
    list_filter = ['status', 'requested_at']
    search_fields = ['student__first_name', 'student__last_name', 'course__name']
    actions = ['approve_requests', 'reject_requests']
    
    def approve_requests(self, request, queryset):
        queryset.update(status='approved')
    approve_requests.short_description = "Approve selected requests"
    
    def reject_requests(self, request, queryset):
        queryset.update(status='rejected')
    reject_requests.short_description = "Reject selected requests"
