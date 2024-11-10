from enum import Enum

from pydantic import BaseModel


class GoogleService(BaseModel):
    """Google service."""

    name: str
    scopes: list[str]


class GoogleServices(Enum):
    """Allowed Google services."""

    GMAIL = GoogleService(
        name="Gmail", scopes=["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/gmail.send"]
    )
    CALENDAR = GoogleService(
        name="Calendar",
        scopes=[
            "https://www.googleapis.com/auth/calendar",
        ],
    )

    @classmethod
    def get_all_scopes(cls):
        scopes = set()
        for service in cls:
            scopes.update(service.value.scopes)
        return list(scopes)
