from pydantic import BaseModel
from datetime import date

class MemoryInput(BaseModel):
    text: str
    date: date
