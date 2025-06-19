from django.db import models
from Level.models import Level
from Course.models import Course
from deepface import DeepFace
from django.core.exceptions import ValidationError
from PIL import Image


# STUDENT MODEL
class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    level = models.ForeignKey(Level, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    student_image = models.ImageField(upload_to='students/images/')
    face_encoding = models.JSONField(null=True, blank=True)

    def save(self, *args, **kwargs):
        # STEP 1: First save image so it's available on disk
        is_new = self._state.adding and not self.pk
        super().save(*args, **kwargs)

        # STEP 2: If face_encoding not yet done, run DeepFace
        if self.student_image and not self.face_encoding:
            try:
                # Optional: Resize to speed up encoding
                img = Image.open(self.student_image.path)
                img = img.resize((512, 512))
                img.save(self.student_image.path)

                # Generate embedding
                representations = DeepFace.represent(
                    img_path=self.student_image.path,
                    model_name='SFace',
                    detector_backend='opencv',
                    enforce_detection=True
                )

                if representations:
                    self.face_encoding = representations[0]["embedding"]
                    # STEP 3: Save encoding only
                    super().save(update_fields=["face_encoding"])

            except Exception as e:
                raise ValidationError([f"DeepFace face embedding failed: {e}"])

    def __str__(self):
        return self.name


# INSTRUCTOR MODEL
class Instructor(models.Model):
    name = models.CharField(max_length=100)
    Instructor_image = models.ImageField(upload_to='instructors/images/')

    def __str__(self):
        return self.name
