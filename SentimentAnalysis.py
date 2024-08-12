import streamlit as st
import os
import pickle
import base64
import json
import openai
from openai import OpenAI
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
from textblob import TextBlob

client_service_data = {
    "client_id": os.environ.get("client_id"),
    "project_id": os.environ.get("project_id"),
    "auth_uri": os.environ.get("auth_uri"),
    "token_uri": os.environ.get("token_uri"),
    "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
    "client_secret": os.environ.get("client_secret")
   
}

with open("client_service.json", "w") as f:
    json.dump(client_service_data, f, indent=4)
    
# Loading API key file for OpenAI API. Create using https://platform.openai.com/docs/models/gpt-4o-mini
#with open('openai_key.json', 'r') as f:
#    data = json.load(f)
#    api_key = data['api_key']
def load_api_key(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            openai.api_key = data['api_key']
    except FileNotFoundError:
        #st.write(f"Error: File '{file_path}' not found.")
        "api_key": os.environ.get("api_key")
        with open("openai_key.json", "w") as f:
            json.dump(client_service_data, f, indent=4)
    except json.JSONDecodeError:
        st.write(f"Error: Invalid JSON in '{file_path}'.")

# Example usage:
client=load_api_key('openai_key.json')

# Initialize OpenAI client
#client = OpenAI(api_key=os.environ.get("openai_key.json"))

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

#Getting the email contents
def get_email_content(message):

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(msg_str)

    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                return part.get_payload(decode=True).decode('utf-8')
    else:
        return mime_msg.get_payload(decode=True).decode('utf-8')

    return ""

#Summarising the text using 'gpt 4o mini' model
def summarize_text(text):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Update this to the correct model name if needed
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes text."},
            {"role": "user", "content": f"Summarize the following text:\n\n{text}"}
        ],
        temperature=0,
        max_tokens=100
    )
    summary = response.choices[0].message.content
    return summary

#Analysing sentiment using textblob
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive"
    elif sentiment < 0:
        return "Negative"
    else:
        return "Neutral"

# Selecting emails
def select_emails(messages, service):
    email_options = []
    for idx, message in enumerate(messages):
        msg = service.users().messages().get(userId='me', id=message['id'], format='metadata').execute()
        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        email_options.append(f"{idx + 1}: {subject}")

    selected_indices = st.multiselect("Select Emails:", email_options)
    selected_emails = [messages[int(index.split(':')[0]) - 1] for index in selected_indices]
    return selected_emails

def list_labels(service):
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    return labels


def get_label_id(service, label_name):
    labels = list_labels(service)
    for label in labels:
        if label['name'] == label_name:
            return label['id']
    return None


#Processing personal gmail using client secret json file aka the "OAuth 2.0 Client IDs" file from the Google cloud API services.
#link: https://console.cloud.google.com/apis/credentials

def retrieve_and_process_emails():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

# Analysing using port and client service file. Updat port value based on your local host port and client_secret is the file from "OAuth 2.0 Client IDs"
# from google cloud API services
def sentanalysis():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Retrieve the latest 30 messages from the spam folder
    results = service.users().messages().list(userId='me', maxResults=30).execute()
    messages = results.get('messages', [])

    if not messages:
        st.write('No messages found.')
        return

    # User can select which email to use for analysis
    selected_emails = select_emails(messages, service)
    selected_emails=selected_emails[:1]

    for message in selected_emails:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        content = get_email_content(msg)

        # Summarize the email content using gpt 4o mini model
        summary = summarize_text(content)
        st.write(f"Email Summary:\n{summary}\n")

        # Perform sentiment analysis on the email content
        sentiment = analyze_sentiment(content)
        st.write(f"Email Sentiment: {sentiment}\n")

        st.write('-' * 40)

#RahulGupta
#https://www.linkedin.com/in/rahul-gupta-a31749166/
