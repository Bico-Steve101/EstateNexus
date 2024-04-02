from datetime import timedelta

from celery import shared_task
from django.utils import timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import ScheduledMessage, Tenant
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_scheduled_messages(self):
    account_sid = 'AC9e35e109ca7de1d8892cc7e00908c6ea'
    auth_token = 'eeb9e3b2a960093dacdc3330bdb046a4'
    twilio_phone_number = '+12098878105'

    client = Client(account_sid, auth_token)
    messages = ScheduledMessage.objects.filter(send_at__lte=timezone.now(), is_sent=False)

    for message in messages:
        tenant = Tenant.objects.get(id=message.tenant.id)
        try:
            client.messages.create(
                body=f'EstateNexus, you have a message from "{message.tenant.property.name}": {message.message}',
                from_=twilio_phone_number,
                to=tenant.phone_number
            )
            message.is_sent = True
            message.save()
            logger.info(f'Successfully sent message {message.id} to {message.tenant.phone_number}')
        except TwilioRestException as e:
            logger.error(f'Twilio Error {e.code}: {e.msg}')
            message.send_at = timezone.now() + timedelta(minutes=5)
            message.save()
            try:
                self.retry(countdown=60 * 5)  # Retry in 5 minutes
            except self.MaxRetriesExceededError:
                logger.error(f'Failed to send message {message.id} after maximum retries')
        except Exception as e:
            logger.error(f'Failed to send message {message.id} to {message.tenant.phone_number}: {str(e)}')
