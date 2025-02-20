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
import csv


# TODO: Replace with actual credentials later (DONE)
# TODO: Encrypt the credentials with .env file (DONE)
# TODO: Add a function to get the device labels (DONE)
# TODO: Make token fetching into a function (DONE)
# TODO: Make client initialization into a function (DONE)
# TODO: Make the device info fetching into a function (DONE) 
# Overall refactoring is DONE

load_dotenv()

# Initialize Arduino IoT Cloud client 
def init_client():
    client_id = os.getenv('ARDUINO_CLIENT_ID')
    client_secret = os.getenv('ARDUINO_CLIENT_SECRET')
    token_url = os.getenv('ARDUINO_TOKEN_URL')

    if not all([client_id, client_secret, token_url]):
        raise ValueError("Missing required environment variables. Please check your .env file")
    
    return client_id, client_secret, token_url

# Function to get the token
def get_token():
    CLIENT_ID, CLIENT_SECRET, TOKEN_URL = init_client()
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
    return token


# Set up authentication headers
# api_url is defining the endpoint url (subject to change/add more endpoints)
def create_api_headers(token):
    api_url = "https://api2.arduino.cc/iot/v2/devices"
    headers = {
        'Authorization': f'Bearer {token.get("access_token")}',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Origin': 'https://api2.arduino.cc'
    }
    return api_url, headers


# Function to get the device info from the API
def get_device_info():
    # Get the devices from the API
    try:
        token = get_token()
        api_url, headers = create_api_headers(token)
        
        # First make OPTIONS request
        options_response = requests.options(api_url, headers=headers)
        
        # Then make GET request
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            devices = response.json()
            device_labels = [device.get('name', '') for device in devices]
            device_types = [device.get('type', '') for device in devices]
            #print("Device Labels:", device_labels)
            #print("Device Types:", device_types)
            return device_labels, device_types
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Exception when calling API: {str(e)}")
        return None, None
        

# Function to read a csv file (may be used for the data from the devices)
def read_csv_data(file_path, delimiter=',', encoding='utf-8', header=0):
    try:
        # Read CSV file into a pandas DataFrame
        df = pd.read_csv(
            file_path,
            delimiter=delimiter,
            encoding=encoding,
            header=header
        )

        if df.empty:
            print(f"Warning: The CSV file {file_path} is empty")
            return None
            
        print(f"Successfully loaded {len(df)} rows from {file_path}")
        return df
        
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found")
        return None
    except pd.errors.EmptyDataError:
        print(f"Error: The file {file_path} is empty")
        return None
    except Exception as e:
        print(f"Error reading CSV file: {str(e)}")
        return None
    

def main():
    print("Fetching Arduino IoT Cloud device information...")
    device_labels, device_types = get_device_info()

    if device_labels and device_types:
        print("\nDevice Summary:")
        print("-" * 50)
        for i, (label, type_) in enumerate(zip(device_labels, device_types), 1):
            print(f"Device {i}:")
            print(f" Name: {label}")
            print(f" Type: {type_}")
            print("-" * 50)
    else:
        print("Failed to fetch device information. Please check your credentials.")

if __name__ == "__main__":
    main()
