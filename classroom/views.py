import cv2
from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render
from .models import Classroom


# LIST CLASSROOM EXIST
def class_list_view(request):
    classes = Classroom.objects.all()
    return render(request, 'classroom/class_grid.html', {'classes': classes})



# CAMERA STREAMING GENERATOR
def gen_frames():
    cap = cv2.VideoCapture(0)  # DEFAULT WEB CAM 
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# VIDEO STREAM RESPONSE
@gzip.gzip_page
# -------------
def video_stream(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')


# PAGE
def classroom_camera_page(request):
    students = [
        {'name': 'Ahmed Kamal', 'initials': 'AK', 'present': False},
        {'name': 'Sara Mostafa', 'initials': 'SM', 'present': True},
        {'name': 'Omar Tarek', 'initials': 'OT', 'present': False},
        {'name': 'Laila Nour', 'initials': 'LN', 'present': True},
        {'name': 'Youssef Adel', 'initials': 'YA', 'present': False},
    ]
    return render(request, 'classroom/classroom_camera.html', {'students': students})









#=============== NOTE =================
'''
StreamingHttpResponse:
----------------------
    - we are using django: front+back  => HttpResponse
    - we want to take stream response  => StreamingHttpResponse

gzip: for performance
---------------------
    - reduces the size of the data sent from the server to the client using the GZIP algorithm,
      which makes your responses load faster 


content_type='multipart/x-mixed-replace; boundary=frame'
--------------------------------------------------------
    used for video stream - continuously sending a sequence of frames

'''

