from api.routes.gmail.get_mail import get_email
from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError
from typing import List, Dict, Any
import asyncio
import aiohttp
from .utils import get_read_gmail_service

router = APIRouter()

# Fetches emails metadata through Gmail API first


async def _get_messages_list_metadata(service, label_ids, max_results=500, page_token=None):
    try:
        service = get_read_gmail_service()

        messages_metadata = []

        # Get messages from inbox
        results = service.users().messages().list(
            userId="me",
            labelIds=label_ids,
            maxResults=max_results
        ).execute()

        messages_metadata += results.get("messages", [])

        next_page_token = results.get("nextPageToken", "")

        while next_page_token:
            results = service.users().messages().list(
                userId="me",
                labelIds=label_ids,
                maxResults=max_results,
                pageToken=next_page_token
            ).execute()

            result_size_estimate = results.get("resultSizeEstimate", 0)
            messages_metadata += results.get("messages", [])

            # TODO: 2000 for free version. Potentially charge for all emails retrieval
            if len(messages_metadata) >= 2000:
                break

            if result_size_estimate < 500:
                break

            next_page_token = results.get("nextPageToken", "")

        return messages_metadata

    except HttpError as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching messages metadata: {str(error)}"
        )

# Fetches email data based on the given metadata


async def _get_message_data_from_metadata(session, service, message_metadata):
    url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_metadata['id']}"
    params = {
        "format": "full",
    }
    headers = {
        "Authorization": f"Bearer {service._http.credentials.token}"
    }

    try:
        async with session.get(url, params=params, headers=headers) as response:
            if response.status == 200:
                msg = await response.json()
            else:
                # Fallback to the synchronous method if the HTTP request fails
                msg = service.users().messages().get(
                    userId="me",
                    id=message_metadata["id"],
                    format="full",
                ).execute()

        email_data = get_email(msg)["data"]
    except Exception as e:
        print(f"Error processing message {message_metadata['id']}: {str(e)}")
        # Return minimal data in case of error
        email_data = {
            "id": message_metadata["id"],
            "threadId": message_metadata.get("threadId", ""),
            "from": "",
            "subject": "Error retrieving email",
            "date": "",
            "snippet": "An error occurred while retrieving this email.",
            "labels": []
        }

    return email_data


async def _get_all_message_data_from_metadata(session, service, message_metadata_list):
    tasks = []
    for message in message_metadata_list:
        task = asyncio.create_task(_get_message_data_from_metadata(
            session=session, service=service, message_metadata=message))
        tasks.append(task)

    res = await asyncio.gather(*tasks)

    return res


@router.get("/sync-mailbox", response_model=List[Dict[str, Any]])
async def sync_mailbox():
    """
    TODO: Implement filter when fetching emails (e.g., exclude marketing emails, etc.)
    Retrieves emails from the user's Gmail inbox (For first time sync).
    Returns a list of email messages with basic information.
    """
    try:
        service = get_read_gmail_service()
        messages_metadata = await _get_messages_list_metadata(service, ["INBOX"])

        async with aiohttp.ClientSession() as session:
            emails = await _get_all_message_data_from_metadata(
                session=session, service=service, message_metadata_list=messages_metadata)
            return emails

    except HttpError as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while fetching emails with their metadata: {str(error)}"
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
