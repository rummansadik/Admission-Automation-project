import json
from datetime import datetime

from django.db import models
from multiselectfield import MultiSelectField
from student.models import Student
from teacher.models import Teacher

subject_choices = (
    ('CSE', 'CSE'),
    ('ECE', 'ECE'),
    ('EEE', 'EEE'),
    ('BBA', 'BBA'),
    ('English', 'English'),
    ('Math', 'Math'),
    ('Bangla', 'Bangla'),
)


class University(models.Model):
    university_name = models.CharField(max_length=100)
    subjects = MultiSelectField(
        max_length=100,
        max_choices=7,
        choices=subject_choices
    )


class Course(models.Model):

    course_types = [
        ('Strict', 'Strict'),
        ('Warning', 'Warning'),
        ('Notify', 'Notify'),
        ('Open Book', 'Open Book'),
        ('Capture', 'Capture'),
        ('Record', 'Record'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=50)
    course_type = models.CharField(
        max_length=50,
        choices=course_types,
        default='Strict'
    )

    total_students = models.PositiveIntegerField(default=0)
    question_number = models.PositiveIntegerField(default=0)
    total_marks = models.PositiveIntegerField(default=0)

    start_date = models.DateField()
    start_time = models.TimeField()

    end_date = models.DateField()
    end_time = models.TimeField()

    def start_at(self):
        return datetime.combine(self.start_date, self.start_time)

    def end_at(self):
        return datetime.combine(self.end_date, self.end_time)

    def __str__(self):
        return self.course_name


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=600)
    option1 = models.CharField(max_length=200)
    option2 = models.CharField(max_length=200)
    option3 = models.CharField(max_length=200)
    option4 = models.CharField(max_length=200)
    cat = (
        ('Option1', 'Option1'),
        ('Option2', 'Option2'),
        ('Option3', 'Option3'),
        ('Option4', 'Option4')
    )
    answer = models.CharField(max_length=200, choices=cat)


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    exam = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField()

    status_choices = [
        ('Unknown', 'Unknown'),
        ('Attended', 'Attended'),
        ('Expelled', 'Expelled'),
    ]

    status = models.CharField(
        max_length=20, 
        choices=status_choices,
        default='Unknown'
    )

    def save(self, *args, **kwargs):
        self.date = datetime.now()
        super(Result, self).save(*args, **kwargs)


class ShortQuestion(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    question = models.CharField(max_length=2000)


class AnswerSheet(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    mcqAnswer = models.CharField(max_length=200, blank=True)
    mcqMarks = models.CharField(max_length=200, blank=True)
    shortsAnswer = models.CharField(max_length=2000, blank=True)
    is_evaluated = models.BooleanField(default=False)
    unfocus = models.IntegerField(default=0)

    def set_mcq_answer(self, answer):
        self.mcqAnswer = json.dumps(answer)

    def get_mcq_answer(self):
        return json.loads(self.mcqAnswer)

    def set_mcq_marks(self, answer):
        self.mcqMarks = json.dumps(answer)

    def get_mcq_marks(self):
        return json.loads(self.mcqMarks)

    def set_shorts_answer(self, answer):
        self.shortsAnswer = json.dumps(answer)

    def get_shorts_answer(self):
        return json.loads(self.shortsAnswer)


class Expel(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
