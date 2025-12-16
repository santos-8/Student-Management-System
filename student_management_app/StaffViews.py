from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.core import serializers
from django.urls import reverse
from django.contrib import messages
import json

from datetime import datetime
from student_management_app.models import Subjects, SessionYearModel, Students, Attendance, AttendanceReport, LeaveReportStaff, Staffs, FeedBackStaffs, CustomUser, Courses


def staff_home(request):
    #For Fetching All Student Under Staff
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    course_id_list=[]
    for subject in subjects:
        course=Courses.objects.get(id=subject.course_id.id)
        course_id_list.append(course.id)
    
    final_course=[]
    #Removing Duplicate Course ID
    for course_id in course_id_list:
        if course_id not in final_course:
            final_course.append(course_id)
    
    students_count=Students.objects.filter(course_id__in=final_course).count()

    #Fetch All Attendance Count
    attendance_count=Attendance.objects.filter(subject_id__in=subjects).count()
    
    #Fetch All Approved Leave
    staff=Staffs.objects.get(admin=request.user.id)
    leave_count=LeaveReportStaff.objects.filter(staff_id=staff.id,leave_status=1).count()
    subject_count=subjects.count()

    #Fetch Attendance Data by Subject
    subject_list=[]
    attendance_list=[]
    for subject in subjects:
        attendance_count1=Attendance.objects.filter(subject_id=subject.id).count()
        subject_list.append(subject.subject_name)
        attendance_list.append(attendance_count1)

    students_attendance=Students.objects.filter(course_id__in=final_course)
    student_list=[]
    student_list_attendance_present=[]
    student_list_attendance_absent=[]
    for student in students_attendance:
        attendance_present_count=AttendanceReport.objects.filter(status=True,student_id=student.id).count()
        attendance_absent_count=AttendanceReport.objects.filter(status=False,student_id=student.id).count()
        student_list.append(student.admin.username)
        student_list_attendance_present.append(attendance_present_count)
        student_list_attendance_absent.append(attendance_absent_count)

    return render(request,"staff_template/staff_home_template.html",{"students_count":students_count,"attendance_count":attendance_count,"leave_count":leave_count,"subject_count":subject_count,"subject_list":subject_list,"attendance_list":attendance_list,"student_list":student_list,"present_list":student_list_attendance_present,"absent_list":student_list_attendance_absent})

def staff_take_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_years=SessionYearModel.objects.all()
    return render(request,"staff_template/staff_take_attendance.html",{"subjects":subjects,"session_years":session_years})

@csrf_exempt
def get_students(request):
    subject_id=request.POST.get("subject")
    session_year=request.POST.get("session_year")

    subject=Subjects.objects.get(id=subject_id)
    session_model=SessionYearModel.objects.get(id=session_year)
    students=Students.objects.filter(course_id=subject.course_id,session_year_id=session_model)
    list_data=[]

    for student in students:
        data_small={"id":student.admin.id,"name":student.admin.first_name+" "+student.admin.last_name}
        list_data.append(data_small)
    return JsonResponse(list_data, safe=False)

@csrf_exempt
def save_attendance_data(request):
    try:
        # Get data from the request
        # Accept either student_ids[] (array) or student_ids (array)
        student_ids = request.POST.getlist("student_ids[]") or request.POST.getlist("student_ids") or []
        subject_id = request.POST.get("subject_id")
        session_year_id = request.POST.get("session_year_id")
        attendance_date_str = request.POST.get("attendance_date")  # expected format YYYY-MM-DD

        print(f"DEBUG: POST data = {request.POST}")
        print(f"DEBUG: student_ids = {student_ids}")
        print(f"DEBUG: subject_id = {subject_id}")
        print(f"DEBUG: session_year_id = {session_year_id}")
        print(f"DEBUG: attendance_date_str = {attendance_date_str}")

        # Validate required fields (student_ids may be empty if everyone is absent)
        if not subject_id or not session_year_id or not attendance_date_str:
            error_msg = (
                f"Missing fields: subject_id={bool(subject_id)}, session_year_id={bool(session_year_id)}, attendance_date={bool(attendance_date_str)}"
            )
            print(f"DEBUG: {error_msg}")
            return JsonResponse({"error": error_msg}, status=400)

        # Parse attendance date (date-only)
        try:
            att_date = datetime.strptime(attendance_date_str, "%Y-%m-%d").date()
        except Exception:
            att_date = datetime.now().date()

        # Get models from database
        subject_model = Subjects.objects.get(id=subject_id)
        session_model = SessionYearModel.objects.get(id=session_year_id)

        # Create Attendance record (store date provided by user)
        attendance = Attendance(
            subject_id=subject_model,
            attendance_date=att_date,
            session_year_id=session_model
        )
        attendance.save()

        # Build set of present student admin ids (strings)
        present_ids = set([str(s) for s in student_ids])

        # Fetch all students for this subject's course and the session year
        students_qs = Students.objects.filter(course_id=subject_model.course_id, session_year_id=session_model)

        # Create AttendanceReport for each student (True if present, False if absent)
        for student in students_qs:
            stud_admin_id_str = str(student.admin.id)
            status = stud_admin_id_str in present_ids
            # Avoid duplicate AttendanceReport if one already exists for the same attendance and student
            report, created = AttendanceReport.objects.get_or_create(
                student_id=student,
                attendance_id=attendance,
                defaults={"status": status}
            )
            if not created:
                # If it exists (unlikely for new attendance), update status
                report.status = status
                report.save()

        return JsonResponse({"success": "Attendance saved successfully"})

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Exception = {str(e)}")
        print(f"DEBUG: Traceback = {error_trace}")
        return JsonResponse({"error": str(e)}, status=500)


def staff_update_attendance(request):
    subjects=Subjects.objects.filter(staff_id=request.user.id)
    session_year_id=SessionYearModel.objects.all()
    return render(request,"staff_template/staff_update_attendance.html",{"subjects":subjects,"session_year_id":session_year_id})

@csrf_exempt
def get_attendance_dates(request):
    subject=request.POST.get("subject")
    session_year_id=request.POST.get("session_year_id")
    subject_obj=Subjects.objects.get(id=subject)
    session_year_obj=SessionYearModel.objects.get(id=session_year_id)
    attendance=Attendance.objects.filter(subject_id=subject_obj,session_year_id=session_year_obj)
    attendance_obj=[]
    for attendance_single in attendance:
        data={"id":attendance_single.id,"attendance_date":str(attendance_single.attendance_date),"session_year_id":attendance_single.session_year_id.id}
        attendance_obj.append(data)

    return JsonResponse(json.dumps(attendance_obj),safe=False)


@csrf_exempt
def get_attendance_student(request):
    attendance_date=request.POST.get("attendance_date")
    attendance=Attendance.objects.get(id=attendance_date)

    attendance_data=AttendanceReport.objects.filter(attendance_id=attendance)
    list_data=[]

    for student in attendance_data:
        data_small={"id":student.student_id.admin.id,"name":student.student_id.admin.first_name+" "+student.student_id.admin.last_name,"status":student.status}
        list_data.append(data_small)
    return JsonResponse(list_data, safe=False)

@csrf_exempt
def save_updateattendance_data(request):
    try:
        # student_ids[] contains the ids of students marked present
        student_ids = request.POST.getlist("student_ids[]")
        attendance_id = request.POST.get("attendance_date")

        if not attendance_id:
            return JsonResponse({"error": "Missing attendance id"}, status=400)

        # Validate attendance exists
        attendance = Attendance.objects.get(id=attendance_id)

        # Fetch all attendance reports for this attendance
        attendance_reports = AttendanceReport.objects.filter(attendance_id=attendance)

        # Convert student_ids to set of strings for quick membership test
        present_ids = set(student_ids)

        for report in attendance_reports:
            # report.student_id is a Students instance; its admin.id is the user id
            student_admin_id = str(report.student_id.admin.id)
            report.status = True if student_admin_id in present_ids else False
            report.save()

        return JsonResponse({"status": "OK", "message": "Attendance updated successfully"})

    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"DEBUG: Exception = {str(e)}")
        print(f"DEBUG: Traceback = {error_trace}")
        return JsonResponse({"error": str(e)}, status=500)


def staff_apply_leave(request):
    staff_obj=Staffs.objects.get(admin=request.user.id)
    leave_data=LeaveReportStaff.objects.filter(staff_id=staff_obj)
    return render(request,"staff_template/staff_apply_leave.html",{"leave_data":leave_data})

def staff_apply_leave_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_apply_leave"))
    else:
        leave_date=request.POST.get("leave_date")
        leave_msg=request.POST.get("leave_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            leave_report=LeaveReportStaff(staff_id=staff_obj,leave_date=leave_date,leave_message=leave_msg,leave_status=0)
            leave_report.save()
            messages.success(request, "Successfully Applied For Leave")
            return HttpResponseRedirect(reverse("staff_apply_leave"))
        except Exception as e:
            messages.error(request, f"Failed To Apply For Leave: {str(e)}")
            return HttpResponseRedirect(reverse("staff_apply_leave"))


def staff_feedback(request):
    staff_id=Staffs.objects.get(admin=request.user.id)
    feedback_data=FeedBackStaffs.objects.filter(staff_id=staff_id)
    return render(request,"staff_template/staff_feedback.html",{"feedback_data":feedback_data})


def staff_feedback_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_feedback_save"))
    else:
        feedback_msg=request.POST.get("feedback_msg")

        staff_obj=Staffs.objects.get(admin=request.user.id)
        try:
            feedback=FeedBackStaffs(staff_id=staff_obj,feedback=feedback_msg,)
            feedback.save()
            messages.success(request, "Successfully Sent Feedback")
            return HttpResponseRedirect(reverse("staff_feedback"))
        except Exception as e:
            messages.error(request, f"Failed To Send Feedback: {str(e)}")
            return HttpResponseRedirect(reverse("staff_feedback"))


def staff_profile(request):
    user=CustomUser.objects.get(id=request.user.id)
    staff=Staffs.objects.get(admin=user)
    return render(request,"staff_template/staff_profile.html",{"user":user,"staff":staff})

def staff_profile_save(request):
    if request.method!="POST":
        return HttpResponseRedirect(reverse("staff_profile"))
    else:
        first_name=request.POST.get("first_name")
        last_name=request.POST.get("last_name")
        address=request.POST.get("address")
        password=request.POST.get("password")
        try:
            customuser=CustomUser.objects.get(id=request.user.id)
            customuser.first_name=first_name
            customuser.last_name=last_name
            if password!=None and password!="":
                customuser.set_password(password)
            customuser.save()

            staff=Staffs.objects.get(admin=customuser.id)
            staff.address=address
            staff.save()
            messages.success(request,"Successfully Updated Profile")
            return HttpResponseRedirect(reverse("staff_profile"))
        except:
            messages.error(request,"Failed to Update Profile")
            return HttpResponseRedirect(reverse("staff_profile"))