from django.urls import path
from .views import student_attendance_report, course_attendance_report

urlpatterns = [
    path('admin/student/<int:student_id>/attendance/', 
         student_attendance_report, name='student_attendance_report'),
    path('admin/course/<int:course_id>/attendance/', 
         course_attendance_report, name='course_attendance_report'),
]