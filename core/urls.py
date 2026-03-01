from django.urls import path
from core.views import HealthView, EventGetListView, EventDetailView, SyncTriggerView, SeatsGetView, RegisterPostView, RegisterDeleteView

urlpatterns = [
    path('health', HealthView.as_view()),
    path('events', EventGetListView.as_view()),
    path('events/<uuid:event_id>', EventDetailView.as_view()),
    path('sync/trigger', SyncTriggerView.as_view()),
    path('events/<uuid:event_id>/seats', SeatsGetView.as_view()),
    path('tickets', RegisterPostView.as_view()),
    path('tickets/<uuid:ticket_id>', RegisterDeleteView.as_view()),
]