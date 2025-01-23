from rest_framework import serializers
from .models import Event, Contact_Event, Workshop, Contact_Workshop, Guest, Contact_Guest, Speaker, Registration


class ContactEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Event
        fields = '__all__'


class ContactWorkshopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Workshop
        fields = '__all__'


class ContactGuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact_Guest
        fields = '__all__'


class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    contact = ContactEventSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = '__all__'


class WorkshopSerializer(serializers.ModelSerializer):
    contact = ContactWorkshopSerializer(many=True, read_only=True)

    class Meta:
        model = Workshop
        fields = '__all__'


class GuestSerializer(serializers.ModelSerializer):
    contact = ContactGuestSerializer(many=True, read_only=True)
    speaker = SpeakerSerializer(many=True, read_only=True)

    class Meta:
        model = Guest
        fields = '__all__'
