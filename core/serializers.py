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