from pyexpat import model
from django.contrib.auth.models import User
from django.db import models

def get_dir(self, filename):
    return f'profile_pic/Student/{self.user.id}_{filename}'

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=40)
    mobile = models.CharField(max_length=20, null=False)
    profile_pic = models.ImageField(
        upload_to=get_dir, blank=True, null=True)
    is_trained = models.BooleanField(default=False)

    @property
    def get_name(self):
        return self.user.first_name+" "+self.user.last_name

    @property
    def get_instance(self):
        return self

    def __str__(self):
        return self.user.first_name+" "+self.user.last_name
