from typing import Any

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from pydantic import BaseModel, ConfigDict

from src.settings import Settings
from src.utils.google import get_credentials

settings: Settings = Settings()
creds: Credentials = get_credentials()


class GmailEmails(BaseModel):
    """Retrieve the 10 most recent emails from Gmail."""

    model_config = ConfigDict(json_schema_extra={"name": "get_gmail_emails", "required": []})


async def get_gmail_emails() -> str:
    """
    Fetch the 10 most recent emails from Gmail.

    Returns:
        str: A formatted string containing email information.
    """
    service: Resource = build(serviceName="gmail", version="v1", credentials=creds)

    query: str = "-category:social -category:promotions -category:updates -category:forums"
    messages: dict[str, Any] = service.users().messages().list(userId="me", labelIds=["INBOX"], q=query, maxResults=10).execute()

    formatted_emails: list[str] = []

    for i, message in enumerate(messages.get("messages")):
        msg: dict[str, Any] = service.users().messages().get(userId="me", id=message.get("id")).execute()
        headers: list[dict[str, Any]] = msg.get("payload", {}).get("headers")
        subject: str = next((header.get("value") for header in headers if header.get("name") == "Subject"), "No Subject")
        sender: str = next((header.get("value") for header in headers if header.get("name") == "From"), "Unknown Sender")
        formatted_emails.append(f"[{i+1}] {subject} (From: {sender})")

    return "\n ---- \n".join(formatted_emails)
