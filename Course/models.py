from django.db import models
from classroom.models import Classroom

DAY = [
    ('Sat', 'Saturday'),
    ('Sun', 'Sunday'),
    ('Mon', 'Monday'),
    ('Tue', 'Tuesday'),
    ('Wed', 'Wednesday'),
    ('Thu', 'Thursday'),
    ('Fri', 'Friday'),
]



from Level.models import Level
class Course(models.Model):

    name = models.CharField(max_length=100)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='courses')


    # LECTURE: DAY - TIME 
    day_of_lecture = models.CharField(max_length=3, choices=DAY) # [SENU]: ALTERED TO CHOICES
    start_lecture = models.TimeField()
    end_lecture = models.TimeField()

    # SECTION: DAY - TIME 
    day_of_section = models.CharField(max_length=3, choices=DAY) # [SENU]: ALTERED TO CHOICES
    start_section = models.TimeField()
    end_section = models.TimeField()

    # [SENU]l ATLER INSTRUCTOR
    instructor_lecture = models.ForeignKey('Student.Instructor',on_delete=models.SET_NULL,null=True,blank=True,related_name='lecture_courses'  )
    instructor_section = models.ForeignKey('Student.Instructor',on_delete=models.SET_NULL,null=True,blank=True,related_name='section_courses'  )




    # [??]
    notes = models.TextField(blank=True)

    # [SENU]: ADD CLASS (ONE-MANY)
    # ----------------------------
    classroom = models.ForeignKey(
        Classroom, on_delete=models.CASCADE,
        related_name='courses'  # [SENU] allows classroom.courses.all()
    )



    def __str__(self):
        return self.name
