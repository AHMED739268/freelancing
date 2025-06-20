from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

# Register your models here.
from .models import Course
from Student.models import Attendance
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'level', 'day_of_lecture', 'instructor_lecture','attendance_summary', 'attendance_summary_link']
    list_filter = ['level', 'day_of_lecture']
    search_fields = ['name', 'instructor_lecture']
    # [AMS] METHODE TO SHOW STUDENT ATTENDANCE 
    def attendance_summary(self, obj):
        present = Attendance.objects.filter(course=obj, present=True).count()
        absent = Attendance.objects.filter(course=obj, present=False).count()
        return f"Present: {present}, Absent: {absent}"
    attendance_summary.short_description = 'Attendance Summary'
    
    class AttendanceInline(admin.TabularInline):
        model = Attendance
        extra = 0
        fields = ['student', 'timestamp', 'present']
        readonly_fields = ['timestamp']
        can_delete = False
        
    inlines = [AttendanceInline]
    
    def attendance_summary_link(self, obj):
        url = reverse('course_attendance_report', args=[obj.pk])
        return format_html('<a href="{}">View Attendance Report</a>', url)
    attendance_summary_link.short_description = 'Detailed Report'
