from openai import AsyncOpenAI
from termcolor import colored

from .ai_requests.look_for_an_answer import look_for_an_answer
from .ai_requests.pick_best_link import pick_best_link
from .PageScrapper import PageScrapper


class AiAgent:
    def __init__(self, open_ai_key: str, base_url: str) -> None:
        self.scrapper = PageScrapper(base_url)
        self.client = AsyncOpenAI(api_key=open_ai_key)

    async def find_answer(self, question: str, url: str, tries: int = 10) -> str | None:
        print(colored("Finding answer", "cyan"), question, url, tries)
        if tries == 0:
            print(colored("Max tries reached", "red"))
            return None
        page = await self.scrapper.scrape_page(url)
        answer = await look_for_an_answer(self.client, question=question, context=page.text)
        if answer:
            print(colored("Answer found", "green"), answer)
            return answer
        print(colored("No answer found - picking link", "blue"))
        link = await pick_best_link(self.client, question=question, links=page.links)
        if link:
            print(colored("Following link", "green"), link)
            return await self.find_answer(question, link, tries - 1)
        else:
            print(colored("No answer found and no links to follow", "red"))
            return None
