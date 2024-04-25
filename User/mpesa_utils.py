# import requests
# import json
# from datetime import datetime
# import base64
# import logging
#
#
# logger = logging.getLogger(__name__)
#
#
# def getAccessToken():
#     consumer_key = "sGxb5imn3ePLbcNKeaUiVKpIxNtWQkO8DDH6qEJJpCZGFwGy"
#     consumer_secret = "S55sSNaKNWUS1TsG7DTWxZdgmlULDhAqRSGGCfzp0YGNaoJILwKfGwjRAJLG39ki"
#
#     url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
#
#     try:
#
#         encoded_credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
#
#         headers = {
#             "Authorization": f"Basic {encoded_credentials}",
#             "Content-Type": "application/json"
#         }
#
#         # Send the request and parse the response
#         response = requests.get(url, headers=headers).json()
#
#         # Check for errors and return the access token
#         if "access_token" in response:
#             return response["access_token"]
#         else:
#             raise Exception("Failed to get access token: " + response["error_description"])
#     except Exception as e:
#         raise Exception("Failed to get access token: " + str(e))
#
#
# def query_stk_push_status(checkout_request_id, phone_number):
#     access_token = getAccessToken()  # Function to retrieve access token
#
#     if not access_token:
#         logging.error('Failed to obtain M-Pesa access token.')
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
#     try:
#         mpesa_response = requests.post(api_url, json=request_data, headers=headers)
#         response_data = mpesa_response.json()
#
#         # Process the response data
#         if response_data.get('ResponseCode') == '0':
#             # Transaction was successful, handle accordingly
#             # Example: Update database, send confirmation to user, etc.
#             print("Transaction successful")
#         else:
#             # Transaction failed or other error occurred, handle accordingly
#             # Example: Log error, inform user, retry, etc.
#             print("Transaction failed:", response_data.get('errorMessage', 'Unknown error'))
#
#     except Exception as e:
#         logging.error('Error querying STK push status:', exc_info=True)
