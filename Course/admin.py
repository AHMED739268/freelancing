from django.contrib import admin

# Register your models here.
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'day_of_lecture', 'instructor_lecture']
    list_filter = ['level', 'day_of_lecture']
    search_fields = ['name', 'instructor_lecture']