from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.utils import timezone
from .wize import updateDB
from rest_framework_simplejwt.tokens import RefreshToken
import uuid


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


@api_view(["GET"])
def qr(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    e = request.user.emailId
    i = request.GET.get("eventId")
    w = Wize.objects.filter(emailId=e, eventId=i)
    return Response(w, status=status.HTTP_200_OK)


@api_view(["GET"])
def pronite(request):
    pronites = Pronite.objects.all().values()
    return Response(pronites, status=status.HTTP_200_OK)


@api_view(["GET"])
def slot(request):
    if not request.user.is_authenticated:
        return Response(status=status.HTTP_401_UNAUTHORIZED)
    proniteID = request.GET.get("proniteID")
    print(proniteID)
    slots = Slot.objects.filter(
        capacity__gt=0,
        start_time__lt=timezone.now(),
        end_time__gt=timezone.now(),
        proniteId=proniteID,
    ).values()
    return Response(slots, status=status.HTTP_200_OK)


@api_view(["GET"])
def passes(request):
    if request.user.is_authenticated:
        passes = Pass.objects.filter(userId=request.user.username).values()
        if not passes:
            return Response(
                {"error": "No passes found"}, status=status.HTTP_404_NOT_FOUND
            )
        for pass_ in passes:
            if not pass_["entry"]:
                del pass_["entryTime"]
            pass_["pronite"] = Slot.objects.get(id=pass_["slotId"]).proniteId
        return Response(passes, status=status.HTTP_200_OK)
    return Response(
        {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def bookPasses(request, slotId):
    if request.user.is_authenticated:
        userId = request.user.username
        data = request.data
        profile = Profile.objects.get(user_ID=request.user.username)
        if not profile.email_ID[-10:] == "iitd.ac.in":
            return Response(
                {"error": "Only IITD students are allowed"},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            slots = Slot.objects.filter(
                proniteId=Slot.objects.get(id=slotId).proniteId
            ).values()
        except:
            return Response(
                {"error": "Invalid slotId"}, status=status.HTTP_400_BAD_REQUEST
            )
        slotids = [slot["id"] for slot in slots]
        if Pass.objects.filter(userId=userId, slotId__in=slotids):
            return Response(
                {"error": "You have already booked a pass"},
                status=status.HTTP_403_FORBIDDEN,
            )
        s = Slot.objects.get(id=slotId)
        if not s:
            return Response(
                {"error": "Invalid slotId"}, status=status.HTTP_400_BAD_REQUEST
            )
        t = timezone.now()
        if s.start_time > t:
            return Response(
                {"error": "Slot has not started yet"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if s.end_time < t:
            return Response(
                {"error": "Slot has ended"}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            nextSlot = Slot.objects.get(id=int(slotId) + 1)
        except:
            nextSlot = None
        if not s.capacity:
            if not nextSlot:
                return Response(
                    {"error": "Slot capacity is full"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            time = str(
                datetime.datetime.strptime(
                    nextSlot.start_time.strftime("%H:%M"), "%H:%M"
                )
                + datetime.timedelta(minutes=330)
            ).split(" ")[1]
            return Response(
                {"error": f"Slot capacity is full. More slots at {time} HRS."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        p = Pass.objects.create(userId=userId, slotId=slotId)
        s.capacity -= 1
        s.save()
        return Response({"passCode": p.code}, status=status.HTTP_201_CREATED)
    return Response(
        {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def entry(request):
    if request.user.is_authenticated:
        data = request.data
        if not "code" in data:
            return Response(
                {"error": "Invalid fields"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        myPass = Pass.objects.filter(code=data["code"])
        if not myPass:
            return Response(
                {"error": "Invalid pass code"}, status=status.HTTP_404_NOT_FOUND
            )
        entries = myPass.filter(entry=True).values()
        if not entries:
            return Response(
                {"error": "No entries found"}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(entries, status=status.HTTP_200_OK)
    return Response(
        {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(["POST"])
def login(request):
    data = request.data
    if "username" not in data or "password" not in data:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        user = User.objects.get(username=data["username"])
    except User.DoesNotExist:
        return Response({"error": "Invalid username"}, status=status.HTTP_404_NOT_FOUND)
    if not user.check_password(data["password"]):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
        )
    if not user.is_superuser:
        return Response(
            {"error": "User not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )
    tokens = get_tokens_for_user(user)
    return Response({"tokens": tokens}, status=status.HTTP_200_OK)


# api to scan the qr code


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False

@api_view(["POST"])
def enterPasses(request):
    if request.user.is_staff:
        data = request.data
        if "code" not in data:
            return Response(
                {"error": "Invalid fields"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
            )
        # if not Pass.objects.filter(code=data['code']):
        #     return Response({'error': 'No pass found'}, status=status.HTTP_404_NOT_FOUND)
        # check that data['code'] is a valid pass code i.e. uuid.uuid4 type
        if not is_valid_uuid(data["code"]):
            return Response(
                {"error": "Invalid pass code"}, status=status.HTTP_404_NOT_FOUND
            )
        # pass_ = Pass.objects.get(code=data["code"])
        pass_exists = Pass.objects.filter(code=data["code"])
        if pass_exists:
            if pass_exists[0].entry:
                return Response(
                    {"error": "Pass already entered"}, status=status.HTTP_403_FORBIDDEN
                )
            else:
                pass_exists.update(entry=True, entryTime=timezone.now())
        else:
            Pass.objects.create(code=data["code"], entry=True, entryTime=timezone.now(), slotId=17, userId="tryst_member")


        return Response({"message": "Entry successful"}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "Not a staff member"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
def internalpass(request):
    if not request.user.is_superuser:
        return Response(
            {"error": "User not authorized"}, status=status.HTTP_401_UNAUTHORIZED
        )
    data = request.data
    username = data["username"]
    password = data["password"]
    if username == "hmawandia" and password == "tryst":
        name = data["name"]
        user = User.objects.create_user(username=name, password="mawandia&oganja")
        user.save()
        passes = Pass.objects.create(userId=name, slotId=1)
        passes.save()
        return Response(
            {"message": "Pass generated", "passcode": passes.code},
            status=status.HTTP_201_CREATED,
        )


@api_view(["POST"])
def self_login(request):
    data = request.data
    if "username" not in data or "password" not in data:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    try:
        user = User.objects.get(username=data["username"])
    except User.DoesNotExist:
        return Response({"error": "Invalid username"}, status=status.HTTP_404_NOT_FOUND)
    if not user.check_password(data["password"]):
        return Response(
            {"error": "Invalid password"}, status=status.HTTP_401_UNAUTHORIZED
        )
    tokens = get_tokens_for_user(user)
    return Response({"tokens": tokens}, status=status.HTTP_200_OK)
