"""
Utility functions for sending alerts via email and SMS.
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
import logging

logger = logging.getLogger(__name__)


def send_email_alert(recipient_email, subject, message, html_message=None):
    """
    Send email alert to recipient.
    
    Args:
        recipient_email (str): Email address of recipient
        subject (str): Email subject
        message (str): Plain text message
        html_message (str, optional): HTML message
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if html_message:
            email = EmailMultiAlternatives(
                subject=subject,
                body=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            email.attach_alternative(html_message, "text/html")
            email.send()
        else:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False
            )
        
        logger.info(f"Email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {str(e)}")
        return False


def send_sms_alert(recipient_phone, message):
    """
    Send SMS alert to recipient using Twilio.
    
    Args:
        recipient_phone (str): Phone number of recipient (with country code)
        message (str): SMS message
    
    Returns:
        bool: True if SMS sent successfully, False otherwise
    """
    try:
        # Initialize Twilio client
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Send SMS
        message_obj = client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=recipient_phone
        )
        
        logger.info(f"SMS sent successfully to {recipient_phone}, SID: {message_obj.sid}")
        return True
        
    except TwilioException as e:
        logger.error(f"Twilio error sending SMS to {recipient_phone}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send SMS to {recipient_phone}: {str(e)}")
        return False


def send_whatsapp_alert(recipient_phone, message):
    """
    Send WhatsApp alert to recipient using Twilio.
    
    Args:
        recipient_phone (str): Phone number of recipient (with country code)
        message (str): WhatsApp message
    
    Returns:
        bool: True if WhatsApp message sent successfully, False otherwise
    """
    try:
        # Initialize Twilio client
        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )
        
        # Send WhatsApp message
        message_obj = client.messages.create(
            body=message,
            from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
            to=f"whatsapp:{recipient_phone}"
        )
        
        logger.info(f"WhatsApp message sent successfully to {recipient_phone}, SID: {message_obj.sid}")
        return True
        
    except TwilioException as e:
        logger.error(f"Twilio error sending WhatsApp to {recipient_phone}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Failed to send WhatsApp to {recipient_phone}: {str(e)}")
        return False


def send_alert_notification(alert_notification, delivery_methods=['email', 'sms']):
    """
    Send alert notification through specified delivery methods.
    
    Args:
        alert_notification: AlertNotification instance
        delivery_methods (list): List of delivery methods ['email', 'sms', 'whatsapp']
    
    Returns:
        dict: Results of each delivery method
    """
    results = {}
    
    # Get recipient information
    recipient_email = None
    recipient_phone = None
    
    # Try to get email and phone from related users
    if hasattr(alert_notification, 'village') and alert_notification.village:
        # Get users from the village's health facilities
        health_facilities = alert_notification.village.healthfacility_set.all()
        for facility in health_facilities:
            if facility.email:
                recipient_email = facility.email
                break
    
    # For now, use default test values
    if not recipient_email:
        recipient_email = "test@example.com"
    if not recipient_phone:
        recipient_phone = "+919876543210"
    
    # Prepare message content
    subject = f"Health Alert: {alert_notification.alert_type}"
    message = f"""
Alert Type: {alert_notification.alert_type}
Severity: {alert_notification.severity}
Location: {alert_notification.village.name if alert_notification.village else 'Unknown'}
Message: {alert_notification.message}
Time: {alert_notification.triggered_at}

Please take appropriate action immediately.

Smart Health Surveillance System
    """
    
    html_message = f"""
    <html>
    <body>
        <h2>🚨 Health Alert Notification</h2>
        <p><strong>Alert Type:</strong> {alert_notification.alert_type}</p>
        <p><strong>Severity:</strong> {alert_notification.severity}</p>
        <p><strong>Location:</strong> {alert_notification.village.name if alert_notification.village else 'Unknown'}</p>
        <p><strong>Message:</strong> {alert_notification.message}</p>
        <p><strong>Time:</strong> {alert_notification.triggered_at}</p>
        <hr>
        <p><em>Please take appropriate action immediately.</em></p>
        <p><small>Smart Health Surveillance System</small></p>
    </body>
    </html>
    """
    
    # Send through each delivery method
    if 'email' in delivery_methods:
        results['email'] = send_email_alert(recipient_email, subject, message, html_message)
    
    if 'sms' in delivery_methods:
        results['sms'] = send_sms_alert(recipient_phone, message)
    
    if 'whatsapp' in delivery_methods:
        results['whatsapp'] = send_whatsapp_alert(recipient_phone, message)
    
    return results
