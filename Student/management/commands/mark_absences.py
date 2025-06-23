from django.core.management.base import BaseCommand
from django.utils import timezone
from Student.models import Student, Attendance, Course
from datetime import datetime, time
from django.db.models import Q
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Marks students absent for missed course sessions'

    def handle(self, *args, **options):
        now = timezone.localtime()
        today = now.date()
        current_time = now.time()
        current_day = now.strftime('%a')  # e.g., 'Mon'
        # Find courses that ended today
        ended_courses = Course.objects.filter(
            Q(day_of_lecture=current_day, end_lecture__lt=current_time) |
            Q(day_of_section=current_day, end_section__lt=current_time)
        )

        for course in ended_courses:
            # Process lecture
            if course.day_of_lecture == current_day and course.end_lecture < current_time:
                self.process_session(course, 'lecture', today)
            
            # Process section
            if course.day_of_section == current_day and course.end_section < current_time:
                self.process_session(course, 'section', today)

    def process_session(self, course, session_type, date_today):
        enrolled_students = course.student_set.all()
        
        for student in enrolled_students:
            # Check if attendance already exists
            exists = Attendance.objects.filter(
                student=student,
                course=course,
                session_type=session_type,
                timestamp__date=date_today
            ).exists()
            
            if not exists:
                # Mark student absent
                Attendance.objects.create(
                    student=student,
                    course=course,
                    session_type=session_type,
                    present=False
                )
                self.stdout.write(f"Marked absent: {student.name} for {course.name} {session_type}")
                
                # Send absence notification
                self.send_absence_email(student, course, session_type, date_today)

    def send_absence_email(self, student, course, session_type, date):
        if student.email:
            subject = f"Absence Recorded: {course.name} {session_type}"
            message = (
                f"Dear {student.name},\n\n"
                f"You were marked absent for the {session_type} of "
                f"{course.name} on {date}.\n\n"
                "If this is a mistake, please contact your instructor.\n\n"
                "Best regards,\nAttendance Management System"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.EMAIL_HOST_USER,
                    [student.email],
                    fail_silently=False,
                )
                self.stdout.write(f"Sent absence email to {student.email}")
            except Exception as e:
                self.stderr.write(f"Failed to send email to {student.email}: {e}")