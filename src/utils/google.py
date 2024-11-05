from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from src.settings import Settings

settings: Settings = Settings()


def get_credentials() -> Credentials:
    SCOPES = ["https://www.googleapis.com/auth/gmail.readonly", "https://www.googleapis.com/auth/calendar.readonly"]
    flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(str(settings.credentials_path), SCOPES)
    creds: Credentials = flow.run_local_server(port=0)
    return creds
