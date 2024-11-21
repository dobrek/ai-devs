import httpx
from decouple import config
from termcolor import colored

api_key = config("API_KEY")


def _parse_response(response: dict) -> list[str]:
    if response.get("code") != 0:
        print(colored(response, "red"))
    if response.get("message") == "[**RESTRICTED DATA**]":
        return []
    return response["message"].split(" ") if response["code"] == 0 else []


class ApiService:
    def __init__(self, api_url: str = config("CENTRALA_URL")) -> None:
        self.api_url = api_url
        self.client = httpx.AsyncClient(base_url=api_url)

    async def people_from(self, city: str) -> list[str]:
        response = await self.client.post("/places", json={"query": city, "apikey": api_key})
        return _parse_response(response.json())

    async def cities_visited_by(self, person_name: str) -> list[str]:
        response = await self.client.post("/people", json={"query": person_name, "apikey": api_key})
        return _parse_response(response.json())
