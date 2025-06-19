from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render, get_object_or_404
from datetime import datetime
import cv2

from .models import Classroom
from Student.models import Student
from Course.models import Course

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
def video_stream(request):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

# CLASSROOM CAMERA PAGE WITH COURSE & STUDENTS LOGIC
def classroom_camera_page(request, classroom_id):
    # Get classroom or 404
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    # Get current day and time
    now = datetime.now()
    current_day = now.strftime('%a') 
    current_time = now.time()

    # Find a course for this classroom where current time is between lecture start/end and day matches
    course_qs = Course.objects.filter(
        classroom=classroom,
        day_of_lecture=current_day,
        start_lecture__lte=current_time,
        end_lecture__gte=current_time
    ).select_related('level', 'instructor_lecture')

    if not course_qs.exists():
        # NO ACTIVE COURSE - send a friendly page instead of 404
        context = {
            'message': f"There are no courses scheduled for today in classroom {classroom.letter}.",
            'classroom': classroom,
            'current_day_full': now.strftime('%A'),  # Full day name for display
        }
        return render(request, 'classroom/no_active_course.html', context)

    course = course_qs.first()

    # Fetch students with the same level as course.level
    students_queryset = Student.objects.filter(level=course.level)

    # Convert students to your template format
    students = []
    for student in students_queryset:
        initials = ''.join([part[0].upper() for part in student.name.split() if part])[:2]
        students.append({
            'name': student.name,
            'initials': initials,
            'present': False,
        })

    context = {
        'students': students,
        'lecture_start': course.start_lecture.strftime('%H:%M:%S'),  
        'lecture_end': course.end_lecture.strftime('%H:%M:%S'),     
        'lecture_start_ampm': course.start_lecture.strftime('%I:%M %p'), 
        'lecture_end_ampm': course.end_lecture.strftime('%I:%M %p'),     
        'level': course.level,
        'instructor_lecture': course.instructor_lecture,
        'classroom': classroom,
        'course_name': course.name
    }







    return render(request, 'classroom/classroom_camera.html', context)
