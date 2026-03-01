from rest_framework import serializers
from core.models import Place, Event


class PlaceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'city', 'address']


class EventListSerializer(serializers.ModelSerializer):
    place = PlaceListSerializer()
    class Meta:
        model = Event
        fields = ['id', 'name', 'place', 'event_time', 'registration_deadline', 'status', 'number_of_visitors']


class PlaceDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = ['id', 'name', 'city', 'address', 'seats_pattern']


class EventDetailSerializer(serializers.ModelSerializer):
    place = PlaceDetailSerializer()
    class Meta:
        model = Event
        fields = ['id', 'name', 'place', 'event_time', 'registration_deadline', 'status', 'number_of_visitors']


class RegisterSerializer(serializers.Serializer):
    event_id = serializers.UUIDField()
    first_name = serializers.CharField(max_length=50, allow_blank=False, trim_whitespace=True)
    last_name = serializers.CharField(max_length=50, allow_blank=False, trim_whitespace=True)
    email = serializers.EmailField()
    seat = serializers.RegexField(r"^[A-Za-z]\d+$", max_length=32)