import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
import base64
from .utils import get_all_gmail_service

router = APIRouter()


@router.post("/reply")
async def reply_to_email(
    message_id: str,
    reply_data: Dict[str, str] = Body(..., example={
        "body": "This is my reply",
        "thread_id": "thread_id_here"
    })
):
    """
    Reply to an email using the Gmail API.

    Args:
        message_id: The ID of the message to reply to
        reply_data: Contains the body of the reply and thread_id

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Get the original message to extract headers
        original_message = service.users().messages().get(
            userId="me",
            id=message_id
        ).execute()

        headers = original_message["payload"]["headers"]
        subject = next((h["value"]
                       for h in headers if h["name"] == "Subject"), "")
        from_email = next((h["value"]
                          for h in headers if h["name"] == "From"), "")

        # Extract email address from the "From" field
        if "<" in from_email and ">" in from_email:
            to_email = from_email.split("<")[1].split(">")[0]
        else:
            to_email = from_email

        # Create reply with proper headers
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        # Create the message
        message = MIMEText(reply_data["body"])
        message["To"] = to_email
        message["Subject"] = subject
        message["In-Reply-To"] = message_id
        message["References"] = message_id

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create the final message body
        body = {
            "raw": encoded_message,
            "threadId": reply_data.get("thread_id", original_message.get("threadId"))
        }

        # Send the reply
        sent_message = service.users().messages().send(
            userId="me",
            body=body
        ).execute()

        return {
            "status": "success",
            "message": "Reply sent successfully",
            "message_id": sent_message["id"]
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.delete("/delete/{message_id}")
async def delete_email(message_id: str):
    """
    Permanently delete an email using the Gmail API.

    Args:
        message_id: The ID of the message to delete

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Permanently delete the message
        service.users().messages().delete(
            userId="me",
            id=message_id
        ).execute()

        return {
            "status": "success",
            "message": "Email deleted successfully"
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.post("/archive/{message_id}")
async def archive_email(message_id: str):
    """
    Archive an email by removing the INBOX label using the Gmail API.

    Args:
        message_id: The ID of the message to archive

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Remove INBOX label to archive the message
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["INBOX"]}
        ).execute()

        return {
            "status": "success",
            "message": "Email archived successfully"
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.post("/mark-as-read/{message_id}")
async def mark_as_read(message_id: str):
    """
    Mark an email as read by removing the UNREAD label using the Gmail API.

    Args:
        message_id: The ID of the message to mark as read

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Remove UNREAD label
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]}
        ).execute()

        return {
            "status": "success",
            "message": "Email marked as read"
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.post("/mark-as-unread/{message_id}")
async def mark_as_unread(message_id: str):
    """
    Mark an email as unread by adding the UNREAD label using the Gmail API.

    Args:
        message_id: The ID of the message to mark as unread

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Add UNREAD label
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": ["UNREAD"]}
        ).execute()

        return {
            "status": "success",
            "message": "Email marked as unread"
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.post("/add-label/{message_id}")
async def add_label(
    message_id: str,
    label_data: Dict[str, str] = Body(..., example={"label_id": "Label_123"})
):
    """
    Add a label to an email using the Gmail API.

    Args:
        message_id: The ID of the message to label
        label_data: Contains the label_id to add

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Add the specified label
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_data["label_id"]]}
        ).execute()

        return {
            "status": "success",
            "message": "Label added successfully"
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")


@router.post("/forward")
async def forward_email(
    message_id: str,
    forward_data: Dict[str, str] = Body(..., example={
        "to": "recipient@example.com",
        "additional_text": "FYI, see email below."
    })
):
    """
    Forward an email to another recipient using the Gmail API.

    Args:
        message_id: The ID of the message to forward
        forward_data: Contains the recipient and any additional text

    Returns:
        Dict with status and message information
    """
    try:
        service = get_all_gmail_service()

        # Get the original message
        original_message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        headers = original_message["payload"]["headers"]
        subject = next((h["value"]
                       for h in headers if h["name"] == "Subject"), "")
        from_email = next((h["value"]
                          for h in headers if h["name"] == "From"), "")

        # Prepare forward subject
        if not subject.startswith("Fwd:"):
            subject = f"Fwd: {subject}"

        # Get the message content
        # This is simplified - in a real app you'd need to handle different MIME types
        message_content = ""
        if "parts" in original_message["payload"]:
            for part in original_message["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    if data:
                        message_content = base64.urlsafe_b64decode(
                            data).decode()
                    break
        elif "body" in original_message["payload"] and "data" in original_message["payload"]["body"]:
            data = original_message["payload"]["body"]["data"]
            message_content = base64.urlsafe_b64decode(data).decode()

        # Create forward message
        forward_text = f"""
{forward_data.get('additional_text', '')}

---------- Forwarded message ---------
From: {from_email}
Subject: {subject}

{message_content}
"""

        message = MIMEText(forward_text)
        message["To"] = forward_data["to"]
        message["Subject"] = subject

        # Encode the message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create the final message body
        body = {
            "raw": encoded_message
        }

        # Send the forwarded message
        sent_message = service.users().messages().send(
            userId="me",
            body=body
        ).execute()

        return {
            "status": "success",
            "message": "Email forwarded successfully",
            "message_id": sent_message["id"]
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500, detail=f"An error occurred: {error}")
