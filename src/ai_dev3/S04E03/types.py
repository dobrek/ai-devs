from pydantic import BaseModel


class Question(BaseModel):
    id: str
    text: str


class Link(BaseModel):
    text: str
    href: str
    title: str | None


class ScrapedPage(BaseModel):
    url: str
    questions: list[Question]
    links: list[Link]
