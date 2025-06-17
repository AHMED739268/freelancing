from django.contrib import admin


from   .models import Level

@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']