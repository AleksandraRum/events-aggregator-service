from django.urls import path
from core.views import HealthView, EventGetListView, EventDetailView, SyncTriggerView

urlpatterns = [
    path('health/', HealthView.as_view()),
    path('events/', EventGetListView.as_view()),
    path('events/<uuid:event_id>/', EventDetailView.as_view()),
    path('sync/trigger', SyncTriggerView.as_view()),
    path('sync/trigger/', SyncTriggerView.as_view()),
]