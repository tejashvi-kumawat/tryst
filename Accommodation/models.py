from django.db import models

# Create your models here.


class Accommodation(models.Model):
    bookedBy = models.CharField(max_length=100)
    checkInDate = models.DateField()
    checkOutDate = models.DateField()
    amount = models.IntegerField(null=True, blank=True)
    men = models.IntegerField()
    women = models.IntegerField()
    memberDetails = models.JSONField()
    orderId = models.CharField(max_length=100, null=True, blank=True)
    paymentId = models.CharField(max_length=100, null=True, blank=True)
    paymentReceived = models.BooleanField(default=False)

    def __str__(self):
        if self.paymentReceived:
            return self.bookedBy + " (Paid)"
        return self.bookedBy


class Variable(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.name
