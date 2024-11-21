import asyncio

from decouple import config
from termcolor import colored

from ai_dev3.utils.api_client import send_answer
from ai_dev3.utils.http import get_text

from .Investigator import Investigator
from .OpenAiService import OpenAiService

task_name = "loop"


async def task():
    ai_service = OpenAiService()
    text = await get_text(f"{config('CENTRALA_URL')}/dane/barbara.txt")
    response = await ai_service.extract_people_and_cities(text)
    investgator = Investigator(ignored_cities=response.cities, peoples=response.people, wanted="BARBARA")
    city = await investgator.search()
    if city is None:
        print(colored("No city found", "red"))
    else:
        print("City found", colored(city, "green"))
        send_answer(task=task_name, answer=city)


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()
