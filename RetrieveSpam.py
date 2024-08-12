import os.path
import pickle
import base64
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import message_from_bytes
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import re
import streamlit as st

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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

#Retrieving the spam email using labelIds and passing Spam
def retrieve_spam_emails(service):
    label_id = get_label_id(service, 'Spam')  # Use 'Spam' or correct name for spam folder
    if not label_id:
        st.error("Spam label not found.")
        return []

    results = service.users().messages().list(userId='me', labelIds=[label_id], maxResults=30).execute()
    messages = results.get('messages', [])
    return messages

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


#Making word cloud using spam folder in 'id'
def get_spam_wordcloud():
    service = retrieve_and_process_emails()
    messages = retrieve_spam_emails(service)
    all_text = ""
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        content = get_email_content(msg)
        all_text += content + " "

    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_text)
    return wordcloud

#plotting wordcloud
def show_wordcloud():
    st.sidebar.header("Word Cloud of Spam Emails")
    wordcloud = get_spam_wordcloud()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    st.sidebar.pyplot(fig)

def analysis():
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

    # Retrieving the latest 30 messages from the spam folder, if don't need spam just remove labelIds as a whole and it will pick all mails.
    results = service.users().messages().list(userId='me', labelIds=['SPAM'], maxResults=30).execute()
    messages = results.get('messages', [])

    if not messages:
        print('No spam messages found.')
        return

    all_texts = ""

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='raw').execute()
        content = get_email_content(msg)
        all_texts += content

    # Clean the text and remove common email-related words
    cleaned_text = re.sub(r'\b(?:From|To|Subject|Date|Re)\b', '', all_texts)
    cleaned_text = re.sub(r'\W+', ' ', cleaned_text.lower())

    # Generate a word cloud
    wordcloud = WordCloud(width=800, height=400, max_words=50, background_color='white').generate(cleaned_text)

    fig, ax = plt.subplots(figsize=(10, 5))  # Set figure size
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')  # Turn off axes for cleaner visualization
    st.pyplot(fig)

    # Save the word cloud as an image
    wordcloud.to_file('Commonwords.jpg')
#RahulGupta
#https://www.linkedin.com/in/rahul-gupta-a31749166/
