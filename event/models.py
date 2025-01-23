from django.db import models
from users.models import Profile


# Event Models


class Club(models.Model):
    club_id = models.IntegerField(primary_key=True)
    club_name = models.CharField(max_length=100)

    def __str__(self):
        return self.club_name + " - " + str(self.club_id)

class Event(models.Model):
    spreadsheet_id = models.CharField(max_length=100, null=True, blank=True)
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    venue = models.CharField(max_length=100)
    event_image = models.ImageField(upload_to="event_images", blank=True, null=True)
    deadline_date = models.DateField(null=True, blank=True)
    deadline_time = models.TimeField(null=True, blank=True)
    rulebook = models.TextField(null=True, blank=True)
    has_form = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, null=True)
    clubs = models.JSONField(null=True, blank=True, default=dict)

    def __str__(self):
        return self.title


class Contact_Event(models.Model):
    contact = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="contact")
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# Workshop Models


class Workshop(models.Model):
    spreadsheet_id = models.CharField(max_length=100, null=True, blank=True)
    workshop_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    event_date = models.DateField()
    event_time = models.TimeField()
    venue = models.CharField(max_length=100)
    event_image = models.ImageField(upload_to="workshop_images", blank=True, null=True)
    deadline_date = models.DateField(null=True, blank=True)
    deadline_time = models.TimeField(null=True, blank=True)
    rulebook = models.TextField(null=True, blank=True)
    has_form = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, null=True)
    clubs = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.title


class Contact_Workshop(models.Model):
    contact = models.ForeignKey(
        Workshop, on_delete=models.CASCADE, related_name="contact"
    )
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


# Guest Models


class Guest(models.Model):
    spreadsheet_id = models.CharField(max_length=100, null=True, blank=True)
    guest_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField()
    event_time = models.TimeField()
    event_date = models.DateField()
    venue = models.CharField(max_length=100)
    event_image = models.ImageField(upload_to="guest_images", blank=True, null=True)
    has_form = models.BooleanField(default=False)
    registration_link = models.URLField(blank=True, null=True)
    deadline_date = models.DateField(null=True, blank=True)
    deadline_time = models.TimeField(null=True, blank=True)
    clubs = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - ID: {self.guest_id}"


class Contact_Guest(models.Model):
    contact = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="contact")
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Speaker(models.Model):
    speaker = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name="speaker")
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="speaker", blank=True, null=True)

    def __str__(self):
        return self.name


class Registration(models.Model):
    eventtype = models.CharField(max_length=100, blank=True, null=True)
    event_id = models.IntegerField(blank=True, null=True, default=1)
    formFields = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.eventtype} - ID: {self.event_id}"


class UserRegistration(models.Model):
    user = models.CharField(max_length=100, blank=True, null=True)
    event_type = models.CharField(max_length=100, blank=True, null=True)
    event_id = models.IntegerField(blank=True, null=True)
    form = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.event_type} - ID: {self.event_id}"
