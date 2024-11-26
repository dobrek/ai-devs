import httpx
from termcolor import colored


class PhotosApiError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class NotSoSmartPhotoApi:
    def __init__(self, api_key: str, api_url: str):
        self.client = httpx.AsyncClient(base_url=api_url)
        self.api_key = api_key

    async def _request(self, message: str) -> str:
        print(colored("PhotoApi", "light_blue"), message)
        result = (
            await self.client.post("/report", json={"task": "photos", "apikey": self.api_key, "answer": message})
        ).json()
        print(colored("PhotoApi", "yellow"), result["message"])
        if result["code"] < 0:
            raise PhotosApiError(result["message"])
        return result["message"]

    async def get_images(self) -> str:
        return await self._request("START")

    async def repair_image(self, image_name: str) -> str:
        return await self._request(f"REPAIR {image_name}")

    async def darken_image(self, image_name: str) -> str:
        return await self._request(f"DARKEN {image_name}")

    async def brighten_image(self, image_name: str) -> str:
        return await self._request(f"BRIGHTEN {image_name}")
