
from django.core.mail import send_mail
from django.conf import settings
from .models import Student, Attendance
from django.utils import timezone 
def record_attendance(student, classroom):
    now = timezone.localtime()
    current_time = now.time()
    current_date = now.date()
    current_day = now.strftime('%a')
    
    # Get courses in the current classroom
    courses_in_classroom = student.courses.filter(classroom=classroom)
    
    for course in courses_in_classroom:
        # Check if attendance already exists for today
        existing_attendance = Attendance.objects.filter(
            student=student,
            course=course,
            timestamp__date=current_date,
            session_type__in=['lecture', 'section']
        ).exists()
        
        if existing_attendance:
            continue  # Skip if already recorded
        
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
    try:
        next_course = student.get_next_course()
        if not next_course:
            print(f"No upcoming courses found for {student.name}")
            return False
            
        if not student.email:
            print(f"No email available for {student.name}")
            return False
            
        # Format times properly
        start_time = next_course['start'].strftime('%I:%M %p')
        course_date = next_course['datetime'].strftime('%A, %B %d')
        
        subject = f"Upcoming {next_course['type']}: {next_course['course'].name}"
        message = (
            f"Hello {student.name},\n\n"
            f"Your next {next_course['type']} for {next_course['course'].name} "
            f"is scheduled for {course_date} at {start_time}.\n"
            f"Location: {next_course['location']}\n\n"
            "Please arrive 10 minutes early."
        )
        
        # Print message for debugging
        print(f"Sending reminder to {student.email}:\n{subject}\n{message}")
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                fail_silently=False,
            )
            print(f"Email sent successfully to {student.email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {student.email}: {str(e)}")
            return False
    except Exception as e:
        print(f"Error in send_course_reminder: {str(e)}")
        return False
    
    
def send_current_course_reminder(student):
    try:
        next_course = student.get_current_course()
        if not next_course:
            print(f"No upcoming courses found for {student.name}")
            return False
            
        if not student.email:
            print(f"No email available for {student.name}")
            return False
            
        # Format times properly
        start_time = next_course['start'].strftime('%I:%M %p')
        course_date = next_course['datetime'].strftime('%A, %B %d')
        
        subject = f"Upcoming {next_course['type']}: {next_course['course'].name}"
        message = (
            f"Hello {student.name},\n\n"
            f"Your next {next_course['type']} for {next_course['course'].name} "
            f"is scheduled for {course_date} at {start_time}.\n"
            f"Location: {next_course['location']}\n\n"
            "Please arrive 10 minutes early."
        )
        
        # Print message for debugging
        print(f"Sending reminder to {student.email}:\n{subject}\n{message}")
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [student.email],
                fail_silently=False,
            )
            print(f"Email sent successfully to {student.email}")
            return True
        except Exception as e:
            print(f"Failed to send email to {student.email}: {str(e)}")
            return False
    except Exception as e:
        print(f"Error in send_course_reminder: {str(e)}")
        return False
    
    
# [AMS] SENU START TO USE 
# FETCH STUDENT FROM CAMERA 
# CALL THE FOLLOWING METHODS   
#  record_attendance(student)
# send_course_reminder(student)