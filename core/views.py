from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from core.serializers import EventListSerializer
from core.models import Event

class HealthView(APIView):
    # renderer_classes = [JSONRenderer]

    def get(self, request):
        return Response({'status': 'ok'})


class EventGetListView(ListAPIView):
    queryset = Event.objects.select_related('place')
    serializer_class = EventListSerializer