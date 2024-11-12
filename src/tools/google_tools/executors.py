import base64
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import Any

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pydantic import BaseModel, ConfigDict, Field

from src.settings import Settings

settings = Settings()


class GoogleServiceExecutor(BaseModel, ABC):
    """Base class for Google service executors."""

    @abstractmethod
    async def execute(self, creds: Credentials):
        pass


class GmailReadExecutor(GoogleServiceExecutor):
    """Get the n most recent emails from Gmail"""

    model_config = ConfigDict(json_schema_extra={"name": "read_gmail_emails"})
    n: int = Field(description="Number of emails to read")

    async def execute(self, creds: Credentials) -> str:
        """
        Fetch the n most recent emails from Gmail.

        Args:
            creds (Credentials): Google OAuth2 credentials.

        Returns:
            str: A formatted string containing email information.
        """
        service = build(serviceName="gmail", version="v1", credentials=creds)
        # Obtain ids of the n most recent emails in the inbox
        messages: dict[str, Any] = (
            service.users().messages().list(userId="me", labelIds=["INBOX"], q="category:primary", maxResults=self.n).execute()
        )

        # Extract email information from the messages
        formatted_emails: list[str] | None = []

        for i, message in enumerate(messages.get("messages")):
            msg: dict[str, Any] = service.users().messages().get(userId="me", id=message.get("id")).execute()
            snippet: str = msg.get("snippet", "No snippet")
            labels: list[str] = msg.get("labelIds", [])
            headers: list[dict[str, Any]] = msg.get("payload", {}).get("headers")
            date: str = next((header.get("value") for header in headers if header.get("name") == "Date"), "Unknown Date")
            subject: str = next((header.get("value") for header in headers if header.get("name") == "Subject"), "No Subject")
            sender: str = next((header.get("value") for header in headers if header.get("name") == "From"), "Unknown Sender")
            formatted_emails.append(
                f"[{i+1}] Subject: {subject}\n(From: {sender} at {date})\nSnippet: {snippet}\nLabels: {labels}"
            )

        return "\n ---- \n".join(formatted_emails)


class GmailWriteExecutor(GoogleServiceExecutor):
    """Send an email from Gmail"""

    model_config = ConfigDict(json_schema_extra={"name": "send_gmail_email"})
    to: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject")
    body: str = Field(description="Complete content of the email. Expected to be long text.")

    async def execute(self, creds) -> str:
        """Send an email using the Gmail API.

        Args:
            creds (Credentials): Google OAuth2 credentials.

        Returns:
            str: A message indicating if the email was sent successfully.
        """
        service = build(serviceName="gmail", version="v1", credentials=creds)

        message = EmailMessage()
        message.set_content(self.body)
        message["To"] = self.to
        message["From"] = settings.gmail_host_user
        message["Subject"] = self.subject

        # Encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {"raw": encoded_message}

        # Send message
        sent_message = service.users().messages().send(userId="me", body=create_message).execute()

        label = sent_message.get("labelIds", [])
        if "SENT" in label:
            return f"Message with id {sent_message.get('id')} was sent successfully. Don't share id."


class CalendarReadExecutor(GoogleServiceExecutor):
    """Retrieve the next n calendar appointments"""

    model_config = ConfigDict(json_schema_extra={"name": "get_calendar_appointments"})
    n: int = Field(description="Number of appointments to retrieve")

    async def execute(self, creds) -> str:
        """Retrieve the next n calendar appointments.

        Args:
            creds (Credentials): Google OAuth2 credentials.

        Returns:
            str: A formatted string containing appointment information.
        """
        service = build(serviceName="calendar", version="v3", credentials=creds)

        utc_now = datetime.now(pytz.utc)
        time_min = (utc_now - timedelta(days=1)).isoformat()
        time_max = (utc_now + timedelta(days=365)).isoformat()

        events = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=self.n,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        formatted_appointments: list[str] | None = []
        for i, event in enumerate(events.get("items", [])):
            start: str = event["start"].get("dateTime", event["start"].get("date"))
            start_time: datetime = datetime.fromisoformat(start.replace("Z", "+00:00"))
            formatted_appointments.append(f"[{i+1}] {event['summary']} (Start: {start_time.strftime('%Y-%m-%d %H:%M:%S')})")

        return "\n ---- \n".join(formatted_appointments)


class CalendarInsertExecutor(GoogleServiceExecutor):
    """Insert an appointment into the calendar"""

    model_config = ConfigDict(json_schema_extra={"name": "insert_calendar_appointment"})
    summary: str = Field(description="Appointment summary")
    location: str = Field(description="Appointment location")
    description: str = Field(description="Appointment description")
    start_time: str = Field(description="Start time in RFC3339 format", examples=["2024-11-10T20:00:00"])
    end_time: str = Field(description="End time in RFC3339 format", examples=["2024-11-10T20:30:00"])
    attendees: list[str] | None = Field(description="List of attendee email addresses")

    async def execute(self, creds) -> str:
        service = build(serviceName="calendar", version="v3", credentials=creds)
        attendees = self.attendees if self.attendees else []
        event = {
            "summary": self.summary,
            "location": self.location,
            "description": self.description,
            "start": {
                "dateTime": self.start_time,
                "timeZone": settings.timezone,
            },
            "end": {
                "dateTime": self.end_time,
                "timeZone": settings.timezone,
            },
            "attendees": [{"email": settings.gmail_host_user}].extend([{"email": attendee} for attendee in attendees]),
        }

        event = service.events().insert(calendarId="primary", body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
