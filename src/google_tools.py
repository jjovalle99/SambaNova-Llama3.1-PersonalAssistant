from datetime import datetime
from typing import Any

import pytz
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build
from pydantic import BaseModel, ConfigDict

from src.settings import Settings

settings: Settings = Settings()


def get_credentials() -> Credentials:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/calendar.readonly"]
    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(str(settings.credentials_path), SCOPES)
    creds: Credentials = flow.run_local_server(port=0)
    return creds


creds: Credentials = get_credentials()


class GmailEmails(BaseModel):
    """Retrieve the 10 most recent emails from Gmail."""

    model_config = ConfigDict(json_schema_extra={"name": "get_gmail_emails", "required": []})


class CalendarAppointments(BaseModel):
    """Retrieve the next 10 calendar appointments."""

    model_config = ConfigDict(json_schema_extra={"name": "get_calendar_appointments", "required": []})


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


async def get_calendar_appointments() -> str:
    """
    Fetch the next 10 calendar appointments.

    Returns:
        str: A formatted string containing appointment information.
    """
    service: Resource = build(serviceName="calendar", version="v3", credentials=creds)

    utc_now = datetime.now(pytz.utc)
    rfc3339_time = utc_now.isoformat()

    events: dict[str, Any] = (
        service.events()
        .list(calendarId="primary", timeMin=rfc3339_time, maxResults=10, singleEvents=True, orderBy="startTime")
        .execute()
    )

    formatted_appointments: list[str] = []
    for i, event in enumerate(events.get("items", [])):
        start: str = event["start"].get("dateTime", event["start"].get("date"))
        start_time: datetime = datetime.fromisoformat(start.replace("Z", "+00:00"))
        formatted_appointments.append(f"[{i+1}] {event['summary']} (Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')})")

    return "\n ---- \n".join(formatted_appointments)
