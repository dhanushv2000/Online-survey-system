from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from student import models as SMODEL
from quiz import forms as QFORM
from django.contrib.auth.forms import UserCreationForm
from quiz.function import render_to_pdf
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.views.generic import ListView, FormView, View, DeleteView
from django.conf import settings
from django.core.mail import send_mail

#for showing signup/login button for teacher
def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'teacher/teacherclick.html')

def teacher_signup_view(request):
    userForm=forms.TeacherUserForm()
    teacherForm=forms.TeacherForm()
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST)
        teacherForm=forms.TeacherForm(request.POST,request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacher=teacherForm.save(commit=False)
            teacher.user=user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request,'teacher/teachersignup.html',context=mydict)



def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict={

    'total_course':QMODEL.Course.objects.filter(status = True,user = request.user).count(),
    'total_question':QMODEL.Question.objects.filter(course__status = True,course__user = request.user).count(),
    'total_student':SMODEL.Student.objects.all().count(),
    'total_pending_course':QMODEL.Course.objects.filter(status=False,user = request.user).count(),
    }
    return render(request,'teacher/teacher_dashboard.html',context=dict)

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request,'teacher/teacher_exam.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_update_view(request):

    teacher=models.Teacher.objects.get(user = request.user)
    print(teacher)
    user=models.User.objects.get(id=teacher.user_id)
    userForm=forms.TeacherUserForm(instance=user)
    teacherForm=forms.TeacherForm(request.FILES,instance=teacher)
    mydict={'userForm':userForm,'teacherForm':teacherForm}
    if request.method=='POST':
        userForm=forms.TeacherUserForm(request.POST,instance=user)
        teacherForm=forms.TeacherForm(request.POST,request.FILES,instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            dict={

            'total_course':QMODEL.Course.objects.filter(user=request.user,status=True).count(),
            'total_question':QMODEL.Question.objects.filter(course__user=request.user,course__status = True).count(),
            'total_student':SMODEL.Student.objects.all().count(),
            'total_pending_course':QMODEL.Course.objects.filter(user=request.user,status=True).count(),
            }
            return render(request,'teacher/teacher_dashboard.html',context=dict)
    return render(request,'teacher/teacher_update.html',context=mydict)

@login_required(login_url = 'teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_pending_survey_view(request):
    survey= QMODEL.Course.objects.filter(status=False,user = request.user)
    return render(request,'teacher/teacher_view_pending_survey.html',{'survey':survey})


@login_required(login_url = 'teacherlogin')
@user_passes_test(is_teacher)
def teacher_reject_survey_view(request,pk):
    sur=QMODEL.Course.objects.get(id=pk)
    sur.delete()
    survey=QMODEL.Course.objects.all().filter(status=False,user = request.user)
    return render(request,'teacher/teacher_view_pending_survey.html',{'survey':survey})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm=QFORM.CourseForm()
    if request.method=='POST':
        courseForm=QFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            form = courseForm.save(commit = False)
            form.user = request.user
            form.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request,'teacher/teacher_add_exam.html',{'courseForm':courseForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    courses = QMODEL.Course.objects.filter(status=True,user = request.user)
    return render(request,'teacher/teacher_view_exam.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')

@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request,'teacher/teacher_question.html')

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm=QFORM.QuestionForm()
    if request.method=='POST':
        questionForm=QFORM.QuestionForm(request.POST)
        if questionForm.is_valid():
            question=questionForm.save(commit=False)
            course=QMODEL.Course.objects.get(id=request.POST.get('courseID'))
            question.course=course
            question.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-question')
    return render(request,'teacher/teacher_add_question.html',{'questionForm':questionForm})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    courses= QMODEL.Course.objects.filter(user=request.user,status=True)
    return render(request,'teacher/teacher_view_question.html',{'courses':courses})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request,pk):
    questions=QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request,'teacher/see_question.html',{'questions':questions})

@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request,pk):
    question=QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/teacher/teacher-view-question')


@login_required(login_url='teacherlogin')
def teacher_check_marks_view(request,pk):
    course_pre=QMODEL.Course.objects.get(id=pk)
    results= QMODEL.Question.objects.all().filter(course=course_pre)
    return render(request,'teacher/teacher_check_marks.html',{'course_pre':course_pre,'results':results})

class teacher_view_result_pdf_view(View):
    def get(self, request, *args, **kwargs):
        courses = QMODEL.Course.objects.get(id = kwargs['pk'])
        result = QMODEL.Question.objects.all().filter(course = courses)
        pdf = render_to_pdf('teacher/teacher_view_Pdf_Page.html', {'result':result, 'courses':courses})
        return HttpResponse(pdf, content_type='application/pdf')

@login_required(login_url='teacherlogin')
def teacher_notify_survey_view(request,pk):
    course_pre=QMODEL.Course.objects.get(id=pk)
    user_emails = SMODEL.Student.objects.values_list('address',flat = True)
    emails = []
    for email in user_emails:
        emails.append(email)
        
    subject = "You Survey have a New Survey"
    message = f"Hi , We are glad to inform that the new {course_pre.course_name} survey will be available from {course_pre.start_date} and ends {course_pre.end_date}. This is an automated email address do not reply back."
    email_from  = settings.EMAIL_HOST_USER
    recipient_list = emails
    send_mail(subject,message,email_from,recipient_list)

    return redirect('teacher-view-exam')
