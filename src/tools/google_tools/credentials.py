import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from pydantic import BaseModel, Field


class GoogleCredsConfig(BaseModel):
    """Configuration for Google credentials."""

    client_secrets_path: Path
    token_path: Path = Field(default=Path("token.json"))


class GoogleCredsManager(BaseModel):
    """Class to obtain Google credentials."""

    creds_config: GoogleCredsConfig

    def get_credentials(self, scopes: list[str]) -> Credentials:
        """Get Google credentials.

        Args:
            scopes (list[str]): The scopes to request.

        Returns:
            Credentials: The Google credentials.
        """
        creds: Credentials | None = None

        # The file token.json stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists(path=self.creds_config.token_path):
            creds = Credentials.from_authorized_user_file(filename=self.creds_config.token_path, scopes=scopes)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(request=Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    client_secrets_file=self.creds_config.client_secrets_path, scopes=scopes
                )
                creds = flow.run_local_server(port=0)
                # Save the credentials for the next run
                with open(file=self.creds_config.token_path, mode="w") as token:
                    token.write(creds.to_json())

        return creds
