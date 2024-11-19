from pydantic import BaseModel


class TextFile(BaseModel):
    name: str
    text: str


class IndexedTextFile(BaseModel):
    name: str
    text: str
    keywords: list[str]
