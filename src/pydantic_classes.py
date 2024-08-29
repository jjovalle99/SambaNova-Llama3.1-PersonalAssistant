from typing import Any

from pydantic import BaseModel, Field


class Metadata(BaseModel):
    id: str
    created: int
    model: str
    system_fingerprint: str
    usage: dict[str, Any]
    finish_reason: str = Field(default="unknown")
