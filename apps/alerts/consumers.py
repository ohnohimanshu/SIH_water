"""
WebSocket consumers for real-time alerts.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import AlertNotification

User = get_user_model()


class AlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for individual user alerts.
    """
    
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'alerts_user_{self.user_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'alert_message',
                'message': message
            }
        )
    
    # Receive message from room group
    async def alert_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    # Receive new alert from room group
    async def new_alert(self, event):
        alert_data = event['alert']
        
        # Send alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'alert': alert_data
        }))
    
    # Receive alert update from room group
    async def alert_update(self, event):
        alert_data = event['alert']
        
        # Send alert update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'alert_update',
            'alert': alert_data
        }))


class DashboardAlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for district dashboard alerts.
    """
    
    async def connect(self):
        self.district_id = self.scope['url_route']['kwargs']['district_id']
        self.room_group_name = f'alerts_district_{self.district_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'dashboard_message',
                'message': message
            }
        )
    
    # Receive message from room group
    async def dashboard_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    # Receive new alert from room group
    async def new_alert(self, event):
        alert_data = event['alert']
        
        # Send alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'alert': alert_data
        }))
    
    # Receive alert update from room group
    async def alert_update(self, event):
        alert_data = event['alert']
        
        # Send alert update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'alert_update',
            'alert': alert_data
        }))
    
    # Receive statistics update from room group
    async def stats_update(self, event):
        stats_data = event['stats']
        
        # Send statistics update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': stats_data
        }))


class StateAlertConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for state-level alerts.
    """
    
    async def connect(self):
        self.state_id = self.scope['url_route']['kwargs']['state_id']
        self.room_group_name = f'alerts_state_{self.state_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'state_message',
                'message': message
            }
        )
    
    # Receive message from room group
    async def state_message(self, event):
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
    
    # Receive new alert from room group
    async def new_alert(self, event):
        alert_data = event['alert']
        
        # Send alert to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'new_alert',
            'alert': alert_data
        }))
    
    # Receive alert update from room group
    async def alert_update(self, event):
        alert_data = event['alert']
        
        # Send alert update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'alert_update',
            'alert': alert_data
        }))
    
    # Receive statistics update from room group
    async def stats_update(self, event):
        stats_data = event['stats']
        
        # Send statistics update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': stats_data
        }))
