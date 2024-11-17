import json

import httpx
from decouple import config
from openai import AsyncOpenAI
from termcolor import colored

from .types import AnswerQuestion, ImageInfo, Question, RecordingInfo

sysyem_prompt_question_tpl = """
You are a helpful assistant. Please answer the user question in a concise way based on the provided article. There are additional sections that provide descriptions and context for the images and recordings used in the article.

<article>
{article}
</article>

<images_description>
{images}
</images_description>

<recordings_description>
{recordings}
</recordings_description>
"""
client = AsyncOpenAI(api_key=config("OPENAI_API_KEY"))


def _build_system_message(article: str, images: list[ImageInfo], recordings: list[RecordingInfo]):
    images_appendix = json.dumps([image.model_dump(exclude=["url"]) for image in images], indent=2)
    recordings_appendix = json.dumps([recording.model_dump(exclude=["url"]) for recording in recordings], indent=2)
    return {
        "role": "system",
        "content": sysyem_prompt_question_tpl.format(
            article=article, images=(images_appendix), recordings=(recordings_appendix)
        ),
    }


async def _ask_llm_question(
    question: str, article: str, images: list[ImageInfo], recordings: list[RecordingInfo]
) -> str:
    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[_build_system_message(article, images, recordings), {"role": "user", "content": question}],
    )
    response = completion.choices[0].message.content
    return response


def _asQuestion(line: str) -> Question:
    items = line.split("=")
    return Question(id=items[0], text=" ".join(items[1:]))


async def get_questions(url: str) -> list[Question]:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return [_asQuestion(line) for line in response.text.splitlines()]


async def get_answer(
    question: Question, article: str, images: list[ImageInfo], recordings: list[RecordingInfo]
) -> AnswerQuestion:
    print("Answering question:", colored(question.text, "light_blue"))
    answer = await _ask_llm_question(question.text, article, images, recordings)
    return AnswerQuestion(id=question.id, question=question.text, answer=answer)
