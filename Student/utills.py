
from django.core.mail import send_mail
from django.conf import settings
from .models import Student, Attendance
from django.utils import timezone 
def record_attendance(student):
    now = timezone.localtime()
    current_time = now.time()
    current_day = now.strftime('%a')
    
    for course in student.courses.all():
        # Lecture attendance
        if course.day_of_lecture == current_day:
            if course.start_lecture <= current_time <= course.end_lecture:
                Attendance.objects.create(
                    student=student,
                    course=course,
                    session_type='lecture',
                    present=True
                )
                return course
        
        # Section attendance
        if course.day_of_section == current_day:
            if course.start_section <= current_time <= course.end_section:
                Attendance.objects.create(
                    student=student,
                    course=course,
                    session_type='section',
                    present=True
                )
                return course
    return None
def send_course_reminder(student):
    next_course = student.get_next_course()
    if next_course and student.email:
        subject = f"Upcoming Course: {next_course['course'].name}"
        message = (
            f"Hello {student.name},\n\n"
            f"Your next {next_course['type']} for {next_course['course'].name} "
            f"is in {next_course['location']} at {next_course['start']}.\n\n"
            "Please arrive 10 minutes early."
        )
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [student.email],
            fail_silently=False,
        )
      
# [AMS] SENU START TO USE 
# FETCH STUDENT FROM CAMERA 
# CALL THE FOLLOWING METHODS   
#  record_attendance(student)
# send_course_reminder(student)