from django.db import models
from Level.models import Level
from Course.models import Course
from django.core.exceptions import ValidationError
import cv2
import face_recognition
import numpy as np

#####[AMS] 
from django.utils import timezone
from datetime import datetime, timedelta

###################


#########[AMS] ABSENSE MANAGEMENT SYSTEM
######### LOGIC STARTS HERE 
class Attendance(models.Model):
    SESSION_TYPES = (
        ('lecture', 'Lecture'),
        ('section', 'Section'),
    )
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    course = models.ForeignKey('Course.Course', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=True)
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='lecture')
    
    def __str__(self):
        status = "Present" if self.present else "Absent"
        return f"{self.student.name} - {self.course.name} - {self.session_type} ({status})"
########################################################


class Student(models.Model):
    name = models.CharField(max_length=100)
    # [AMS] EMAIL FIELD TO SEND TO STUDENT
    email = models.EmailField(blank=True, null=True)
    #####################################
    age = models.PositiveIntegerField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    student_image = models.ImageField(upload_to='students/images/')
    face_encoding = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding and not self.pk
        super().save(*args, **kwargs)

        if self.student_image and self.face_encoding is None:
            try:
                img_path = self.student_image.path
                img = cv2.imread(img_path)

                if img is None:
                    raise ValidationError(["Image not found or unreadable."])

                # === Convert to RGB for face_recognition ===
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # === Generate embedding using face_recognition ===
                face_locations = face_recognition.face_locations(rgb_img)
                encodings = face_recognition.face_encodings(rgb_img, face_locations)

                if encodings:
                    encoding_array = encodings[0]
                    # === Optional: normalize for cosine similarity consistency ===
                    normalized_encoding = encoding_array / np.linalg.norm(encoding_array)
                    self.face_encoding = normalized_encoding.tolist()
                    super().save(update_fields=["face_encoding"])
                else:
                    raise ValidationError(["No face detected in the image."])

            except Exception as e:
                raise ValidationError([f"face_recognition embedding failed: {e}"])

    def __str__(self):
        return self.name

###########[AMS] ADD AN ATTR TO GET NEXT COURSE FOR STUDENT
# Update the get_next_course method
    def get_next_course(self):
        now = timezone.localtime()
        current_time = now.time()
        current_day = now.strftime('%a')
        
        # Map day abbreviations to weekday numbers
        day_map = {
            'Mon': 0, 'Tue': 1, 'Wed': 2, 
            'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
        }
        
        # Create a list of all upcoming sessions
        upcoming = []
        
        for course in self.courses.all():
            # Process lecture
            if course.day_of_lecture:
                # Calculate next lecture date
                lecture_day_num = day_map[course.day_of_lecture]
                current_weekday = now.weekday()
                days_until_lecture = (lecture_day_num - current_weekday) % 7
                if days_until_lecture == 0 and course.start_lecture <= current_time:
                    days_until_lecture = 7  # Move to next week if already passed
                next_lecture_date = now.date() + timedelta(days=days_until_lecture)
                next_lecture_datetime = datetime.combine(next_lecture_date, course.start_lecture)
                next_lecture_datetime = timezone.make_aware(next_lecture_datetime)
                
                upcoming.append({
                    'course': course,
                    'start': course.start_lecture,
                    'datetime': next_lecture_datetime,
                    'location': course.classroom,
                    'type': 'Lecture'
                })
            
            # Process section
            if course.day_of_section:
                section_day_num = day_map[course.day_of_section]
                current_weekday = now.weekday()
                days_until_section = (section_day_num - current_weekday) % 7
                if days_until_section == 0 and course.start_section <= current_time:
                    days_until_section = 7
                next_section_date = now.date() + timedelta(days=days_until_section)
                next_section_datetime = datetime.combine(next_section_date, course.start_section)
                next_section_datetime = timezone.make_aware(next_section_datetime)

                upcoming.append({
                    'course': course,
                    'start': course.start_section,
                    'datetime': next_section_datetime,
                    'location': course.classroom,
                    'type': 'Section'
                })

        future_sessions = [s for s in upcoming if s['datetime'] > now]
        return min(future_sessions, key=lambda x: x['datetime']) if future_sessions else None
    
    def get_current_course(self):
        now = timezone.localtime()
        current_time = now.time()
        current_day = now.strftime('%a')

        day_map = {
            'Mon': 0, 'Tue': 1, 'Wed': 2, 
            'Thu': 3, 'Fri': 4, 'Sat': 5, 'Sun': 6
        }

        upcoming = []

        for course in self.courses.all():
            if course.day_of_lecture:
                lecture_day_num = day_map[course.day_of_lecture]
                current_weekday = now.weekday()
                days_until_lecture = (lecture_day_num - current_weekday) % 7
                if days_until_lecture == 0 and course.start_lecture <= current_time:
                    days_until_lecture = 7
                next_lecture_date = now.date() + timedelta(days=days_until_lecture)
                next_lecture_datetime = datetime.combine(next_lecture_date, course.start_lecture)
                next_lecture_datetime = timezone.make_aware(next_lecture_datetime)

                upcoming.append({
                    'course': course,
                    'start': course.start_lecture,
                    'datetime': next_lecture_datetime,
                    'location': course.classroom,
                    'type': 'Lecture'
                })

            if course.day_of_section:
                section_day_num = day_map[course.day_of_section]
                current_weekday = now.weekday()
                days_until_section = (section_day_num - current_weekday) % 7
                if days_until_section == 0 and course.start_section <= current_time:
                    days_until_section = 7
                next_section_date = now.date() + timedelta(days=days_until_section)
                next_section_datetime = datetime.combine(next_section_date, course.start_section)
                next_section_datetime = timezone.make_aware(next_section_datetime)

                upcoming.append({
                    'course': course,
                    'start': course.start_section,
                    'datetime': next_section_datetime,
                    'location': course.classroom,
                    'type': 'Section'
                })

        future_sessions = [s for s in upcoming if s['datetime'] > now]
        return min(future_sessions, key=lambda x: x['datetime']) if future_sessions else None

##################################################


# INSTRUCTOR MODEL
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    Instructor_image = models.ImageField(upload_to='instructors/images/')

    def __str__(self):
        return self.name
