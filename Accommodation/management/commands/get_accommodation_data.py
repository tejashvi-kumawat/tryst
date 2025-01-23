from django.core.management.base import BaseCommand
from Accommodation.models import Accommodation
from users.models import Profile


class Command(BaseCommand):
    help = "Export data of people who have successfully booked accommodation"

    def handle(self, *args, **options):
        data = []
        accomodations = Accommodation.objects.all()
        for accomodation in accomodations:
            if accomodation.paymentReceived == False:
                continue
            curr = {}
            curr["UID"] = accomodation.bookedBy
            profile = Profile.objects.get(user_ID=accomodation.bookedBy)
            curr["name"] = profile.name
            curr["email"] = profile.email_ID
            curr["phone"] = profile.phone_Number
            data.append(curr)

        with open("accommodation_data.csv", "w") as file:
            file.write("Name, UID, Email, Phone\n")
            for curr in data:
                file.write(
                    f"{curr['name']}, {curr['UID']}, {curr['email']}, {curr['phone']}\n"
                )
