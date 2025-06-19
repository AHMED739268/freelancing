from django.urls import path
from . import views

urlpatterns = [


    # for classroom grid 
    path('', views.class_list_view, name='class_list'),

    # for classroom camera
    path('stream/', views.classroom_camera_page, name='camera_page'),
    path('video_stream/', views.video_stream, name='video_stream'),

    
]
