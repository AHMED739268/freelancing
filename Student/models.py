from django.db import models
from Level.models import Level
from Course.models import Course
from deepface import DeepFace
from django.core.exceptions import ValidationError
import cv2
import numpy as np
#####[AMS] 
from django.utils import timezone
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

        if self.student_image and (self.face_encoding is None):
            try:
                img_path = self.student_image.path
                img = cv2.imread(img_path)

                if img is None:
                    raise ValidationError(["Image not found or unreadable."])

                # === Resize and convert to RGB ===
                resized_img = cv2.resize(img, (512, 512))
                rgb_img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2RGB)

                # === Ensure it's uint8 ===
                if rgb_img.dtype == np.float64:
                    rgb_img = (rgb_img * 255).astype(np.uint8)

                # === Generate embedding ===
                representations = DeepFace.represent(
                    rgb_img,
                    model_name='Facenet',
                    detector_backend='skip',  # already cropped
                    enforce_detection=True
                )

                if representations:
                    self.face_encoding = representations[0]["embedding"]
                    super().save(update_fields=["face_encoding"])

            except Exception as e:
                raise ValidationError([f"DeepFace face embedding failed: {e}"])

    def __str__(self):
        return self.name
    
###########[AMS] ADD AN ATTR TO GET NEXT COURSE FOR STUDENT
    def get_next_course(self):
        now = timezone.localtime()
        current_time = now.time()
        current_day = now.strftime('%a')
        
        # Get upcoming courses within next 24 hours
        upcoming = []
        for course in self.courses.all():
            # Check lecture
            if course.day_of_lecture == current_day and course.start_lecture > current_time:
                upcoming.append({
                    'course': course,
                    'start': course.start_lecture,
                    'location': course.classroom,
                    'type': 'Lecture'
                })
            # Check section
            if course.day_of_section == current_day and course.start_section > current_time:
                upcoming.append({
                    'course': course,
                    'start': course.start_section,
                    'location': course.classroom,
                    'type': 'Section'
                })
        
        # Return nearest course
        return min(upcoming, key=lambda x: x['start']) if upcoming else None

##################################################




# INSTRUCTOR MODEL
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    Instructor_image = models.ImageField(upload_to='instructors/images/')

    def __str__(self):
        return self.name
