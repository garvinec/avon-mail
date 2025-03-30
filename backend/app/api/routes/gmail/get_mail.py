from fastapi import APIRouter, HTTPException
from googleapiclient.errors import HttpError
from typing import Dict, Any
from .utils import get_read_gmail_service

router = APIRouter()


@router.get("/email/{message_id}")
async def get_email_by_id(message_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific email using its message ID.

    Args:
        message_id: The ID of the email message to retrieve

    Returns:
        Dict containing email details including subject, sender, body, etc.
    """
    try:
        service = get_read_gmail_service()

        # Get the full message details
        message = service.users().messages().get(
            userId="me",
            id=message_id,
            format="full"
        ).execute()

        # Extract headers
        headers = message["payload"]["headers"]
        email_data = {
            "id": message["id"],
            "threadId": message.get("threadId", ""),
            "from": next((h["value"] for h in headers if h["name"].lower() == "from"), ""),
            "to": next((h["value"] for h in headers if h["name"].lower() == "to"), ""),
            "subject": next((h["value"] for h in headers if h["name"].lower() == "subject"), ""),
            "date": next((h["value"] for h in headers if h["name"].lower() == "date"), ""),
            "snippet": message.get("snippet", ""),
            "labels": message.get("labelIds", []),
        }

        # Extract body content
        if "parts" in message["payload"]:
            # Multipart message
            for part in message["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    if "data" in part["body"]:
                        import base64
                        data = part["body"]["data"]
                        email_data["body"] = base64.urlsafe_b64decode(
                            data).decode()
                        break
        elif "body" in message["payload"] and "data" in message["payload"]["body"]:
            # Single part message
            import base64
            data = message["payload"]["body"]["data"]
            email_data["body"] = base64.urlsafe_b64decode(data).decode()
        else:
            email_data["body"] = ""

        return {
            "status": "success",
            "data": email_data
        }

    except HttpError as error:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while retrieving the email: {str(error)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(e)}"
        )
