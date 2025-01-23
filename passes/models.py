from django.db import models
from django.contrib.auth.models import User
from users.models import Profile
import datetime
import uuid



class Pronite(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Slot(models.Model):
    proniteId = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.proniteId} | Slot {self.id}"


class Pass(models.Model):
    userId = models.CharField(max_length=100)
    slotId = models.CharField(max_length=100)
    code = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    entry = models.BooleanField(default=False)
    entryTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.userId}"


class Wize(models.Model):
    emailId = models.CharField(max_length=100)
    qrId = models.CharField(max_length=100)
    eventId = models.CharField(max_length=100)

# Create your models here.

class TeamPass(models.Model):
    teamId = models.CharField(max_length=100)
    slotId = models.CharField(max_length=100)
    code = models.UUIDField(default=uuid.uuid4, editable=True, unique=True)
    entry = models.BooleanField(default=True)
    entryTime = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.teamId}"
