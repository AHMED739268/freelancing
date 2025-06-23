# views.py

from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render, get_object_or_404
from datetime import datetime
import cv2
import numpy as np
import tempfile
from deepface import DeepFace
from django.utils import timezone
from django.contrib import messages
import threading

from .models import Classroom
from Student.models import Student
from Course.models import Course
from Student.utills import record_attendance, send_course_reminder

THRESHOLD = 12.0  # Recommended for Facenet


def class_list_view(request):
    classes = Classroom.objects.all()
    return render(request, 'classroom/class_grid.html', {'classes': classes})


def gen_frames(level_students_encodings, classroom_id):
    cap = cv2.VideoCapture(0)
    processed_students = set()  # Track processed students in this session
    last_processed = {}  # Track last processing time per student
    classroom = Classroom.objects.get(id=classroom_id)
    
    while True:
        success, frame = cap.read()
        if not success:
            break

        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
                cv2.imwrite(tmp_file.name, frame)

                detections = DeepFace.extract_faces(
                    img_path=tmp_file.name,
                    detector_backend='opencv',
                    enforce_detection=False
                )

            for face_data in detections:
                facial_area = face_data['facial_area']
                x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

                try:
                    face = face_data['face']
                    resized_face = cv2.resize(face, (512, 512))

                    if resized_face.dtype == np.float64:
                        resized_face = (resized_face * 255).astype(np.uint8)

                    rgb_face = cv2.cvtColor(resized_face, cv2.COLOR_BGR2RGB)

                    face_embedding = DeepFace.represent(
                        rgb_face,
                        model_name='Facenet',
                        detector_backend='skip',
                        enforce_detection=False
                    )[0]['embedding']

                except Exception as e:
                    print("Embedding error:", e)
                    continue

                found = False
                for student in level_students_encodings:
                    known_encoding = np.array(student['encoding'])
                    dist = np.linalg.norm(np.array(face_embedding) - known_encoding)
                    print(f"dist with {student['name']} = {dist:.4f}")

                    if dist < THRESHOLD:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        cv2.putText(frame, student['name'], (x, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        found = True
                        
                        # Process attendance and reminders
                        student_id = student['id']
                        current_time = timezone.now()
                        
                        # Process at most once per minute per student
                        if student_id not in last_processed or \
                           (current_time - last_processed[student_id]).seconds > 60:
                            
                            try:
                                student_obj = Student.objects.get(id=student_id)
                                
                                # 1. Record attendance in background thread
                                def record_attendance_thread():
                                    recorded_course = record_attendance(student_obj, classroom)
                                    if recorded_course:
                                        print(f"Attendance recorded for {student_obj.name} in {recorded_course.name}")
                                
                                threading.Thread(target=record_attendance_thread).start()
                                
                                # 2. Send course reminder in background thread
                                def send_reminder_thread():
                                    send_course_reminder(student_obj)
                                    print(f"Reminder sent to {student_obj.email}")
                                
                                threading.Thread(target=send_reminder_thread).start()
                                
                                # Update tracking
                                last_processed[student_id] = current_time
                                processed_students.add(student_id)
                                
                            except Exception as e:
                                print(f"Error processing student {student_id}: {e}")
                        
                        break

                if not found:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (128, 128, 128), 2)
                    cv2.putText(frame, "Unknown", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)

        except Exception as e:
            print("Frame Error:", e)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@gzip.gzip_page
def video_stream(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    now = datetime.now()
    current_day = now.strftime('%a')
    current_time = now.time()

    course = Course.objects.filter(
        classroom=classroom,
        day_of_lecture=current_day,
        start_lecture__lte=current_time,
        end_lecture__gte=current_time
    ).first()

    level_students_encodings = []

    if course:
        students = Student.objects.filter(level=course.level)
        for student in students:
            if student.face_encoding:
                level_students_encodings.append({
                    'id': student.id,  # Added student ID
                    'name': student.name,
                    'encoding': student.face_encoding
                })

    return StreamingHttpResponse(
        gen_frames(level_students_encodings, classroom_id),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )


def classroom_camera_page(request, classroom_id):
    classroom = get_object_or_404(Classroom, pk=classroom_id)

    now = datetime.now()
    current_day = now.strftime('%a')
    current_time = now.time()

    course_qs = Course.objects.filter(
        classroom=classroom,
        day_of_lecture=current_day,
        start_lecture__lte=current_time,
        end_lecture__gte=current_time
    ).select_related('level', 'instructor_lecture')

    if not course_qs.exists():
        return render(request, 'classroom/no_active_course.html', {
            'message': f"There are no courses scheduled for today in classroom {classroom.letter}.",
            'classroom': classroom,
            'current_day_full': now.strftime('%A'),
        })

    course = course_qs.first()

    students_queryset = Student.objects.filter(level=course.level)

    students = []
    for student in students_queryset:
        initials = ''.join([part[0].upper() for part in student.name.split() if part])[:2]
        students.append({
            'name': student.name,
            'initials': initials,
            'present': False,
            'student_image': student.student_image 
        })

    return render(request, 'classroom/classroom_camera.html', {
        'students': students,
        'lecture_start': course.start_lecture.strftime('%H:%M:%S'),
        'lecture_end': course.end_lecture.strftime('%H:%M:%S'),
        'lecture_start_ampm': course.start_lecture.strftime('%I:%M %p'),
        'lecture_end_ampm': course.end_lecture.strftime('%I:%M %p'),
        'level': course.level,
        'instructor_lecture': course.instructor_lecture,
        'classroom': classroom,
        'course_name': course.name
    })