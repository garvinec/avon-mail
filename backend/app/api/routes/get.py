import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import APIRouter

router = APIRouter(prefix="/get")

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


@router.get("/inbox-emails")
def get_inbox_emails():
    """
    Retrieves emails from the user's Gmail inbox.
    Returns a list of email messages with basic information.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("gmail", "v1", credentials=creds)

        # Get messages from inbox
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=100  # Adjust this number as needed
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            return []

        email_list = []
        for message in messages:
            msg = service.users().messages().get(
                userId="me",
                id=message["id"],
                format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = msg["payload"]["headers"]
            email_data = {
                "id": msg["id"],
                "from": next((h["value"] for h in headers if h["name"] == "From"), ""),
                "subject": next((h["value"] for h in headers if h["name"] == "Subject"), ""),
                "date": next((h["value"] for h in headers if h["name"] == "Date"), ""),
                "snippet": msg.get("snippet", "")
            }
            email_list.append(email_data)

        return email_list

    except HttpError as error:
        print(f"An error occurred: {error}")
        return []
