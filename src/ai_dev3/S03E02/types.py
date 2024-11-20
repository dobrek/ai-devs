from datetime import date
from uuid import UUID

from pydantic import BaseModel


class TextFile(BaseModel):
    name: str
    text: str


class ReportFile(BaseModel):
    id: UUID
    name: str
    text: str
    weapon: str
    date: date
