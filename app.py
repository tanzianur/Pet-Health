import streamlit as st
from arduino_iot_cloud import ArduinoCloudClient
import pandas as pd
from datetime import datetime, timedelta
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from dotenv import load_dotenv
import iot_api_client as iot
from iot_api_client.exceptions import ApiException
from iot_api_client.models import *
from iot_api_client.configuration import Configuration
from iot_api_client.api import DevicesV2Api
import requests
import os

# Initialize Arduino IoT Cloud client
# TODO: Replace with actual credentials later (DONE)
# TODO: Encrypt the credentials with .env file (DONE)

print("Current working directory:", os.getcwd())

load_dotenv()

# Initialize Arduino IoT Cloud client 
CLIENT_ID = os.getenv('ARDUINO_CLIENT_ID')
CLIENT_SECRET = os.getenv('ARDUINO_CLIENT_SECRET')
TOKEN_URL = os.getenv('ARDUINO_TOKEN_URL', 'https://api2.arduino.cc/iot/v1/clients/token')

# Validate that all required variables are present
if not all([CLIENT_ID, CLIENT_SECRET, TOKEN_URL]):
    raise ValueError("Missing required environment variables. Please check your .env file")

oauth_client = BackendApplicationClient(client_id=CLIENT_ID)
oauth = OAuth2Session(client=oauth_client)

try:
    token = oauth.fetch_token(
        token_url=TOKEN_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        include_client_id=True,
        audience="https://api2.arduino.cc/iot"
    )
    #print("Token successfully obtained:", token.get("access_token"))
except Exception as e:
    raise

# Configure API client
api_url = "https://api2.arduino.cc/iot/v2/devices"
headers = {
    'Authorization': f'Bearer {token.get("access_token")}',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Origin': 'https://api2.arduino.cc'
}

try:
    # First make OPTIONS request
    options_response = requests.options(api_url, headers=headers)
    
    # Then make GET request
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        devices = response.json()
        device_labels = [device.get('name', '') for device in devices]
        print("Device Labels:", device_labels)
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"Exception when calling API: {str(e)}")