from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Student, Instructor,Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'level', 'attendance_summary','attendance_summary_link'] # [SENU]: removed user [we don't need it]
    list_filter = ['level']
    search_fields = ['name']
    filter_horizontal = ('courses',)
    fields = ('name', 'age', 'level', 'courses', 'student_image','email')
    # [AMS] METHODE TO SHOW STUDENT ATTENDANCE 
    def attendance_summary(self, obj):
        present = Attendance.objects.filter(student=obj, present=True).count()
        absent = Attendance.objects.filter(student=obj, present=False).count()
        return f"Present: {present}, Absent: {absent}"
    attendance_summary.short_description = 'Attendance Summary'
    
    def attendance_summary_link(self, obj):
        url = reverse('student_attendance_report', args=[obj.pk])
        return format_html('<a href="{}">View Attendance Report</a>', url)
    attendance_summary_link.short_description = 'Detailed Report'

# [SENU]: add instructor
@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name']


#[AMS] ADD ATTENDANCE TO ADMIN AND MAKE HIM CAN FILTER - SEARCH
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'session_type', 'timestamp', 'present']
    list_filter = ['course', 'present', 'timestamp', 'session_type']
    search_fields = ['student__name', 'course__name']
    date_hierarchy = 'timestamp'
class AttendanceInline(admin.TabularInline):
    model = Attendance
    fields = ['student', 'session_type', 'timestamp', 'present']
    
