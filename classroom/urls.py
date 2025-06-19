from django.urls import path
from . import views

urlpatterns = [
    path('', views.class_list_view, name='class_list'),
    path('<int:classroom_id>/', views.classroom_camera_page, name='classroom_camera_page'),
    path('video/', views.video_stream, name='video_stream'),
]
