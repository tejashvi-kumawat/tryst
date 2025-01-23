from rest_framework_simplejwt.tokens import RefreshToken
from .models import Profile, College
import random
import time


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_user_id():
    time_part = str(int(time.time()*(10**5) % 1000))
    count_part = str(Profile.objects.count() + 1)
    return "TRC" + "0"*(3-len(time_part)) + time_part + "0"*(4-len(count_part)) + count_part


def validate_registration(data):
    required_fields = ['name', 'phone', 'email']
    if 'college' not in data:
        if 'category' not in data:
            return "College is required"
    for field in required_fields:
        if field not in data or not data[field]:
            return f"{field.capitalize()} is required"
    return data


def create_password():
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-=[];',./|:<>?`~"
    password = ""
    for i in range(16):
        password += random.choice(chars)
    return password
