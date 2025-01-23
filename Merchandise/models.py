from django.db import models
from users.models import *

# Create your models here.

class Order(models.Model):
    userId = models.CharField(max_length=100)
    quantity = models.IntegerField()
    details = models.JSONField()
    lot = models.IntegerField(null=True, blank=True)
    orderId = models.CharField(max_length=100, null=True, blank=True)
    paymentId = models.CharField(max_length=100, null=True, blank=True)
    paymentReceived = models.BooleanField(default=False)
    orderDate = models.DateTimeField(auto_now_add=True)
    paymentProof = models.ImageField(upload_to='merchandise', null=True, blank=True)

    def __str__(self):
        if self.paymentReceived:
            return f"{self.lot} | {self.userId} | Count = {self.quantity}"
        return f"{self.userId}"