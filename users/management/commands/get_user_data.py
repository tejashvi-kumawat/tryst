from django.core.management.base import BaseCommand
from users.models import Profile

class Command(BaseCommand):
    help = "Export data of all users"

    def handle(self, *args, **options):
        data = []
        users = Profile.objects.all()

        for user in users:
            if user.category == 'general':
                curr = {}
                curr["UID"] = user.user_ID
                curr["Name"] = user.name
                curr["Email"] = user.email_ID
                data.append(curr)

        with open("user_data.csv", "w", encoding="utf-8") as file:
            file.write("S.No, UID, Name, Email\n")
            for i, user in enumerate(data):
                file.write(f"{i+1}, {user['UID']}, {user['Name']}, {user['Email']}\n")