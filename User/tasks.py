import base64
import datetime
import time
from datetime import timedelta

from celery import shared_task
from django.contrib.sites import requests
from django.utils import timezone
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import ScheduledMessage, Tenant
import logging


logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_scheduled_messages(self):
    account_sid = 'AC07a99ab29757d9b52dd396795ab8982f'
    auth_token = 'ce6895097c1175fea1b88023d255d95c'
    twilio_phone_number = '+15706522081'

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




# @shared_task
# def query_stk_push_status(checkout_request_id, phone_number):
#     access_token = getAccessToken()  # Function to retrieve access token
#
#     if not access_token:
#         logger.error('Failed to obtain M-Pesa access token.')
#         return
#
#     api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query"
#     headers = {'Authorization': 'Bearer ' + access_token,
#                'Content-Type': 'application/json'}
#
#     shortCode = "174379"
#     passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
#     timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
#     stk_password = base64.b64encode((shortCode + passkey + timestamp).encode('utf-8')).decode('utf-8')
#
#     request_data = {
#         "BusinessShortCode": shortCode,
#         "Password": stk_password,
#         "Timestamp": timestamp,
#         "CheckoutRequestID": checkout_request_id
#     }
#
#     retries = 0
#     max_retries = 10  # Maximum number of retries
#     retry_interval = 30  # Interval between retries in seconds
#
#     while retries < max_retries:
#         try:
#             logger.info('Querying STK push status...')
#             mpesa_response = requests.post(api_url, json=request_data, headers=headers)
#             response_data = mpesa_response.json()
#
#             # Process the response data
#             if response_data.get('ResponseCode') == '0':
#                 # Transaction was successful, handle accordingly
#                 # Example: Update database, send confirmation to user, etc.
#                 logger.info('Transaction successful')
#                 break  # Exit the loop if successful
#             else:
#                 # Transaction failed or other error occurred, handle accordingly
#                 # Example: Log error, inform user, retry, etc.
#                 logger.error('Transaction failed: %s', response_data.get('errorMessage', 'Unknown error'))
#
#             # Increment the number of retries
#             retries += 1
#
#             if retries < max_retries:
#                 # Wait before retrying
#                 time.sleep(retry_interval)
#
#         except Exception as e:
#             logger.error('Error querying STK push status:', exc_info=True)
#
#             # Increment the number of retries
#             retries += 1
#
#             if retries < max_retries:
#                 # Wait before retrying
#                 time.sleep(retry_interval)