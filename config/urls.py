from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    ######[AMS]ATTENDANCE REPORTS URLS 
    path('', include('Student.urls')),
    #####################################
    path('admin/', admin.site.urls),
    path('classrooms/', include('classroom.urls')),   
# [SENU]: HANDLE IMAGE VIEW
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
