from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
import datetime
from quiz import models as QMODEL
from teacher import models as TMODEL


#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={

    'total_course':QMODEL.Course.objects.filter(status = True).count(),
    'total_question':QMODEL.Question.objects.filter(course__status = True).count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses=QMODEL.Course.objects.filter(status = True, start_date__lte = datetime.datetime.now(), end_date__gte = datetime.datetime.now())
    return render(request,'student/student_exam.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_update_view(request):
    student=models.Student.objects.get(user = request.user)
    user=models.User.objects.get(id=student.user_id)
    userForm=forms.StudentUserForm(instance=user)
    studentForm=forms.StudentForm(request.FILES,instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST,instance=user)
        studentForm=forms.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            dict={
            'total_course':QMODEL.Course.objects.filter(status = True).count(),
            'total_question':QMODEL.Question.objects.filter(course__status = True).count(),
            }
            return render(request,'student/student_dashboard.html',context=dict)
    return render(request,'student/student_update.html',context=mydict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    #for q in questions:
        #total_marks=total_marks + q.marks

    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        pass
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is not None:
        course_id = request.COOKIES.get('course_id')
        course=QMODEL.Course.objects.get(id=course_id)

        #total_marks=0
        questions=QMODEL.Question.objects.all().filter(course=course)
        for i in range(len(questions)):

            selected_ans = request.COOKIES.get(str(i+1))
            print(selected_ans)
            print(questions[i].option1)
            print(questions[i].option2)
            print(questions[i].option3)
            print(questions[i].option4)
            #actual_answer = questions[i].answer
            if selected_ans == "Option1":
                questions[i].option1_count += 1
                print("ENTERED 1")
                print(questions[i].option1)
                print(questions[i].option1_count)
            elif selected_ans == "Option2":
                print("ENTERED 2")
                questions[i].option2_count += 1
                print(questions[i].option2)
                print(questions[i].option2_count)
            elif selected_ans == "Option3":
                print("ENTERED 3")
                questions[i].option3_count += 1
            elif selected_ans == "Option4":
                print("ENTERED 4")
                questions[i].option4_count += 1
            else:
                redirect('student-dashboard')

            questions[i].save()
            print(questions[i])

        return HttpResponseRedirect('view-result')



@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses=QMODEL.Course.objects.filter(status = True)
    return render(request,'student/view_result.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course_pre=QMODEL.Course.objects.get(id=pk)
    print(course_pre)
    results= QMODEL.Question.objects.all().filter(course=course_pre)
    #print(results.course)
    return render(request,'student/check_marks.html',{'course_pre':course_pre,'results':results})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses=QMODEL.Course.objects.filter(status = True)
    return render(request,'student/student_marks.html',{'courses':courses})
