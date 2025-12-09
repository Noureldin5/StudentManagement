from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'subject', 'created_at']
    search_fields = ['first_name', 'last_name', 'subject']
    filter_horizontal = ['courses']  # This enables the widget for ManyToMany field
    list_filter = ['subject', 'created_at']
    readonly_fields = ['created_at']
