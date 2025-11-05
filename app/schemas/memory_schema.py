from pydantic import BaseModel
from typing import Optional
from datetime import date

class MemoryInput(BaseModel):
    text: str
    date: date

class MemoryUpdate(BaseModel):
    id: int
    text: str
    date: date
    gpt_analysis: Optional[str] = None
    image_url: Optional[str] = None