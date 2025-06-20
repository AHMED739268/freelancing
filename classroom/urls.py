# classrooms/urls.py
from django.urls import path
from . import views

app_name = 'classrooms'

urlpatterns = [
    path('', views.class_list_view, name='class_list'),
    path('video/<int:classroom_id>/', views.video_stream, name='video_stream'),  # <-- updated
    path('<int:classroom_id>/', views.classroom_camera_page, name='classroom_camera_page'),
]
