from datetime import datetime
from typing import Any

import pytz
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import Resource, build
from pydantic import BaseModel, ConfigDict

from src.settings import Settings
from src.utils.google import get_credentials

settings: Settings = Settings()
creds: Credentials = get_credentials()


class CalendarAppointments(BaseModel):
    """Retrieve the next 10 calendar appointments."""

    model_config = ConfigDict(json_schema_extra={"name": "get_calendar_appointments", "required": []})


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
