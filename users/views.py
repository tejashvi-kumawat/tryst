import json
import tempfile
import requests
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.utils import get_tokens_for_user
from .models import Profile, College
from .utils import generate_user_id, validate_registration, create_password
from django.core.files import File
import tempfile
from utils.mailer import send_registration_email
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse


@api_view(["POST"])
def events_admin_login(request):
    data = request.data
    try:
        username = data["username"]
        password = data["password"]
    except Exception as e:
        return Response({"error": "Missing Fields"}, status=status.HTTP_400_BAD_REQUEST)
    user = User.objects.get(username=username)
    if not user:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    if not user.check_password(password):
        return Response(
            {"error": "Incorrect Password"}, status=status.HTTP_403_FORBIDDEN
        )
    tokens = get_tokens_for_user(user)
    if user.is_staff:
        return Response({"tokens": tokens}, status=status.HTTP_200_OK)
    else:
        return Response(
            {"error": "User is not authorised"}, status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(["POST"])
def iitd_login(request):
    data = request.data
    if not data["code"]:
        return Response(
            {"message": "Please provide a code."}, status=status.HTTP_400_BAD_REQUEST
        )
    code = data["code"]
    client_id = "j9McPoLgRB0kOA2W8TOsQjwePLYMdhpP"
    client_secret = "oV6XMJoWXprbT5cCKAtpYnmQwlCWxz49"
    request_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "authorization_code",
        "code": code,
    }
    request_url = "https://oauth2.iitd.ac.in/token.php"
    response = requests.post(request_url, request_data, verify=False)
    if response.status_code != 200:
        return Response(
            {"message": "Invalid code provided.", "error": str(response)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    response_data = response.json()
    access_token = response_data["access_token"]
    request_url = "https://oauth2.iitd.ac.in/resource.php"
    response = requests.post(
        request_url, data={"access_token": access_token}, verify=False
    )
    if response.status_code != 200:
        return Response(
            {"message": "Invalid access token provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    response_data = response.json()
    mail = response_data["mail"]
    # Check if user exists
    if not Profile.objects.filter(email_ID=mail).exists():
        return Response({"userdetails": response_data}, status=status.HTTP_200_OK)
    else:
        profile = Profile.objects.get(email_ID=mail)
        user_id = Profile.objects.get(user_ID=profile.user_ID)
        user = User.objects.get(username=user_id)
        tokens = get_tokens_for_user(user)
        return Response(
            {
                "tokens": tokens,
                "details": {
                    "name": profile.name,
                    "email": profile.email_ID,
                    "user_id": profile.user_ID,
                },
            },
            status=status.HTTP_200_OK,
        )


@api_view(["POST"])
def google_login(request):
    data = request.data
    if "token" not in data:
        return Response(
            {"error": "Invalid fields"}, status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    r = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        params={"access_token": data["token"]},
    )
    response_data = json.loads(r.text)

    if "error" in response_data:
        return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    email = response_data.get("email", "").lower()
    profile_exists = Profile.objects.filter(email_ID__iexact=email).exists()

    if not profile_exists:
        return Response(
            {
                "message": "New User Created",
                "details": {
                    "name": response_data["name"],
                    "email": email,
                    "photo": response_data["picture"],
                },
            },
            status=status.HTTP_201_CREATED,
        )

    profile = Profile.objects.get(email_ID__iexact=email)
    user = User.objects.get(username=profile.user_ID)
    photo = profile.photo.url if profile.photo else None
    return Response(
        {
            "message": "Logged in",
            "tokens": get_tokens_for_user(user),
            "details": {
                "name": profile.name,
                "email": profile.email_ID,
                "photo": photo,
                "user_id": profile.user_ID,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["GET", "POST", "PUT"])
def manage_profile(request):
    if request.method == "GET":
        # get profile details
        if request.user.is_authenticated:
            user = request.user
            profile = Profile.objects.get(user_ID=user.username)
            college = College.objects.get(college_ID=profile.college_ID)
            if profile.photo:
                photo = profile.photo.url
            else:
                photo = None
            state_colleges = (
                College.objects.filter(state=college.state)
                .values_list("college_ID", flat=True)
                .distinct()
            )
            city_colleges = (
                College.objects.filter(city=college.city)
                .values_list("college_ID", flat=True)
                .distinct()
            )
            state_colleges = list(state_colleges)
            city_colleges = list(city_colleges)
            return Response(
                {
                    "user_id": profile.user_ID,
                    "name": profile.name,
                    "phone_number": profile.phone_Number,
                    "email_id": profile.email_ID,
                    "college": college.name,
                    "city": college.city,
                    "state": college.state,
                    "instagram": profile.instagram_id,
                    "facebook": profile.facebook_Link,
                    "linkedin": profile.linkedIn_Link,
                    "photo": photo,
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
            )

    elif request.method == "POST":
        # Creating a new profile
        data = request.data
        validated_data = validate_registration(data)
        if validated_data != data:
            return Response(
                {"error": validated_data}, status=status.HTTP_400_BAD_REQUEST
            )
        if Profile.objects.filter(email_ID=data["email"]).exists():
            return Response(
                {"error": "This email is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if Profile.objects.filter(phone_Number=data["phone"]).exists():
            return Response(
                {"error": "This phone number is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_id = generate_user_id()
        password = create_password()
        user = User.objects.create_user(username=user_id, password=password)
        if "referral_id" in data:
            if Profile.objects.filter(user_ID=data["referral_id"]).exists():
                profile_referral = Profile.objects.get(
                    user_ID=data["referral_id"])
                profile_referral.points += 50
                profile_referral.save()
        photo_url = (
            data["photo"]
            or "https://www.pngitem.com/pimgs/m/146-1468479_my-profile-icon-blank-profile-picture-circle-hd.png"
        )
        photo_response = requests.get(photo_url)
        if photo_response.status_code == 200:
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(photo_response.content)
                temp_file.flush()
                new_college_id = None
                if data["college_name"] != "":
                    new_college = add_college(
                        data["college_name"], data["city"], data["state"]
                    )
                    if new_college.status_code == 200:
                        new_college_id = new_college.data["college_id"]
                profile_new = Profile.objects.create(
                    user_ID=user_id,
                    name=data["name"],
                    phone_Number=data["phone"],
                    email_ID=data["email"],
                    college_ID=new_college_id or data["college"],
                    instagram_id=data["instagram_ID"],
                    linkedIn_Link=data["linkedIn_Link"],
                )
                if data["college"] == "" and data["college_name"] == "":
                    profile_new.category = data["category"]
                    profile_new.college_ID = "4299"
                    send_registration_email(
                        data["email"],
                        data["name"],
                        College.objects.get(college_ID="4299").name,
                        user_id,
                    )
                else:
                    profile_new.category = "general"
                    send_registration_email(
                        data["email"],
                        data["name"],
                        College.objects.get(college_ID=data["college"]).name,
                        user_id,
                    )
                profile_new.save()
                profile_new.photo.save(
                    f"{user_id}_photo.jpg", File(temp_file), save=True
                )
        else:
            photo = None

        if "referral_id" in data:
            request_url = "https://cap-api.tryst-iitd.org/api/referral/"
            query = {
                "referral_id": data["referral_id"],
            }
            response = requests.get(request_url, query, timeout=5)
            if response.status_code == 404:
                return Response(
                    {"CA not found. Please enter correct CA ID"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        return Response(
            {
                "message": "User created!",
                "tokens": get_tokens_for_user(user),
                "user_id": user_id,
            },
            status=status.HTTP_201_CREATED,
        )

    elif request.method == "PUT":
        # update profile details
        if request.user.is_authenticated:
            user = request.user
            profile = Profile.objects.get(user_ID=user.username)
            data = request.data
            if "photo" in data:
                photo_url = data["photo"]
                photo_response = requests.get(photo_url)
                if photo_response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                        temp_file.write(photo_response.content)
                        temp_file.flush()
                        profile.photo.save(
                            f"{profile.user_ID}_photo.jpg", File(temp_file), save=True
                        )
            if "instagram" in data:
                profile.instagram_id = data["instagram"]
            if "linkedin" in data:
                profile.linkedIn_Link = data["linkedin"]

            profile.save()

        else:
            return Response(
                {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
            )


# add a new college if it doesn't exist
def add_college(college_name, city, state):
    if College.objects.count() == 0:
        college_id = 1
    else:
        college_id = College.objects.count() + 1
    if College.objects.filter(name=college_name, city=city, state=state).exists():
        return Response(
            {"error": "College already exists", "college_id": college_id},
            status=status.HTTP_400_BAD_REQUEST,
        )
    College.objects.create(
        college_ID=college_id, name=college_name, city=city, state=state
    )
    return Response(
        {"message": "College added", "college_id": college_id},
        status=status.HTTP_200_OK,
    )


# apis related to college (for registration)


@api_view(["GET"])
def get_cities(request):
    try:
        state = request.GET["state"]
    except:
        return Response({"error": "Missing state"}, status=status.HTTP_400_BAD_REQUEST)
    cities = (
        College.objects.filter(state=state).values_list(
            "city", flat=True).distinct()
    )
    if not cities:
        return Response(
            {"error": "No cities found"}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(list(cities), status=status.HTTP_200_OK)


@api_view(["GET"])
def get_colleges(request):
    try:
        city = request.GET["city"]
    except:
        return Response({"error": "Missing city"}, status=status.HTTP_400_BAD_REQUEST)
    colleges = College.objects.filter(city=city).values("college_ID", "name")
    if not colleges:
        return Response(
            {"error": "No colleges found"}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(colleges, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_college_details(request):
    try:
        college_id = request.GET["college_id"]
    except:
        return Response(
            {"error": "Missing college_id"}, status=status.HTTP_400_BAD_REQUEST
        )
    college = College.objects.filter(college_ID=college_id)
    if not college:
        return Response(
            {"error": "No college found"}, status=status.HTTP_400_BAD_REQUEST
        )
    return Response(college.values()[0], status=status.HTTP_200_OK)


@api_view(["GET"])
def get_user_profile_category(request):
    if request.user.is_authenticated:
        try:
            user = request.user
            profile = Profile.objects.get(user_ID=user.username)
            profile_category = profile.category
            return Response({"category": profile_category}, status=status.HTTP_200_OK)
        except:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )
    else:
        return Response(
            {"error": "User not logged in"}, status=status.HTTP_401_UNAUTHORIZED
        )
