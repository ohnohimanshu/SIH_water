"""
Alert service for sending notifications.
"""
import logging
from typing import Dict, List, Optional
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import models
from django.utils import timezone
from .models import AlertNotification, AlertSubscription, AlertDeliveryLog, AlertTemplate
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import json

User = get_user_model()
logger = logging.getLogger(__name__)


class AlertService:
    """
    Service for managing alert notifications.
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def send_alert(self, alert: AlertNotification) -> Dict:
        """
        Send alert notification through all configured channels.
        """
        try:
            # Get subscribers for this alert
            subscribers = self.get_alert_subscribers(alert)
            
            if not subscribers:
                logger.warning(f"No subscribers found for alert {alert.alert_id}")
                return {'success': False, 'error': 'No subscribers found'}
            
            # Send to each subscriber
            results = []
            for subscriber in subscribers:
                result = self.send_to_subscriber(alert, subscriber)
                results.append(result)
            
            # Send real-time WebSocket notification
            self.send_websocket_notification(alert)
            
            # Update alert delivery status
            alert.delivery_attempts += 1
            alert.last_delivery_attempt = alert.triggered_at
            alert.save()
            
            successful_deliveries = sum(1 for r in results if r['success'])
            
            return {
                'success': successful_deliveries > 0,
                'total_subscribers': len(subscribers),
                'successful_deliveries': successful_deliveries,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Error sending alert {alert.alert_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_alert_subscribers(self, alert: AlertNotification) -> List[User]:
        """
        Get users who should receive this alert based on their subscriptions.
        """
        subscribers = []
        
        # Get subscriptions that match this alert
        subscriptions = AlertSubscription.objects.filter(
            alert_type=alert.alert_type,
            is_active=True
        )
        
        # Filter by geographic scope
        if alert.village:
            subscriptions = subscriptions.filter(
                models.Q(village=alert.village) |
                models.Q(village__isnull=True, district=alert.village.block.district) |
                models.Q(village__isnull=True, district__isnull=True, state=alert.village.block.district.state)
            )
        elif alert.district:
            subscriptions = subscriptions.filter(
                models.Q(district=alert.district) |
                models.Q(district__isnull=True, state=alert.district.state)
            )
        elif alert.state:
            subscriptions = subscriptions.filter(
                models.Q(state=alert.state) |
                models.Q(state__isnull=True)
            )
        
        # Filter by severity
        severity_order = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        alert_severity_index = severity_order.index(alert.alert_severity)
        
        for subscription in subscriptions:
            min_severity_index = severity_order.index(subscription.min_severity)
            if alert_severity_index >= min_severity_index:
                subscribers.append(subscription.user)
        
        return list(set(subscribers))  # Remove duplicates
    
    def send_to_subscriber(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send alert to a specific user through their preferred delivery methods.
        """
        try:
            subscription = AlertSubscription.objects.filter(
                user=user,
                alert_type=alert.alert_type
            ).first()
            
            if not subscription:
                return {'success': False, 'error': 'No subscription found'}
            
            results = []
            
            # Send through each delivery method
            for delivery_method in subscription.delivery_methods:
                result = self.send_via_method(alert, user, delivery_method)
                results.append(result)
                
                # Log delivery attempt
                AlertDeliveryLog.objects.create(
                    alert=alert,
                    user=user,
                    delivery_method=delivery_method,
                    delivery_status=result['status'],
                    delivery_response=result.get('response', {}),
                    error_message=result.get('error', '')
                )
            
            successful_deliveries = sum(1 for r in results if r['success'])
            
            return {
                'success': successful_deliveries > 0,
                'user_id': user.id,
                'delivery_results': results
            }
            
        except Exception as e:
            logger.error(f"Error sending alert to user {user.id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_via_method(self, alert: AlertNotification, user: User, method: str) -> Dict:
        """
        Send alert via specific delivery method.
        """
        try:
            if method == 'EMAIL':
                return self.send_email(alert, user)
            elif method == 'SMS':
                return self.send_sms(alert, user)
            elif method == 'WHATSAPP':
                return self.send_whatsapp(alert, user)
            elif method == 'PUSH':
                return self.send_push_notification(alert, user)
            elif method == 'DASHBOARD':
                return self.send_dashboard_notification(alert, user)
            else:
                return {'success': False, 'error': f'Unknown delivery method: {method}'}
                
        except Exception as e:
            logger.error(f"Error sending via {method} to user {user.id}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def send_email(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send alert via email.
        """
        try:
            if not user.email:
                return {'success': False, 'error': 'User has no email address'}
            
            # Get email template
            template = AlertTemplate.objects.filter(
                alert_type=alert.alert_type,
                delivery_method='EMAIL',
                is_active=True
            ).first()
            
            if template:
                subject = template.subject_template.format(
                    title=alert.title,
                    village=alert.village.name if alert.village else 'Unknown',
                    severity=alert.alert_severity
                )
                message = template.message_template.format(
                    title=alert.title,
                    message=alert.message,
                    description=alert.description,
                    village=alert.village.name if alert.village else 'Unknown',
                    severity=alert.alert_severity,
                    triggered_at=alert.triggered_at
                )
            else:
                subject = f"Health Alert: {alert.title}"
                message = f"""
                {alert.message}
                
                {alert.description}
                
                Village: {alert.village.name if alert.village else 'Unknown'}
                Severity: {alert.alert_severity}
                Time: {alert.triggered_at}
                
                Please take appropriate action.
                """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return {
                'success': True,
                'status': 'SENT',
                'method': 'EMAIL',
                'response': {'email': user.email}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'status': 'FAILED'}
    
    def send_sms(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send alert via SMS using Twilio.
        """
        try:
            if not user.phone_number:
                return {'success': False, 'error': 'User has no phone number'}
            
            # Get SMS template
            template = AlertTemplate.objects.filter(
                alert_type=alert.alert_type,
                delivery_method='SMS',
                is_active=True
            ).first()
            
            if template:
                message = template.message_template.format(
                    title=alert.title,
                    message=alert.message,
                    village=alert.village.name if alert.village else 'Unknown',
                    severity=alert.alert_severity
                )
            else:
                message = f"Health Alert: {alert.title} in {alert.village.name if alert.village else 'Unknown'}. {alert.message}"
            
            # Truncate message if too long
            if len(message) > 160:
                message = message[:157] + "..."
            
            # Send SMS using Twilio (if configured)
            if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
                from twilio.rest import Client
                
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                
                message_obj = client.messages.create(
                    body=message,
                    from_=settings.TWILIO_PHONE_NUMBER,
                    to=user.phone_number
                )
                
                return {
                    'success': True,
                    'status': 'SENT',
                    'method': 'SMS',
                    'response': {'message_sid': message_obj.sid}
                }
            else:
                # Log SMS for testing (no actual sending)
                logger.info(f"SMS would be sent to {user.phone_number}: {message}")
                return {
                    'success': True,
                    'status': 'SENT',
                    'method': 'SMS',
                    'response': {'test_mode': True, 'message': message}
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'status': 'FAILED'}
    
    def send_whatsapp(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send alert via WhatsApp.
        """
        try:
            if not user.phone_number:
                return {'success': False, 'error': 'User has no phone number'}
            
            # Get WhatsApp template
            template = AlertTemplate.objects.filter(
                alert_type=alert.alert_type,
                delivery_method='WHATSAPP',
                is_active=True
            ).first()
            
            if template:
                message = template.message_template.format(
                    title=alert.title,
                    message=alert.message,
                    village=alert.village.name if alert.village else 'Unknown',
                    severity=alert.alert_severity
                )
            else:
                message = f"🚨 Health Alert: {alert.title}\n\n{alert.message}\n\n📍 Village: {alert.village.name if alert.village else 'Unknown'}\n⚠️ Severity: {alert.alert_severity}\n🕐 Time: {alert.triggered_at}"
            
            # Send WhatsApp using Twilio (if configured)
            if hasattr(settings, 'TWILIO_ACCOUNT_SID') and settings.TWILIO_ACCOUNT_SID:
                from twilio.rest import Client
                
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
                
                message_obj = client.messages.create(
                    body=message,
                    from_=f'whatsapp:{settings.TWILIO_PHONE_NUMBER}',
                    to=f'whatsapp:{user.phone_number}'
                )
                
                return {
                    'success': True,
                    'status': 'SENT',
                    'method': 'WHATSAPP',
                    'response': {'message_sid': message_obj.sid}
                }
            else:
                # Log WhatsApp for testing (no actual sending)
                logger.info(f"WhatsApp would be sent to {user.phone_number}: {message}")
                return {
                    'success': True,
                    'status': 'SENT',
                    'method': 'WHATSAPP',
                    'response': {'test_mode': True, 'message': message}
                }
                
        except Exception as e:
            return {'success': False, 'error': str(e), 'status': 'FAILED'}
    
    def send_push_notification(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send push notification (placeholder for mobile app integration).
        """
        try:
            # This would integrate with Firebase Cloud Messaging or similar
            # For now, just log the notification
            
            logger.info(f"Push notification would be sent to user {user.id}: {alert.title}")
            
            return {
                'success': True,
                'status': 'SENT',
                'method': 'PUSH',
                'response': {'test_mode': True, 'user_id': user.id}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'status': 'FAILED'}
    
    def send_dashboard_notification(self, alert: AlertNotification, user: User) -> Dict:
        """
        Send dashboard notification via WebSocket.
        """
        try:
            # Send WebSocket notification to user
            self.send_websocket_notification(alert, user)
            
            return {
                'success': True,
                'status': 'SENT',
                'method': 'DASHBOARD',
                'response': {'websocket_sent': True}
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'status': 'FAILED'}
    
    def send_websocket_notification(self, alert: AlertNotification, user: User = None):
        """
        Send real-time WebSocket notification.
        """
        try:
            if not self.channel_layer:
                return
            
            alert_data = {
                'id': alert.id,
                'alert_id': alert.alert_id,
                'alert_type': alert.alert_type,
                'alert_severity': alert.alert_severity,
                'title': alert.title,
                'message': alert.message,
                'village': alert.village.name if alert.village else None,
                'district': alert.district.name if alert.district else None,
                'state': alert.state.name if alert.state else None,
                'triggered_at': alert.triggered_at.isoformat(),
                'alert_data': alert.alert_data
            }
            
            if user:
                # Send to specific user
                group_name = f'alerts_user_{user.id}'
                async_to_sync(self.channel_layer.group_send)(
                    group_name,
                    {
                        'type': 'new_alert',
                        'alert': alert_data
                    }
                )
            else:
                # Send to all relevant groups
                if alert.village:
                    # Send to village group
                    group_name = f'alerts_village_{alert.village.id}'
                    async_to_sync(self.channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'new_alert',
                            'alert': alert_data
                        }
                    )
                
                if alert.district:
                    # Send to district group
                    group_name = f'alerts_district_{alert.district.id}'
                    async_to_sync(self.channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'new_alert',
                            'alert': alert_data
                        }
                    )
                
                if alert.state:
                    # Send to state group
                    group_name = f'alerts_state_{alert.state.id}'
                    async_to_sync(self.channel_layer.group_send)(
                        group_name,
                        {
                            'type': 'new_alert',
                            'alert': alert_data
                        }
                    )
            
        except Exception as e:
            logger.error(f"Error sending WebSocket notification: {str(e)}")
    
    def acknowledge_alert(self, alert: AlertNotification, user: User) -> bool:
        """
        Acknowledge an alert.
        """
        try:
            alert.alert_status = 'ACKNOWLEDGED'
            alert.acknowledged_by = user
            alert.acknowledged_at = timezone.now()
            alert.save()
            
            # Send acknowledgment notification
            self.send_websocket_notification(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Error acknowledging alert {alert.alert_id}: {str(e)}")
            return False
    
    def resolve_alert(self, alert: AlertNotification, user: User, resolution_notes: str = '') -> bool:
        """
        Resolve an alert.
        """
        try:
            alert.alert_status = 'RESOLVED'
            alert.resolved_by = user
            alert.resolved_at = timezone.now()
            alert.resolution_notes = resolution_notes
            alert.save()
            
            # Send resolution notification
            self.send_websocket_notification(alert)
            
            return True
            
        except Exception as e:
            logger.error(f"Error resolving alert {alert.alert_id}: {str(e)}")
            return False
