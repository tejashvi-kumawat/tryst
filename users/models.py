from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class College(models.Model):
    college_ID = models.CharField(max_length=100)
    name = models.CharField(max_length=1000)
    city = models.CharField(max_length=1000)
    state = models.CharField(max_length=1000)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user_ID = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    phone_Number = models.CharField(max_length=15)
    email_ID = models.EmailField(max_length=255, unique=True)
    college_ID = models.CharField(max_length=100)
    instagram_id = models.CharField(max_length=100, blank=True)
    facebook_Link = models.URLField(max_length=255, blank=True)
    linkedIn_Link = models.URLField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='profile_pics', blank=True)
    category = models.CharField(max_length=100, default='general')
    accomodation = models.BooleanField(default=False)

    def __str__(self):
        return self.user_ID


class Pac(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    category = models.CharField(
        max_length=100, default='High school', blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)
    teamName = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name + " - " + self.phone + " - " + self.teamName
