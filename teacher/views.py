from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from exam import forms as QFORM
from exam import models as QMODEL
from student import models as SMODEL
from teacher import models as TMODEL

from . import forms


def get_teacher(user):
    return TMODEL.Teacher.objects.get(user_id=user.pk)


def teacherclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'teacher/teacherclick.html')


def teacher_signup_view(request):
    userForm = forms.TeacherUserForm()
    teacherForm = forms.TeacherForm()
    mydict = {'userForm': userForm, 'teacherForm': teacherForm}
    if request.method == 'POST':
        userForm = forms.TeacherUserForm(request.POST)
        teacherForm = forms.TeacherForm(request.POST, request.FILES)
        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            teacher = teacherForm.save(commit=False)
            teacher.user = user
            teacher.save()
            my_teacher_group = Group.objects.get_or_create(name='TEACHER')
            my_teacher_group[0].user_set.add(user)
        return HttpResponseRedirect('teacherlogin')
    return render(request, 'teacher/teachersignup.html', context=mydict)


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    dict = {
        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
        'total_student': SMODEL.Student.objects.all().count(),
        'pending_student': QMODEL.AnswerSheet.objects.all().filter(is_evaluated=False).count()
    }

    return render(request, 'teacher/teacher_dashboard.html', context=dict)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_pending_students_view(request):

    teacher = get_teacher(request.user)
    pending = QMODEL.AnswerSheet.objects.filter(
        is_evaluated=False,
    )

    pending_for_current_teacher = []
    for answer in pending:
        if answer.course.teacher_id == teacher.pk:
            pending_for_current_teacher.append(answer)
    
    context = {
        'pending_students': pending_for_current_teacher
    }

    return render(request, 'teacher/pending_students.html', context=context)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_pending_student_answer_view(request, pk):

    answerSheet = QMODEL.AnswerSheet.objects.get(id=pk)
    student = answerSheet.student
    course = answerSheet.course
    mcqQuestions = QMODEL.Question.objects.all().filter(course=course)
    mcqAnswers = answerSheet.get_mcq_answer()
    mcqMarks = answerSheet.get_mcq_marks()
    shortQuestions = QMODEL.ShortQuestion.objects.all().filter(course=course)
    shortAnswers = answerSheet.get_shorts_answer()

    mcq = []
    for q, a, m in zip(mcqQuestions, mcqAnswers, mcqMarks):
        mcq.append((q.question, a, m, q.marks))

    # print(mcq)

    shorts = []
    for q, a in zip(shortQuestions, shortAnswers):
        shorts.append((q.question, a, q.marks))

    # print(shorts)

    context = {
        'student': student,
        'course': course,
        'mcq': mcq,
        'mcq_len': str(len(mcq)),
        'shorts': shorts,
        'unfocus': str(answerSheet.unfocus),
    }

    if request.method == 'POST':

        if 'submit_marks' in request.POST:
            marks = 0
            for i in range(len(mcq) + len(shorts)):
                name = 'mark' + str(i+1)
                marks += int(request.POST.get(name, '0'))

            result = QMODEL.Result()
            result.student = student
            result.exam = course
            result.marks = marks
            result.save()

            QMODEL.AnswerSheet.objects.filter(id=pk).update(
                is_evaluated=True
            )

        elif 'expel' in request.POST:
            marks = 0
            result = QMODEL.Result()
            result.student = student
            result.exam = course
            result.marks = marks
            result.status = 'Expelled'
            result.save()

            expel = QMODEL.Expel.objects.create(course=course, student=student)
            expel.save()

            QMODEL.AnswerSheet.objects.filter(id=pk).update(
                is_evaluated=True
            )

        return HttpResponseRedirect('/teacher/pending-students')

    return render(request, 'teacher/pending_student_answer.html', context=context)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_exam_view(request):
    return render(request, 'teacher/teacher_exam.html')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_exam_view(request):
    courseForm = QFORM.CourseForm()
    if request.method == 'POST':
        courseForm = QFORM.CourseForm(request.POST)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.teacher = get_teacher(request.user)
            course.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/teacher/teacher-view-exam')
    return render(request, 'teacher/teacher_add_exam.html', {'courseForm': courseForm})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_exam_view(request):
    teacher = get_teacher(request.user)
    courses = QMODEL.Course.objects.filter(teacher_id=teacher.pk)
    return render(request, 'teacher/teacher_view_exam.html', {'courses': courses})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def delete_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/teacher/teacher-view-exam')


@login_required(login_url='adminlogin')
def teacher_question_view(request):
    return render(request, 'teacher/teacher_question.html')


def solve_for_question_form(request, questionForm):
    questionForm = QFORM.QuestionForm(request.POST)
    if questionForm.is_valid():
        question = questionForm.save(commit=False)
        course = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
        question.course = course
        question.save()
        messages.success(request, "Question Added")
        print(questionForm.cleaned_data)
    else:
        print("mcq form is invalid")
    return HttpResponseRedirect('/teacher/teacher-add-question')


def solve_for_short_form(request, shortQuestionForm):
    shortQuestionForm = QFORM.ShortQuestionForm(request.POST)
    if shortQuestionForm.is_valid():
        question = shortQuestionForm.save(commit=False)
        course = QMODEL.Course.objects.get(id=request.POST.get('courseID'))
        question.course = course
        question.save()
        messages.success(request, "Question Added")
        print(shortQuestionForm.cleaned_data)
    else:
        print("short form is invalid")
    return HttpResponseRedirect('/teacher/teacher-add-question')


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_add_question_view(request):
    questionForm = QFORM.QuestionForm()
    shortQuestionForm = QFORM.ShortQuestionForm()
    if request.method == 'POST':
        if 'add_mcq' in request.POST:
            solve_for_question_form(request, questionForm)
        elif 'add_short' in request.POST:
            solve_for_short_form(request, shortQuestionForm)

    context = {
        'questionForm': questionForm,
        'shortQuestionForm': shortQuestionForm,
    }

    return render(request, 'teacher/teacher_add_question.html', context)


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def teacher_view_question_view(request):
    teacher = get_teacher(request.user)
    courses = QMODEL.Course.objects.filter(teacher_id=teacher.pk)
    return render(request, 'teacher/teacher_view_question.html', {'courses': courses})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def see_question_view(request, pk):
    questions = QMODEL.Question.objects.all().filter(course_id=pk)
    return render(request, 'teacher/see_question.html', {'questions': questions})


@login_required(login_url='teacherlogin')
@user_passes_test(is_teacher)
def remove_question_view(request, pk):
    question = QMODEL.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect(reverse('teacher-view-question'))
