# views.py
import os
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from users.models import Profile, College
from .models import (
    Event,
    Workshop,
    Registration,
    Contact_Guest,
    Guest,
    Speaker,
    Contact_Event,
    UserRegistration,
    Contact_Workshop,
)
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build
import re
from .serializers import EventSerializer, WorkshopSerializer, GuestSerializer
from Admin.scripts import imgproc
import requests
from io import BytesIO


@api_view(["GET"])
def get_all_events(request):
    try:
        all_events = Event.objects.all()
        all_workshops = Workshop.objects.all()
        all_guests = Guest.objects.all()

        events_serializer = EventSerializer(all_events, many=True)
        workshops_serializer = WorkshopSerializer(all_workshops, many=True)
        guests_serializer = GuestSerializer(all_guests, many=True)
        response_data = {
            "competitions": events_serializer.data,
            "workshops": workshops_serializer.data,
            "guestlectures": guests_serializer.data,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {"error": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(["POST"])
def create_workshop(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = request.data
            try:
                title = data["title"]
                description = data["description"]
                event_date = data["event_date"]
                event_club = data["event_club"]
                event_time = data["event_time"]
                venue = data["venue"]
                if request.FILES.get("file"):
                    file = request.FILES.get("file")
                else:
                    file = data["file"]
                rulebook = data["ruleBook"]
                if "registration_link" in data:
                    registration_link = data["registration_link"]
                    if data["registration_link"] == "":
                        has_form = False
                    else:
                        has_form = True
                reg_date = data["reg_date"]
                reg_time = data["reg_time"]
                contacts_array = []
                pattern = re.compile(r"^contactPersons\[(\d+)\]\[(name|phone)\]$")
                for key, value in data.items():
                    match = pattern.match(key)
                    if match:
                        index, field = match.groups()
                        index = int(index)
                        while len(contacts_array) <= index:
                            contacts_array.append({})
                        contacts_array[index][field] = value
            except:
                return Response(
                    {"error": "Complete details are not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "editedform" in data:
                if "event_id" in data:
                    event_edited = Workshop.objects.get(workshop_id=data["event_id"])
                    event_edited.title = title
                    event_edited.description = description
                    event_edited.clubs = event_club
                    event_edited.event_date = event_date
                    event_edited.event_time = event_time
                    event_edited.venue = venue
                    if file:
                        file_data = None
                        # Set a default value for the original file name
                        original_file_name = "default_filename"

                        if isinstance(file, str) and (
                            file.startswith("http") or file.startswith("https")
                        ):
                            response = requests.get(file)
                            if response.status_code == 200:
                                image_data = response.content
                                file_data = BytesIO(image_data)
                                original_file_name = file.split("/")[-1]
                        else:
                            file_data = file
                            if hasattr(file, "name"):
                                original_file_name = file.name

                        if file_data:
                            compressed_image = imgproc.compress(
                                file_data, original_file_name
                            )
                            event.event_image = compressed_image

                    if data["has_form"] == "true":
                        event_edited.has_form = True
                    else:
                        event_edited.has_form = False
                    event_edited.rulebook = rulebook
                    event_edited.deadline_date = reg_date
                    event_edited.deadline_time = reg_time
                    event_edited.save()
                    Contact_Workshop.objects.filter(contact=event_edited).delete()
                    for contact in contacts_array:
                        Contact_Workshop.objects.create(
                            contact=event_edited,
                            name=contact["name"],
                            phone=contact["phone"],
                        )
                    if not event_edited.has_form:
                        try:
                            scope_gspread = [
                                "https://spreadsheets.google.com/feeds",
                                "https://www.googleapis.com/auth/drive",
                            ]
                            credentials_gspread = (
                                service_account.Credentials.from_service_account_file(
                                    os.path.abspath(
                                        "event/trystbackend-0d0f6831fb2b.json"
                                    ),
                                    scopes=scope_gspread,
                                )
                            )
                            gc = gspread.authorize(credentials_gspread)

                            spreadsheet = gc.open_by_key(event_edited.spreadsheet_id)

                            spreadsheet.update_title(event_edited.title)

                            return Response(
                                {"success": "Event updated successfully."},
                                status=status.HTTP_200_OK,
                            )
                        except Exception as e:
                            return Response(
                                {
                                    "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                                },
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )
                    return Response(
                        {"success": "Event updated successfully."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Event ID not provided."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            event = Workshop(
                title=title,
                description=description,
                event_date=event_date,
                clubs=event_club,
                event_time=event_time,
                event_image=imgproc.compress(file, file.name),
                venue=venue,
                rulebook=rulebook,
                has_form=has_form,
                registration_link=registration_link,
                deadline_date=reg_date,
                deadline_time=reg_time,
            )
            event.save()
            for contact in contacts_array:
                Contact_Workshop.objects.create(
                    contact=event, name=contact["name"], phone=contact["phone"]
                )
            if not has_form:
                try:
                    drive_folder_id = "1uYaKt5NhxfaYXRerf6e49zGycDoC-hcW"
                    scope_gspread = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive",
                    ]
                    credentials_gspread = (
                        service_account.Credentials.from_service_account_file(
                            os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                            scopes=scope_gspread,
                        )
                    )
                    gc = gspread.authorize(credentials_gspread)
                    spreadsheet = gc.create(event.title)
                    spreadsheet_id = spreadsheet.id

                    scope_drive = ["https://www.googleapis.com/auth/drive"]
                    credentials_drive = (
                        service_account.Credentials.from_service_account_file(
                            os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                            scopes=scope_drive,
                        )
                    )
                    drive_service = build("drive", "v3", credentials=credentials_drive)
                    existing_parents = (
                        drive_service.files()
                        .get(fileId=spreadsheet_id, fields="parents")
                        .execute()["parents"]
                    )
                    response = (
                        drive_service.files()
                        .update(
                            fileId=spreadsheet_id,
                            addParents=drive_folder_id,
                            removeParents="root",
                            supportsAllDrives=True,
                        )
                        .execute()
                    )
                    drive_service.permissions().create(
                        fileId=spreadsheet_id,
                        body={
                            "role": "writer",
                            "type": "user",
                            "emailAddress": "sheets.tryst2024@gmail.com",
                        },
                    ).execute()

                    event.spreadsheet_id = spreadsheet_id
                    event.save()

                    return Response(
                        {
                            "success": "Event created successfully. Spreadsheet created and uploaded to Google Drive.",
                            "event_id": event.workshop_id,
                        },
                        status=status.HTTP_201_CREATED,
                    )

                except Exception as e:
                    return Response(
                        {
                            "error": f"Error creating/uploading Google Spreadsheet: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(
                    {"success": "Event created successfully."},
                    status=status.HTTP_201_CREATED,
                )
        else:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST"])
def create_event(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = request.data
            print(data)
            try:
                title = data["title"]
                description = data["description"]
                event_club = data["event_club"]
                event_date = data["event_date"]
                event_time = data["event_time"]
                venue = data["venue"]
                if request.FILES.get("file"):
                    file = request.FILES.get("file")
                else:
                    file = data["file"]
                rulebook = data["ruleBook"]
                if "registration_link" in data:
                    registration_link = data["registration_link"]
                    if data["registration_link"] == "":
                        has_form = False
                    else:
                        has_form = True
                reg_date = data["reg_date"]
                reg_time = data["reg_time"]
                contacts_array = []
                pattern = re.compile(r"^contactPersons\[(\d+)\]\[(name|phone)\]$")
                for key, value in data.items():
                    match = pattern.match(key)
                    if match:
                        index, field = match.groups()
                        index = int(index)
                        while len(contacts_array) <= index:
                            contacts_array.append({})
                        contacts_array[index][field] = value

            except:
                return Response(
                    {"error": "Complete details are not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "editedform" in data:
                if "event_id" in data:
                    event_edited = Event.objects.get(event_id=data["event_id"])
                    event_edited.title = title
                    event_edited.description = description
                    event_edited.clubs = event_club
                    event_edited.event_date = event_date
                    event_edited.event_time = event_time
                    event_edited.venue = venue
                    if file:
                        file_data = None
                        # Set a default value for the original file name
                        original_file_name = "default_filename"

                        if isinstance(file, str) and file.startswith(("http", "https")):
                            response = requests.get(file)
                            if response.status_code == 200:
                                image_data = response.content
                                file_data = BytesIO(image_data)
                                original_file_name = file.split("/")[-1]
                        else:
                            file_data = file
                            if hasattr(file, "name"):
                                original_file_name = file.name
                        if file_data:
                            compressed_image = imgproc.compress(
                                file_data, original_file_name
                            )
                            event_edited.event_image = compressed_image

                    if data["has_form"] == "true":
                        event_edited.has_form = True
                    else:
                        event_edited.has_form = False
                    event_edited.rulebook = rulebook
                    event_edited.deadline_date = reg_date
                    event_edited.deadline_time = reg_time
                    event_edited.save()
                    Contact_Event.objects.filter(contact=event_edited).delete()
                    for contact in contacts_array:
                        Contact_Event.objects.create(
                            contact=event_edited,
                            name=contact["name"],
                            phone=contact["phone"],
                        )
                    if not event_edited.has_form:
                        try:
                            scope_gspread = [
                                "https://spreadsheets.google.com/feeds",
                                "https://www.googleapis.com/auth/drive",
                            ]
                            credentials_gspread = (
                                service_account.Credentials.from_service_account_file(
                                    os.path.abspath(
                                        "event/trystbackend-0d0f6831fb2b.json"
                                    ),
                                    scopes=scope_gspread,
                                )
                            )
                            gc = gspread.authorize(credentials_gspread)

                            # Find the Google Spreadsheet by event title in the specified folder
                            spreadsheet = gc.open_by_key(event_edited.spreadsheet_id)

                            spreadsheet.update_title(event_edited.title)

                            return Response(
                                {"success": "Event updated successfully."},
                                status=status.HTTP_200_OK,
                            )
                        except Exception as e:
                            return Response(
                                {
                                    "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                                },
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            )
                    return Response(
                        {"success": "Event updated successfully."},
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {"error": "Event ID not provided."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            event = Event(
                title=title,
                description=description,
                clubs=event_club,
                event_date=event_date,
                event_time=event_time,
                event_image=imgproc.compress(file, file.name),
                venue=venue,
                rulebook=rulebook,
                has_form=has_form,
                registration_link=registration_link,
                deadline_date=reg_date,
                deadline_time=reg_time,
            )
            event.save()
            for contact in contacts_array:
                Contact_Event.objects.create(
                    contact=event, name=contact["name"], phone=contact["phone"]
                )
            if not has_form:
                try:
                    drive_folder_id = "1uYaKt5NhxfaYXRerf6e49zGycDoC-hcW"
                    scope_gspread = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive",
                    ]
                    credentials_gspread = (
                        service_account.Credentials.from_service_account_file(
                            os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                            scopes=scope_gspread,
                        )
                    )
                    gc = gspread.authorize(credentials_gspread)
                    spreadsheet = gc.create(event.title)
                    spreadsheet_id = spreadsheet.id

                    scope_drive = ["https://www.googleapis.com/auth/drive"]
                    credentials_drive = (
                        service_account.Credentials.from_service_account_file(
                            os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                            scopes=scope_drive,
                        )
                    )
                    drive_service = build("drive", "v3", credentials=credentials_drive)
                    existing_parents = (
                        drive_service.files()
                        .get(fileId=spreadsheet_id, fields="parents")
                        .execute()["parents"]
                    )
                    response = (
                        drive_service.files()
                        .update(
                            fileId=spreadsheet_id,
                            addParents=drive_folder_id,
                            removeParents="root",
                            supportsAllDrives=True,
                        )
                        .execute()
                    )
                    drive_service.permissions().create(
                        fileId=spreadsheet_id,
                        body={
                            "role": "writer",
                            "type": "user",
                            "emailAddress": "sheets.tryst2024@gmail.com",
                        },
                    ).execute()

                    event.spreadsheet_id = spreadsheet_id
                    event.save()

                    return Response(
                        {
                            "success": "Event created successfully. Spreadsheet created and uploaded to Google Drive.",
                            "event_id": event.event_id,
                        },
                        status=status.HTTP_201_CREATED,
                    )

                except Exception as e:
                    return Response(
                        {
                            "error": f"Error creating/uploading Google Spreadsheet: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )
            else:
                return Response(
                    {"success": "Event created successfully."},
                    status=status.HTTP_201_CREATED,
                )
        else:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST", "GET"])
def registration(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = request.data
            titles = data["formFields"]
            event_id = data["event_id"]
            eventtype = data["event_type"]
            if event_id == None or eventtype == None:
                return Response(
                    {"error": "Complete event details are not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if len(titles) != 0:
                header = ["Name", "Phone", "Email", "State", "City", "College"]
                for title in titles:
                    header.append(f"{title['title']}")
                if eventtype == "competition":
                    event = Event.objects.get(event_id=event_id)
                elif eventtype == "workshop":
                    event = Workshop.objects.get(workshop_id=event_id)
                elif eventtype == "guestlecture":
                    event = Guest.objects.get(guest_id=event_id)
                else:
                    return Response(
                        {"error": "No event found."}, status=status.HTTP_400_BAD_REQUEST
                    )
            if "editedresponse" in data:
                registration = Registration.objects.get(
                    eventtype=eventtype, event_id=event_id
                )
                registration.formFields = titles
                registration.save()
                try:
                    scope_gspread = [
                        "https://spreadsheets.google.com/feeds",
                        "https://www.googleapis.com/auth/drive",
                    ]
                    credentials_gspread = (
                        service_account.Credentials.from_service_account_file(
                            os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                            scopes=scope_gspread,
                        )
                    )
                    gc = gspread.authorize(credentials_gspread)

                    spreadsheet = gc.open_by_key(event.spreadsheet_id)

                    worksheet = spreadsheet.sheet1

                    worksheet.batch_clear(["A1:Z1"])
                    worksheet.update("A1", [header])

                    return Response(
                        {"success": "Registration fields updated successfully"},
                        status=status.HTTP_200_OK,
                    )
                except Exception as e:
                    return Response(
                        {
                            "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                        },
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            else:
                Registration.objects.create(
                    eventtype=eventtype,
                    event_id=event_id,
                    formFields=titles,
                )
            # Append registration details to the Google Spreadsheet
            try:
                scope_gspread = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ]
                credentials_gspread = (
                    service_account.Credentials.from_service_account_file(
                        os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                        scopes=scope_gspread,
                    )
                )
                gc = gspread.authorize(credentials_gspread)

                # Find the Google Spreadsheet by event title in the specified folder
                spreadsheet = gc.open_by_key(event.spreadsheet_id)

                # Get the default worksheet
                worksheet = spreadsheet.sheet1

                # Add registration details headers to the worksheet
                worksheet.append_row(header)

            except Exception as e:
                return Response(
                    {
                        "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(
                {"success": "Registration successful."}, status=status.HTTP_201_CREATED
            )

        else:
            return Response(
                {"error": "You are not authenticated."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    elif request.method == "GET":
        if request.user.is_authenticated:
            event_id = request.query_params.get("event_id")
            eventtype = request.query_params.get("event_type")
            if event_id == None or eventtype == None:
                return Response(
                    {"error": "Event ID not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                registration = Registration.objects.get(
                    event_id=event_id, eventtype=eventtype
                )
                return Response(
                    {"formFields": registration.formFields}, status=status.HTTP_200_OK
                )
            except:
                return Response(
                    {"error": "Error occured: No such registration form found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST"])
def create_guest(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            data = request.data
            print(data)
            try:
                title = data["title"]
                description = data["description"]
                event_date = data["event_date"]
                # event_club = data["event_club"]
                event_time = data["event_time"]
                speakers_array = []
                venue = data["venue"]
                if request.FILES.get("file"):
                    file = request.FILES.get("file")
                else:
                    file = data["file"]
                # rulebook = data["ruleBook"]
                # if "registration_link" in data:
                #     registration_link = data["registration_link"]
                #     if data["registration_link"] == "":
                #         has_form = False
                #     else:
                #         has_form = True
                reg_date = data["reg_date"]
                reg_time = data["reg_time"]
                contacts_array = []
                pattern = re.compile(r"^contactPersons\[(\d+)\]\[(name|phone)\]$")
                for key, value in data.items():
                    match = pattern.match(key)
                    if match:
                        index, field = match.groups()
                        index = int(index)
                        while len(contacts_array) <= index:
                            contacts_array.append({})
                        contacts_array[index][field] = value
                pattern_speaker = re.compile(
                    r"^speakers\[(\d+)\]\[(name|description|file)\]$"
                )
                for key, value in data.items():
                    match = pattern_speaker.match(key)
                    if match:
                        index, field = match.groups()
                        index = int(index)
                        while len(speakers_array) <= index:
                            speakers_array.append({})
                        if field == "file":
                            if request.FILES.get("file"):
                                speakers_array[index][field] = request.FILES.get("file")
                            else:
                                speakers_array[index][field] = value
                        else:
                            speakers_array[index][field] = value
            except:
                return Response(
                    {"error": "Complete details are not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if "editedform" in data:
                if "event_id" in data:
                    event_edited = Guest.objects.get(guest_id=data["event_id"])
                    event_edited.title = title
                    event_edited.description = description
                    # event_edited.clubs = event_club
                    event_edited.event_date = event_date
                    event_edited.event_time = event_time
                    event_edited.venue = venue
                    if file:
                        if isinstance(file, str) and (
                            file.startswith("http") or file.startswith("https")
                        ):
                            response = requests.get(file)
                            if response.status_code == 200:
                                image_data = response.content
                                file_data = BytesIO(image_data)
                            else:
                                file_data = None
                        else:
                            file_data = file

                        if file_data:
                            if hasattr(file, "name"):
                                original_file_name = file.name
                            compressed_image = imgproc.compress(
                                file_data, original_file_name
                            )
                            event_edited.event_image = compressed_image
                    event_edited.deadline_date = reg_date
                    event_edited.deadline_time = reg_time
                    event_edited.save()
                    Contact_Guest.objects.filter(contact=event_edited).delete()
                    Speaker.objects.filter(guest=event_edited).delete()
                    for contact in contacts_array:
                        Contact_Guest.objects.create(
                            contact=event_edited,
                            name=contact["name"],
                            phone=contact["phone"],
                        )
                    for speaker in speakers_array:
                        Speaker.objects.create(
                            guest=event_edited,
                            name=speaker["name"],
                            description=speaker["description"],
                            file=speaker["file"],
                        )
                    # if not event_edited.has_form:
                    try:
                        scope_gspread = [
                            "https://spreadsheets.google.com/feeds",
                            "https://www.googleapis.com/auth/drive",
                        ]
                        credentials_gspread = (
                            service_account.Credentials.from_service_account_file(
                                os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                                scopes=scope_gspread,
                            )
                        )
                        gc = gspread.authorize(credentials_gspread)

                        spreadsheet = gc.open_by_key(event_edited.spreadsheet_id)

                        spreadsheet.update_title(event_edited.title)

                        return Response(
                            {"success": "Event updated successfully."},
                            status=status.HTTP_200_OK,
                        )
                    except Exception as e:
                        return Response(
                            {
                                "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                            },
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        )
                else:
                    return Response(
                        {"error": "Event ID not provided."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            event = Guest(
                title=title,
                description=description,
                event_date=event_date,
                # clubs=event_club,
                event_time=event_time,
                event_image=imgproc.compress(file, file.name),
                venue=venue,
                deadline_date=reg_date,
                deadline_time=reg_time,
            )
            event.save()
            for contact in contacts_array:
                Contact_Guest.objects.create(
                    contact=event, name=contact["name"], phone=contact["phone"]
                )
            for speaker in speakers_array:
                Speaker.objects.create(
                    speaker=event,
                    name=speaker["name"],
                    description=speaker["description"],
                    image=speaker["file"],
                )
            try:
                drive_folder_id = "1uYaKt5NhxfaYXRerf6e49zGycDoC-hcW"
                scope_gspread = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ]
                credentials_gspread = (
                    service_account.Credentials.from_service_account_file(
                        os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                        scopes=scope_gspread,
                    )
                )
                gc = gspread.authorize(credentials_gspread)
                spreadsheet = gc.create(event.title)
                spreadsheet_id = spreadsheet.id

                scope_drive = ["https://www.googleapis.com/auth/drive"]
                credentials_drive = (
                    service_account.Credentials.from_service_account_file(
                        os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                        scopes=scope_drive,
                    )
                )
                drive_service = build("drive", "v3", credentials=credentials_drive)
                existing_parents = (
                    drive_service.files()
                    .get(fileId=spreadsheet_id, fields="parents")
                    .execute()["parents"]
                )
                response = (
                    drive_service.files()
                    .update(
                        fileId=spreadsheet_id,
                        addParents=drive_folder_id,
                        removeParents="root",
                        supportsAllDrives=True,
                    )
                    .execute()
                )
                drive_service.permissions().create(
                    fileId=spreadsheet_id,
                    body={
                        "role": "writer",
                        "type": "user",
                        "emailAddress": "sheets.tryst2024@gmail.com",
                    },
                ).execute()

                event.spreadsheet_id = spreadsheet_id
                event.save()

                return Response(
                    {
                        "success": "Event created successfully. Spreadsheet created and uploaded to Google Drive.",
                        "event_id": event.guest_id,
                    },
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {"error": f"Error creating/uploading Google Spreadsheet: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response(
                {"error": "You are not authorized to perform this action."},
                status=status.HTTP_401_UNAUTHORIZED,
            )


@api_view(["POST", "GET"])
def register(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            data = request.data
            user = request.user.username
            if user == None:
                return Response(
                    {"error": "User not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            profile = Profile.objects.get(user_ID=user)
            college = College.objects.get(college_ID=profile.college_ID)
            form_data = {
                "Name": profile.name,
                "Phone": profile.phone_Number,
                "Email": profile.email_ID,
                "State": college.state,
                "City": college.city,
                "College": college.name,
            }
            try:
                event_id = data["event_id"]
                # print("check 1")
                event_type = data["event_type"]
                # print("check 2")
                form = data["form"]
                # print("details")
                if form:
                    for key, value in form.items():
                        form_data[key] = value
            except:
                return Response(
                    {"error": "Complete details not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if event_type == "competition":
                event = Event.objects.get(event_id=event_id)
            elif event_type == "workshop":
                event = Workshop.objects.get(workshop_id=event_id)
            elif event_type == "guestlecture":
                event = Guest.objects.get(guest_id=event_id)
            else:
                return Response(
                    {"error": "Invalid event type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            UserRegistration.objects.create(
                event_type=event_type, event_id=event_id, user=user, form=form_data
            )

            if any("Team Member" in key for key in form_data.keys()):
                for key, value in list(form_data.items()):
                    if "Team Member" in key and value != "":
                        team_member = Profile.objects.get(user_ID=value)
                        form_data[f"{value} Name"] = team_member.name
                        form_data[f"{value} Email"] = team_member.email_ID
                        form_data[f"{value} Phone"] = team_member.phone_Number
                        if team_member:
                            college = College.objects.get(
                                college_ID=team_member.college_ID
                            )
                            UserRegistration.objects.create(
                                event_type=event_type,
                                event_id=event_id,
                                user=value,
                                form=form_data,
                            )
            try:

                scope_gspread = [
                    "https://spreadsheets.google.com/feeds",
                    "https://www.googleapis.com/auth/drive",
                ]

                credentials_gspread = (
                    service_account.Credentials.from_service_account_file(
                        os.path.abspath("event/trystbackend-0d0f6831fb2b.json"),
                        scopes=scope_gspread,
                    )
                )
                gc = gspread.authorize(credentials_gspread)

                # Find the Google Spreadsheet by event title in the specified folder
                spreadsheet = gc.open_by_key(event.spreadsheet_id)

                # Get the default worksheet
                worksheet = spreadsheet.sheet1

                # directly update the next row with the form data in worksheet
                worksheet.append_row(list(form_data.values()))

                return Response(
                    {"success": "Registration successful."},
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {
                        "error": f"Error appending registration to Google Spreadsheet: {str(e)}"
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        if request.method == "GET":
            data = request.query_params
            event_id = data.get("event_id")
            event_type = data.get("event_type")
            if event_id == None or event_type == None:
                return Response(
                    {"error": "Event ID not provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if event_type == "competition":
                event = Event.objects.get(event_id=event_id)
            elif event_type == "workshop":
                event = Workshop.objects.get(workshop_id=event_id)
            elif event_type == "guest_lecture":
                event = Guest.objects.get(guest_id=event_id)
            else:
                return Response(
                    {"error": "Invalid event type."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if event.has_form:
                return Response(
                    {"registration_link": event.registration_link},
                    status=status.HTTP_200_OK,
                )
            registration = Registration.objects.get(
                event_id=event_id, eventtype=event_type
            )
            if registration:
                return Response(
                    {"formFields": registration.formFields},
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "No such registration form found."},
                    status=status.HTTP_404_NOT_FOUND,
                )
    else:
        return Response(
            {"error": "You are not authorized to perform this action."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["GET"])
def get_registered_events(request):
    if request.user.is_authenticated:
        user = request.user.username
        try:
            registered_events = UserRegistration.objects.filter(user=user)
            events = []
            for event in registered_events:
                event_details = None
                # print("event_type: ", event.event_type, "event_id: ", event.event_id)
                if event.event_type == "competition":
                    event_obj = Event.objects.get(event_id=event.event_id)
                    event_details = {
                        "id": event_obj.event_id,
                        "name": event_obj.title,
                        "date": event_obj.event_date,
                        "time": event_obj.event_time,
                        "venue": event_obj.venue,
                        "image": event_obj.event_image.url,
                    }
                elif event.event_type == "workshop":
                    event_obj = Workshop.objects.get(workshop_id=event.event_id)
                    event_details = {
                        "id": event_obj.workshop_id,
                        "name": event_obj.title,
                        "date": event_obj.event_date,
                        "time": event_obj.event_time,
                        "venue": event_obj.venue,
                        "image": event_obj.event_image.url,
                    }
                elif event.event_type == "guestlecture":
                    event_obj = Guest.objects.get(guest_id=event.event_id)
                    event_details = {
                        "id": event_obj.guest_id,
                        "name": event_obj.title,
                        "date": event_obj.event_date,
                        "time": event_obj.event_time,
                        "venue": event_obj.venue,
                        "image": event_obj.event_image.url,
                    }
                if event_details:
                    events.append(event_details)

            return Response({"registered_events": events}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    else:
        return Response(
            {"error": "You are not authorized to perform this action."},
            status=status.HTTP_401_UNAUTHORIZED,
        )


@api_view(["GET"])
def check_registration(request):
    if request.user.is_authenticated:
        user = request.user.username
        event_id = request.query_params.get("event_id")
        event_type = request.query_params.get("event_type")
        if event_id == None or event_type == None:
            return Response(
                {"error": "Event ID not provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        if not UserRegistration.objects.filter(
            event_id=event_id, event_type=event_type, user=user
        ).exists():
            return Response({"User is not registered"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"User is already registered"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {"error": "You are not authorized to perform this action."},
            status=status.HTTP_401_UNAUTHORIZED,
        )
