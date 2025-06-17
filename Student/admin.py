from django.contrib import admin


from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['name', 'age', 'level', 'user']
    list_filter = ['level']
    search_fields = ['name']
    filter_horizontal = ('courses',)