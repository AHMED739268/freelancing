from django.shortcuts import render, get_object_or_404
from .models import Student, Attendance
from Course.models import Course
from collections import defaultdict

def student_attendance_report(request, student_id):
    # [AMS] GET STUDENT AND ATTENDANCE RECORDS
    student = get_object_or_404(Student, pk=student_id)
    attendance = Attendance.objects.filter(student=student).select_related('course')
    
    # [AMS] GROUP ATTENDANCE BY COURSE
    summary_dict = defaultdict(lambda: {'total': 0, 'present': 0, 'absent': 0})
    
    for record in attendance:
        course_name = record.course.name
        summary_dict[course_name]['total'] += 1
        if record.present:
            summary_dict[course_name]['present'] += 1
        else:
            summary_dict[course_name]['absent'] += 1
    
    # [AMS] CONVERT TO LIST AND CALCULATE PERCENTAGES
    summary = []
    total_present = 0
    total_absent = 0
    
    for course_name, counts in summary_dict.items():
        total = counts['total']
        present = counts['present']
        absent = counts['absent']
        percentage = round((present / total) * 100, 2) if total > 0 else 0.0
        
        summary.append({
            'course__name': course_name,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage
        })
        
        total_present += present
        total_absent += absent
    
    # Calculate overall attendance
    total_classes = total_present + total_absent
    overall_percentage = round((total_present / total_classes) * 100, 2) if total_classes > 0 else 0.0
    
    context = {
        'student': student,
        'attendance': attendance,
        'summary': summary,
        'total_present': total_present,
        'total_absent': total_absent,
        'overall_percentage': overall_percentage
    }
    return render(request, 'admin/student_attendance_report.html', context)

def course_attendance_report(request, course_id):
    # [AMS] GET COURSE AND ATTENDANCE RECORDS
    course = get_object_or_404(Course, pk=course_id)
    attendance = Attendance.objects.filter(course=course).select_related('student')
    
    # [AMS] GROUP ATTENDANCE BY STUDENT
    summary_dict = defaultdict(lambda: {'total': 0, 'present': 0, 'absent': 0})
    
    for record in attendance:
        student_name = record.student.name
        summary_dict[student_name]['total'] += 1
        if record.present:
            summary_dict[student_name]['present'] += 1
        else:
            summary_dict[student_name]['absent'] += 1
    
    # [AMS] CONVERT TO LIST AND CALCULATE PERCENTAGES
    summary = []
    attendance_percentages = []
    
    for student_name, counts in summary_dict.items():
        total = counts['total']
        present = counts['present']
        absent = counts['absent']
        percentage = round((present / total) * 100, 2) if total > 0 else 0.0
        
        summary.append({
            'student__name': student_name,
            'total': total,
            'present': present,
            'absent': absent,
            'percentage': percentage
        })
        
        attendance_percentages.append(percentage)
    
    # Calculate statistics
    total_students = len(summary)
    total_classes = attendance.count()
    avg_attendance = round(sum(attendance_percentages) / total_students, 2) if total_students > 0 else 0.0
    
    context = {
        'course': course,
        'attendance': attendance,
        'summary': summary,
        'total_students': total_students,
        'total_classes': total_classes,
        'avg_attendance': avg_attendance
    }
    return render(request, 'admin/course_attendance_report.html', context)