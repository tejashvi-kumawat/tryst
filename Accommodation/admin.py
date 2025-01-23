from django.contrib import admin
from django.http import HttpResponse
from .models import Accommodation, Variable
from users.models import Profile
import csv

# Register your models here.

class AccommodationAdmin(admin.ModelAdmin):
    list_display = ("bookedBy", "checkInDate", "checkOutDate", "paymentReceived")
    search_fields = ("bookedBy", "checkInDate", "checkOutDate", "paymentReceived")
    actions = ["download_accommodation_data"]

    def download_accommodation_data(self, request, queryset):
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="accomodation_data.csv"'

        writer = csv.writer(response)
        writer.writerow(
            [
                "Name",
                "UID",
                "Email",
                "Phone",
                "CheckInDate",
                "CheckOutDate",
                "Men",
                "Women",
                "Member Details",
                "Amount",
                "OrderId",
                "PaymentId",
            ]
        )

        for accomodation in queryset:
            if not accomodation.paymentReceived:
                continue
            profile = Profile.objects.get(user_ID=accomodation.bookedBy)
            writer.writerow([
                profile.name,
                accomodation.bookedBy,
                profile.email_ID,
                profile.phone_Number,
                accomodation.checkInDate,
                accomodation.checkOutDate,
                accomodation.men,
                accomodation.women,
                accomodation.memberDetails,
                accomodation.amount,
                accomodation.orderId,
                accomodation.paymentId,
            ])

        return response

    download_accommodation_data.short_description = "Download Accomodation Data"

class VariableAdmin(admin.ModelAdmin):
    list_display = ("name", "value")
    search_fields = ("name", "value")


admin.site.register(Accommodation, AccommodationAdmin)
admin.site.register(Variable, VariableAdmin)
