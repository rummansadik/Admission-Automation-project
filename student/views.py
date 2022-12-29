from datetime import datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.http.response import StreamingHttpResponse
from django.shortcuts import redirect, render
from exam import models as QMODEL
from student import train_image

from student.train_dataset import *
from student.train_camera import TrainCamera
from student.video_camera import VideoCamera
from student.train_image import *

from . import forms, models


def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'student/studentclick.html')


def student_signup_view(request): 
    userForm = forms.StudentUserForm() 
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            student = studentForm.save(commit=False)
            student.user = user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
            encode_image(student.profile_pic.path)        
        else:
            print('form not valid')
        return HttpResponseRedirect('studentlogin')
    return render(request, 'student/studentsignup.html', context=mydict)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def get_student(user):
    return models.Student.objects.get(user_id=user.pk)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    current_student = get_student(request.user)
    dict = {
        'student': current_student,
        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
    }
    return render(request, 'student/student_dashboard.html', context=dict)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    time = datetime.now()
    student = models.Student.objects.get(user_id=request.user.id)
    courses = QMODEL.Course.objects.all()
    expels = QMODEL.Expel.objects.filter(student=student)

    # course, time, is_expel
    course_list = []
    for course in courses:
        if(expels.filter(course=course.id).count()):
            course_list.append((course, 0, 1))
        elif course.end_at() < time:
            course_list.append((course, -1, 0))
        elif course.start_at() > time:
            course_list.append((course, 1, 0))
        else:
            course_list.append((course, 0, 0))

    course_list.reverse()
    context = {
        'courses': course_list,
    }

    return render(request, 'student/student_exam.html', context)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.all().filter(course=course)
    shorts = QMODEL.ShortQuestion.objects.all().filter(course=course)

    total_marks = 0
    total_questions = 0
    for q in questions:
        total_questions += 1
        total_marks += q.marks

    for q in shorts:
        total_questions += 1
        total_marks += q.marks

    context = {
        'course': course,
        'total_questions': total_questions,
        'total_marks': total_marks
    }

    return render(request, 'student/take_exam.html', context)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.all().filter(course=course)
    shorts = QMODEL.ShortQuestion.objects.all().filter(course=course)

    if request.method == 'POST':
        pass

    time_remain = course.end_at() - datetime.now()
    time_remain = time_remain.total_seconds()

    timer = int(time_remain)
    time_remain = time_remain * 1000
    time_remain = int(time_remain)

    context = {
        'course': course,
        'questions': questions,
        'shorts': shorts,
        'time_remain': time_remain,
        'timer': timer,
    }

    response = render(request, 'student/start_exam.html', context=context)
    response.set_cookie('course_id', course.id)
    return response


def get_answer_value(question, ans):
    if ans == 'Option1':
        return question.option1
    elif ans == 'Option2':
        return question.option2
    elif ans == 'Option3':
        return question.option3
    elif ans == 'Option4':
        return question.option4
    return ''


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):

    if request.COOKIES.get('course_id') is None:
        return HttpResponseRedirect('student-exam')

    course_id = request.COOKIES.get('course_id')
    course = QMODEL.Course.objects.get(id=course_id)

    shorts = QMODEL.ShortQuestion.objects.all().filter(course=course)
    questions = QMODEL.Question.objects.all().filter(course=course)
    student = models.Student.objects.get(user_id=request.user.id)

    mcq_marks = []
    mcq_answer = []
    for i in range(len(questions)):
        selected_ans = request.COOKIES.get(str(i+1), None)
        actual_answer = questions[i].answer

        mcq_answer.append(get_answer_value(questions[i], selected_ans))
        if selected_ans == actual_answer:
            mcq_marks.append(str(questions[i].marks))
        else:
            mcq_marks.append('0')

    shorts_answer = []
    for i in range(len(shorts)):
        name = 'question' + str(i+1)
        answer = request.POST.get(name, '')
        shorts_answer.append(answer)

    answerSheet = QMODEL.AnswerSheet()
    answerSheet.student = student
    answerSheet.course = course
    answerSheet.set_mcq_answer(mcq_answer)
    answerSheet.set_mcq_marks(mcq_marks)
    answerSheet.set_shorts_answer(shorts_answer)
    answerSheet.unfocus = request.POST.get('unfocus', 0)
    answerSheet.save()

    return HttpResponseRedirect('view-result')


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/view_result.html', {'courses': courses})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results = QMODEL.Result.objects.all().filter(
        exam=course).filter(student=student)
    results = results[::-1]
    return render(request, 'student/check_marks.html', {'results': results})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_expel_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    expel = QMODEL.Expel(course=course, student=student)
    expel.save()
    return render(request, 'student/expel.html', {})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/student_marks.html', {'courses': courses})


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def video_feed(request):
    return StreamingHttpResponse(
        gen(VideoCamera(get_student(request.user))),
        content_type='multipart/x-mixed-replace; boundary=frame')


def train_feed(request):
    values = gen(TrainCamera(get_student(request.user)))
    return StreamingHttpResponse(values,
                                 content_type='multipart/x-mixed-replace; boundary=frame')
