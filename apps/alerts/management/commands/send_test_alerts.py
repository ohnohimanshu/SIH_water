"""
Management command to send test alerts via email and SMS.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.alerts.utils import send_email_alert, send_sms_alert, send_whatsapp_alert
from apps.alerts.models import AlertNotification
from apps.geography.models import Village
from django.utils import timezone
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Send test alerts via email and SMS to verify functionality'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            type=str,
            help='Email address to send test alert to',
            default='test@example.com'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Phone number to send test SMS to (with country code)',
            default='+919876543210'
        )
        parser.add_argument(
            '--whatsapp',
            type=str,
            help='Phone number to send test WhatsApp to (with country code)',
            default='+919876543210'
        )

    def handle(self, *args, **options):
        email = options['email']
        phone = options['phone']
        whatsapp = options['whatsapp']
        
        self.stdout.write('Sending test alerts...')
        
        # Test email
        self.stdout.write('Testing email...')
        email_result = send_email_alert(
            recipient_email=email,
            subject='Test Alert - Smart Health Surveillance System',
            message='This is a test email alert from the Smart Health Surveillance System. If you receive this, email functionality is working correctly.',
            html_message='''
            <html>
            <body>
                <h2>✅ Test Email Alert</h2>
                <p>This is a test email alert from the <strong>Smart Health Surveillance System</strong>.</p>
                <p>If you receive this, email functionality is working correctly!</p>
                <hr>
                <p><small>System Status: Operational</small></p>
            </body>
            </html>
            '''
        )
        
        if email_result:
            self.stdout.write(self.style.SUCCESS('✅ Email test successful!'))
        else:
            self.stdout.write(self.style.ERROR('❌ Email test failed!'))
        
        # Test SMS
        self.stdout.write('Testing SMS...')
        sms_result = send_sms_alert(
            recipient_phone=phone,
            message='Test Alert: Smart Health Surveillance System is operational. SMS functionality working correctly!'
        )
        
        if sms_result:
            self.stdout.write(self.style.SUCCESS('✅ SMS test successful!'))
        else:
            self.stdout.write(self.style.ERROR('❌ SMS test failed!'))
        
        # Test WhatsApp
        self.stdout.write('Testing WhatsApp...')
        whatsapp_result = send_whatsapp_alert(
            recipient_phone=whatsapp,
            message='🚨 Test Alert: Smart Health Surveillance System is operational. WhatsApp functionality working correctly!'
        )
        
        if whatsapp_result:
            self.stdout.write(self.style.SUCCESS('✅ WhatsApp test successful!'))
        else:
            self.stdout.write(self.style.ERROR('❌ WhatsApp test failed!'))
        
        # Create a test alert notification
        self.stdout.write('Creating test alert notification...')
        try:
            village = Village.objects.first()
            if village:
                from django.contrib.auth import get_user_model
                import uuid
                User = get_user_model()
                
                alert = AlertNotification.objects.create(
                    alert_id=f"TEST{str(uuid.uuid4())[:8].upper()}",
                    alert_type='SYSTEM_TEST',
                    alert_severity='LOW',
                    alert_status='ACTIVE',
                    title='Test Alert Notification',
                    message='This is a test alert notification to verify the system is working correctly.',
                    description='Test alert to verify system functionality',
                    village=village,
                    district=village.block.district if village.block else None,
                    state=village.block.district.state if village.block and village.block.district else None,
                    triggered_at=timezone.now(),
                    created_by=User.objects.filter(is_superuser=True).first()
                )
                self.stdout.write(f'✅ Test alert notification created: {alert.id}')
            else:
                self.stdout.write(self.style.WARNING('⚠️ No villages found, skipping alert notification creation'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to create test alert notification: {e}'))
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write('TEST SUMMARY:')
        self.stdout.write(f'Email: {"✅ SUCCESS" if email_result else "❌ FAILED"}')
        self.stdout.write(f'SMS: {"✅ SUCCESS" if sms_result else "❌ FAILED"}')
        self.stdout.write(f'WhatsApp: {"✅ SUCCESS" if whatsapp_result else "❌ FAILED"}')
        self.stdout.write('='*50)
        
        if all([email_result, sms_result, whatsapp_result]):
            self.stdout.write(self.style.SUCCESS('🎉 All tests passed! Email and SMS functionality is working correctly.'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ Some tests failed. Please check the configuration and try again.'))
