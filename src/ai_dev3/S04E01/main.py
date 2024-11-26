import asyncio

from decouple import config
from termcolor import colored

from ai_dev3.utils.api_client import send_answer

from .Investigator import Investigator


async def task():
    api_key = config("API_KEY")
    api_url = config("CENTRALA_URL")
    open_ai_key = config("OPENAI_API_KEY")

    investigator = Investigator(api_key=api_key, api_url=api_url, open_ai_key=open_ai_key)
    images = await investigator.get_images()
    fixed_images = await investigator.validate(images)
    identikit = await investigator.identikit(fixed_images)

    print(colored("Identikit", "green"), identikit)
    send_answer(task="photos", answer=identikit)


def main():
    asyncio.run(task())


if __name__ == "__main__":
    main()
