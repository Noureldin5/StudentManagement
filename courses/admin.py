from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'credits', 'created_at','openings']
    search_fields = ['name', 'code']

