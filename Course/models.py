from django.db import models

from Level.models import Level
class Course(models.Model):
    name = models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses')
    start_lecture = models.TimeField()
    end_lecture = models.TimeField()
    start_section = models.TimeField()
    end_section = models.TimeField()
    day_of_lecture = models.CharField(max_length=20)
    day_of_section = models.CharField(max_length=20)
    instructor_lecture = models.CharField(max_length=100)
    instructor_section = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.level.name})"
