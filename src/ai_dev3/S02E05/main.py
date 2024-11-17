import asyncio

import httpx
from decouple import config
from markdownify import markdownify as md

from ai_dev3.utils.api_client import send_answer

from .images import describe_images
from .questions import get_answer, get_questions
from .recordings import describe_recordings

task_name = "arxiv"
base_url = f"{config('CENTRALA_URL')}/dane"
article_url = f"{base_url}/arxiv-draft.html"
questions_url = f"{config('CENTRALA_URL')}/data/{config('API_KEY')}/{task_name}.txt"


async def task():
    article = md(await _read_document(article_url), strip=["audio"], heading_style="ATX")

    images = await describe_images(article, base_url)
    recordings = await describe_recordings(article, base_url)
    questions = await get_questions(questions_url)
    results = await asyncio.gather(*[get_answer(question, article, images, recordings) for question in questions])

    send_answer(answer={item.id: item.answer for item in results}, task=task_name)


async def _read_document(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()
