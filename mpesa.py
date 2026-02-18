import requests
from requests.auth import HTTPBasicAuth
import datetime
import base64

# Sandbox credentials (replace with your own)
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
SHORTCODE = "174379"
PASSKEY = "YOUR_PASSKEY"
CALLBACK_URL = "https://YOUR_NGROK_URL/mpesa/callback"

def get_mpesa_token():
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    data = response.json()
    return data["access_token"]

def lipa_na_mpesa(phone, amount, token):
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    password = base64.b64encode(f"{SHORTCODE}{PASSKEY}{timestamp}".encode('utf-8')).decode('utf-8')

    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "DimbaWiFi",
        "TransactionDesc": "Pay for WiFi"
    }

    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {"Authorization": "Bearer " + token}
    response = requests.post(url, json=payload, headers=headers)
    return response.json()