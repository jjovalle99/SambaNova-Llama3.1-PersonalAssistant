from src.tools.base import AsyncTool
from src.tools.google_tools.credentials import GoogleCredsManager
from src.tools.google_tools.executors import GoogleServiceExecutor
from src.tools.google_tools.services import GoogleServices


class GoogleTool(AsyncTool):
    """Base class for Google tools."""

    creds_manager: GoogleCredsManager
    executor: GoogleServiceExecutor

    async def run(self) -> None:
        """Run the Google tool."""
        scopes = GoogleServices.get_all_scopes()
        creds = self.creds_manager.get_credentials(scopes=scopes)
        return await self.executor.execute(creds=creds)
