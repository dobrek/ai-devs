import asyncio

from decouple import config

from ai_dev3.utils.api_client import send_answer
from ai_dev3.utils.http import get_json

from .AiAgent import AiAgent
from .types import Question


async def _get_questions() -> list[Question]:
    question_url = f"{config('CENTRALA_URL')}/data/{config('API_KEY')}/softo.json"
    data = await get_json(question_url)
    return [Question(id=key, text=value) for key, value in data.items()]


async def process_questions():
    questions = await _get_questions()
    ai_agent = AiAgent(config("OPENAI_API_KEY"), config("SOFTO_URL"))
    answers = {}
    for question in questions:
        answer = await ai_agent.find_answer(question.text, config("SOFTO_URL"))
        answers[question.id] = answer

    send_answer(task="softo", answer=answers)


def main():
    asyncio.run(process_questions())


if __name__ == "__main__":
    main()
