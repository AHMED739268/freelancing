from django.http import StreamingHttpResponse
from django.views.decorators import gzip
from django.shortcuts import render, get_object_or_404
from datetime import datetime
import cv2
import numpy as np
from django.utils import timezone
import threading
import face_recognition

from .models import Classroom
from Student.models import Student
from Course.models import Course
from Student.utills import record_attendance, send_course_reminder


def class_list_view(request):
    classes = Classroom.objects.all()
    return render(request, 'classroom/class_grid.html', {'classes': classes})


def gen_frames(level_students_encodings, classroom_id):
    cap = cv2.VideoCapture(0)
    processed_students = set()
    last_processed = {}
    classroom = Classroom.objects.get(id=classroom_id) # error might be here 

    while True:
        success, frame = cap.read()
        if not success:
            break

        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_embedding in zip(face_locations, face_encodings):
                best_match = None
                best_distance = 1.0  # max possible distance
                MATCH_THRESHOLD = 0.6  # recommended threshold for face_recognition

                for student in level_students_encodings:
                    known_encoding = np.array(student['encoding'])

                    if len(known_encoding) != 128:
                        continue  # Skip incompatible encodings

                    distance = face_recognition.face_distance([known_encoding], face_embedding)[0]

                    print(f"Distance with {student['name']} = {distance:.4f}")
                    print(f"Student {student['name']} first 5 dims: {known_encoding[:5]}")
                    print(f"Detected face first 5 dims: {face_embedding[:5]}")

                    if distance < best_distance:
                        best_distance = distance
                        best_match = student

                if best_match and best_distance < MATCH_THRESHOLD:
                    # === Match found ===
                    name = best_match['name']
                    student_id = best_match['id']
                    current_time = timezone.now()

                    # Draw green rectangle
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv2.putText(frame, name, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                    if student_id not in last_processed or \
                            (current_time - last_processed[student_id]).seconds > 60:

                        try:
                            student_obj = Student.objects.get(id=student_id)

                             # 1. Record attendance in background thread 
                            def record_attendance_thread():
                                recorded_course = record_attendance(student_obj, classroom)
                                if recorded_course:
                                    print(f"Attendance recorded for {student_obj.name} in {recorded_course.name}")

                            # # 2. Send course reminder in background thread
                            # def send_reminder_thread():
                            #     send_course_reminder(student_obj)
                            #     print(f"Reminder sent to {student_obj.email}")

                            threading.Thread(target=record_attendance_thread).start()
                            # threading.Thread(target=send_reminder_thread).start()

                            
                            last_processed[student_id] = current_time
                            processed_students.add(student_id)

                        except Exception as e:
                            print(f"Error processing student {student_id}: {e}")
                else:
                    # === Unknown face ===
                    cv2.rectangle(frame, (left, top), (right, bottom), (128, 128, 128), 2)
                    cv2.putText(frame, "Unknown", (left, top - 10),
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
            if student.face_encoding and len(student.face_encoding) == 128:
                level_students_encodings.append({
                    'id': student.id,
                    'name': student.name,
                    'encoding': student.face_encoding
                })

    print("classroom:", classroom_id) # debug

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



#===============LOGIC OF THE CAMERA IN THE RECPTION=====================



from .templates.classroom.email_log import add_email_message

def gen_reception_frames(level_students_encodings):

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not opened!")
        return
    print("✅ Camera opened successfully")
    processed_students = set()
    last_processed = {}
    
    while True:
        success, frame = cap.read()
        if not success:
            print("❌ Failed to read frame")
            break
        try:
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
            for (top, right, bottom, left), face_embedding in zip(face_locations, face_encodings):
                best_match = None
                best_distance = 1.0
                MATCH_THRESHOLD = 0.6
                for student in level_students_encodings:
                    known_encoding = np.array(student['encoding'])
                    if len(known_encoding) != 128:
                        continue
                    distance = face_recognition.face_distance([known_encoding], face_embedding)[0]
                    if distance < best_distance:
                        best_distance = distance
                        best_match = student
                if best_match and best_distance < MATCH_THRESHOLD:
                    name = best_match['name']
                    student_id = best_match['id']
                    current_time = timezone.now()
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 180, 0), 2)
                    cv2.putText(frame, name, (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 180, 0), 2)
                    if student_id not in last_processed or \
                            (current_time - last_processed[student_id]).seconds > 60:
                        try:
                            student_obj = Student.objects.get(id=student_id)
                            def send_reminder_thread():
                                send_course_reminder(student_obj)
                                add_email_message(f"📧 Reminder sent to {student_obj.email}")
                            threading.Thread(target=send_reminder_thread).start()
                            last_processed[student_id] = current_time
                        except Exception as e:
                            print(f"Error sending reminder: {e}")
                else:
                    cv2.rectangle(frame, (left, top), (right, bottom), (128, 128, 128), 2)
                    cv2.putText(frame, "Unknown", (left, top - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (128, 128, 128), 2)
        except Exception as e:
            print("Frame Error:", e)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    cap.release()  # Ensure camera is released when done

# FOR STREAMING FOR THE NEW PAGE

@gzip.gzip_page
def reception_stream(request):
    students = Student.objects.all()
    level_students_encodings = []
    for student in students:
        if student.face_encoding and len(student.face_encoding) == 128:
            level_students_encodings.append({
                'id': student.id,
                'name': student.name,
                'encoding': student.face_encoding
            })
    return StreamingHttpResponse(
        gen_reception_frames(level_students_encodings),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )



# HELPER FUNCTION

from django.http import JsonResponse
from .templates.classroom.email_log import get_all_messages

def get_email_messages(request):
    return JsonResponse({'messages': get_all_messages()})





def reception_page(request):
    return render(request, 'classroom/reception.html')



