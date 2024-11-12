from abc import ABC, abstractmethod

from pydantic import BaseModel


class Tool(BaseModel, ABC):
    """Base class for all tools."""

    @abstractmethod
    def run(self):
        """Main functionality of the tool."""
        pass


class AsyncTool(BaseModel, ABC):
    """Base class for all async tools."""

    @abstractmethod
    async def run(self):
        """Main functionality of the tool."""
        pass
