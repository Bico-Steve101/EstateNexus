# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from .models import Tenant, MPesaPayment
# from .views import mpesa_callback
# from unittest.mock import patch
#
# User = get_user_model()
#
# class MPesaCallbackTestCase(TestCase):
#     def setUp(self):
#         self.user = User.objects.create_user(username='test_user', password='password123')
#         self.tenant = Tenant.objects.create(
#             user=self.user,
#             first_name='John',
#             last_name='Doe',
#             email='john@example.com',
#             id_no='12345678',
#             phone_number='1234567890',
#             house_number='A1',
#             no_rooms=2,  # Assuming 2 rooms
#             occupants=1,
#             vehicle_no='ABC123',
#             tenant_id='T123',
#             sum_insured=1000,
#             lease_start_date='2023-01-01',
#             lease_end_date='2024-01-01',
#             balance=0
#         )
#         self.payment_data = {
#             'Body': {
#                 'stkCallback': {
#                     'CheckoutRequestID': '123456',
#                     'ResultCode': 0,
#                     'ResultDesc': 'Success',
#                     'CallbackMetadata': {
#                         'Item': [
#                             {'Name': 'Amount', 'Value': '100'},
#                             {'Name': 'PhoneNumber', 'Value': '1234567890'},
#                             {'Name': 'AccountReference', 'Value': str(self.user.id)}
#                         ]
#                     }
#                 }
#             }
#         }
#
#     @patch('User.views.logger')
#     def test_successful_payment(self, mock_logger):
#         response = self.client.post(reverse('mpesa_callback'), data=self.payment_data, content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         payment = MPesaPayment.objects.get(payment_id='123456')
#         self.assertEqual(payment.tenant, self.tenant)
#         self.assertEqual(payment.amount, 100)
#         self.assertEqual(payment.phone_number, '1234567890')
#         self.assertEqual(payment.status, 'completed')
#         mock_logger.info.assert_called_once()
#
#     @patch('User.views.logger')
#     def test_failed_payment(self, mock_logger):
#         self.payment_data['Body']['stkCallback']['ResultCode'] = 1
#         response = self.client.post(reverse('mpesa_callback'), data=self.payment_data, content_type='application/json')
#         self.assertEqual(response.status_code, 200)
#         self.assertFalse(MPesaPayment.objects.filter(payment_id='123456').exists())
#         mock_logger.error.assert_called_once()
#
#     @patch('User.views.logger')
#     def test_invalid_callback_data(self, mock_logger):
#         invalid_data = {'InvalidKey': 'InvalidValue'}  # Invalid data without required keys
#         response = self.client.post(reverse('mpesa_callback'), data=invalid_data, content_type='application/json')
#         self.assertEqual(response.status_code, 400)
#         self.assertFalse(MPesaPayment.objects.filter(payment_id='123456').exists())
#         mock_logger.error.assert_called_once()
