from django.db import models
from Level.models import Level
from django.contrib.auth.models import User
from Course.models import Course


# STUDENT MODEL
class Student(models.Model):

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    #[SENU]: 
    student_image = models.ImageField(upload_to='students/images/')
    face_encoding = models.JSONField()

    def __str__(self):
        return self.name
    


# [SENU]: ADD INSTRUCTOR MODEL
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    Instructor_image = models.ImageField(upload_to='instructors/images/') 
