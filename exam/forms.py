from django import forms

from . import models

subject_choices = (
    ('CSE', 'CSE'),
    ('ECE', 'ECE'),
    ('EEE', 'EEE'),
    ('BBA', 'BBA'),
    ('English', 'English'),
    ('Math', 'Math'),
    ('Bangla', 'Bangla'),
)


class UniversityForm(forms.Form):
    university_name = forms.CharField(max_length=100)
    subjects = forms.MultipleChoiceField(
        choices=subject_choices,
        widget=forms.CheckboxSelectMultiple()
    )


class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(
        max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))


class TeacherSalaryForm(forms.Form):
    salary = forms.IntegerField()


course_types = [
    ('Strict', 'Strict'),
    ('Warning', 'Warning'),
    ('Notify', 'Notify'),
    ('Open Book', 'Open Book'),
    ('Capture', 'Capture'),
    ('Record', 'Record'),
]


class CourseForm(forms.ModelForm):
    class Meta:
        model = models.Course
        fields = [
            'course_name',
            'course_type',
            'total_students',
            'question_number',
            'total_marks',
            'start_date',
            'start_time',
            'end_date',
            'end_time',
        ]
        widgets = {
            'start_date': forms.DateInput(format='%d/%m/%Y'),
            'start_time': forms.TimeInput(format='%H:%M'),
            'end_date': forms.DateInput(format='%d/%m/%Y'),
            'end_time': forms.TimeInput(format='%H:%M'),
            'course_type': forms.Select(attrs={'class': 'form-control col-sm-2'}),
        }


class QuestionForm(forms.ModelForm):

    # this will show dropdown __str__ method course model is shown on html so override it
    # to_field_name this will fetch corresponding value  user_id present in course model and return it
    courseID = forms.ModelChoiceField(
        queryset=models.Course.objects.all(),
        empty_label="Course Name",
        to_field_name="id"
    )

    class Meta:
        model = models.Question
        fields = ['marks', 'question', 'option1',
                  'option2', 'option3', 'option4', 'answer']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})
        }


class ShortQuestionForm(forms.ModelForm):

    # this will show dropdown __str__ method course model is shown on html so override it
    # to_field_name this will fetch corresponding value  user_id present in course model and return it
    courseID = forms.ModelChoiceField(
        queryset=models.Course.objects.all(),
        empty_label="Course Name",
        to_field_name="id"
    )

    class Meta:
        model = models.ShortQuestion
        fields = ['marks', 'question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }
