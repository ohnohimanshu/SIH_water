"""
WebSocket routing for alerts app.
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/alerts/(?P<user_id>\w+)/$', consumers.AlertConsumer.as_asgi()),
    re_path(r'ws/alerts/dashboard/(?P<district_id>\w+)/$', consumers.DashboardAlertConsumer.as_asgi()),
    re_path(r'ws/alerts/state/(?P<state_id>\w+)/$', consumers.StateAlertConsumer.as_asgi()),
]
