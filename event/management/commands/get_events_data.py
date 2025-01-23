from django.core.management.base import BaseCommand
from event.models import Event


class Command(BaseCommand):
    help = "Export data of venue of all events"

    def handle(self, *args, **options):
        data = []
        events = Event.objects.all()
        for event in events:
            curr = {}
            curr["Event Date"] = event.event_date
            curr["Event Name"] = event.title
            curr["Venue"] = event.venue
            data.append(curr)

        data = sorted(data, key=lambda x: x["Event Date"])
        with open("event_data.csv", "w") as file:
            file.write("S.No, Event Date, Event Name, Venue\n")
            for i, event in enumerate(data):
                file.write(f"{i+1}, {event['Event Date']}, {event['Event Name']}, {event['Venue']}\n")