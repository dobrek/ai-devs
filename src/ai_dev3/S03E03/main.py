import asyncio

from ai_dev3.utils.api_client import send_answer

from .AiAgent import AiAgent

task_name = "database"
question = "które aktywne datacenter (DC_ID) są zarządzane przez pracowników, którzy są na urlopie (is_active=0)"


async def task():
    aiAgent = AiAgent(max_tries=4)
    answer = await aiAgent.answer(question)
    send_answer(task="database", answer=[item.strip() for item in answer.split(",")])


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()
