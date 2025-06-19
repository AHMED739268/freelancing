from django.db import models

class Classroom(models.Model):
    letter = models.CharField(max_length=255)

    def __str__(self):
        return f"classroom {self.letter}"
