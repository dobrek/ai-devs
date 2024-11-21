import httpx


async def get_text(url: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text
