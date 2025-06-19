from django.contrib import admin


from .models import Student, Instructor

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'level', 'user']
    list_filter = ['level']
    search_fields = ['name']
    filter_horizontal = ('courses',)


# [SENU]: add instructor
@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['name']
