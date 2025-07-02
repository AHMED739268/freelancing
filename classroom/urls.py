# classrooms/urls.py
from django.urls import path
from . import views

app_name = 'classrooms'

urlpatterns = [
    path('', views.class_list_view, name='class_list'),
    path('video/<int:classroom_id>/', views.video_stream, name='video_stream'),
    path('<int:classroom_id>/', views.classroom_camera_page, name='classroom_camera_page'),

    # Reception page and camera
    path('reception/', views.reception_page, name='reception_page'),
    path('reception/video/', views.reception_stream, name='reception_stream'),
    path('reception/emails/', views.get_email_messages, name='get_email_messages'),
]
