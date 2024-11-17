from pydantic import BaseModel


class Question(BaseModel):
    id: str
    text: str


class AnswerQuestion(BaseModel):
    id: str
    question: str
    answer: str


class RecordingInfo(BaseModel):
    name: str
    url: str
    description: str


class ImageInfo(BaseModel):
    name: str
    url: str
    context: str
    description: str
