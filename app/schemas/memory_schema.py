from datetime import date
from typing import Any, Optional

from pydantic import BaseModel


class MemoryInput(BaseModel):
    text: str
    date: date


class MemoryUpdate(BaseModel):
    text: str
    date: date
    gpt_analysis: Optional[dict[str, Any]] = None
    image_url: Optional[str] = None
