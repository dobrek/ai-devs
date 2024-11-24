import asyncio

import httpx
from decouple import config
from termcolor import colored


class DbApiServiceError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class DbApiService:
    def __init__(self, api_url: str) -> None:
        self.api_url = api_url
        self.client = httpx.AsyncClient(base_url=api_url)

    async def get_tables(self) -> list[str]:
        tabel_name_key = "Tables_in_banan"
        result = await self.query("show tables")
        return [item.get(tabel_name_key) for item in result if item.get(tabel_name_key)]

    async def query(self, query: str) -> dict:
        print("query:", colored(query, "light_blue"))
        result = (
            await self.client.post("/", json={"task": "database", "apikey": config("API_KEY"), "query": query})
        ).json()
        if result["reply"] is None:
            raise DbApiServiceError(result["error"])
        return result["reply"]

    async def get_table_definition(self, tabel: str) -> str:
        result = await self.query(f"show create table {tabel}")
        return result[0].get("Create Table")

    async def get_schema(self) -> dict:
        tables = await self.get_tables()
        definitions = await asyncio.gather(*[self.get_table_definition(table) for table in tables])
        return "\n\n".join(definitions)
