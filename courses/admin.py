from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'openings', 'get_enrolled_count', 'get_available_spots', 'created_at']
    search_fields = ['name', 'code']
    readonly_fields = ['created_at', 'get_enrolled_count', 'get_available_spots', 'get_is_full']

    def get_enrolled_count(self, obj):
        return obj.enrolled_students
    get_enrolled_count.short_description = 'Enrolled'

    def get_available_spots(self, obj):
        return obj.available_spots
    get_available_spots.short_description = 'Available'

    def get_is_full(self, obj):
        return obj.is_full
    get_is_full.short_description = 'Full?'
    get_is_full.boolean = True

