from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
from .utils import get_read_gmail_service

router = APIRouter()


@router.get("/sync-mailbox", response_model=List[Dict[str, Any]])
async def sync_mailbox():
    """
    TODO: Figure out a way to get 1000 - 1500 emails
    Retrieves emails from the user's Gmail inbox (For first time sync).
    Returns a list of email messages with basic information.
    """
    try:
        service = get_read_gmail_service()

        # Get messages from inbox
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=500
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
                "threadId": msg.get("threadId", ""),
                "from": next((h["value"] for h in headers if h["name"] == "From"), ""),
                "subject": next((h["value"] for h in headers if h["name"] == "Subject"), ""),
                "date": next((h["value"] for h in headers if h["name"] == "Date"), ""),
                "snippet": msg.get("snippet", ""),
                "labels": msg.get("labelIds", [])
            }
            email_list.append(email_data)

        return email_list

    except HttpError as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while syncing mailbox: {str(error)}"
        )


@router.get("/update-mailbox", response_model=List[Dict[str, Any]])
async def update_mailbox():
    """
    TODO: Think through the logic for this.
    Retrieves new emails from the user's Gmail inbox whenever user logs in.
    Logic: Fetch emails that are not read and were sent after the last time the user was online.
    Alternative: use the Gmail Push Notifications endpoint to get real-time updates.
    Returns a list of email messages with basic information.
    """
    try:
        service = get_read_gmail_service()

        # Get messages from inbox
        results = service.users().messages().list(
            userId="me",
            labelIds=["INBOX", "UNREAD"],
            maxResults=100
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
                "threadId": msg.get("threadId", ""),
                "from": next((h["value"] for h in headers if h["name"] == "From"), ""),
                "subject": next((h["value"] for h in headers if h["name"] == "Subject"), ""),
                "date": next((h["value"] for h in headers if h["name"] == "Date"), ""),
                "snippet": msg.get("snippet", ""),
                "labels": msg.get("labelIds", [])
            }
            email_list.append(email_data)

        return email_list

    except HttpError as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating mailbox: {str(error)}"
        )
