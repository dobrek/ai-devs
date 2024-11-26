import asyncio

from openai import AsyncOpenAI
from pydantic import BaseModel
from termcolor import colored

from ai_dev3.S04E01.actions.pick_best_identikit import pick_best_identikit

from .actions.check_image_quality import ImageQualityAction, check_image_quality
from .actions.create_identikit import Identikit, create_identikit
from .actions.extract_images import extract_images
from .PhotosApi import NotSoSmartPhotoApi


class InvestigatorError(Exception):
    MISSING_IMAGE_URL = "Image URL is missing: {name}"
    IMAGE_REPAIR_FAILED = "Image {name} was not repaired"
    UNKNOWN_ACTION = "Unknown action: {action}"

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Image(BaseModel):
    url: str | None
    name: str


class Investigator:
    def __init__(self, open_ai_key: str, api_key: str, api_url: str) -> None:
        self.photo_api_client = NotSoSmartPhotoApi(api_key, api_url)
        self.openai_client = AsyncOpenAI(api_key=open_ai_key)

    async def get_images(self) -> list[Image]:
        print(colored("Getting images", "cyan"))
        response = await self.photo_api_client.get_images()
        all_images = await self._parse_as_images(response)
        return [image for image in all_images if image.url]

    async def validate(self, images: list[Image]) -> list[Image]:
        return await asyncio.gather(*[self.validate_image(image) for image in images])

    async def validate_image(self, image: Image, iteration: int = 1) -> Image:
        print(colored("Validate image", "cyan"), image.name)
        if iteration > 3:
            print(f"Failed to get a valid image {image.name} after {iteration} attempts")
            return None
        quality_action = await check_image_quality(self.openai_client, image.url)
        if quality_action == "OK":
            return image
        fixed_image = await self._fix_image(image, quality_action)
        return await self.validate_image(fixed_image, iteration + 1)

    async def _fix_image(self, image: Image, action: ImageQualityAction) -> Image:
        print(colored("Fixing image ...", "cyan"), image.name, action)
        if not image.url:
            raise InvestigatorError(InvestigatorError.MISSING_IMAGE_URL.format(name=image.name))
        action_map = {
            "REPAIR": self.photo_api_client.repair_image,
            "DARKEN": self.photo_api_client.darken_image,
            "BRIGHTEN": self.photo_api_client.brighten_image,
        }
        if action == "OK":
            return image
        if action in action_map:
            response = await action_map[action](image.name)
            fixed_image = await self._as_new_image(response, image)
            print(colored("Fix result", "cyan"), fixed_image.url, response)
            return fixed_image
        raise InvestigatorError(InvestigatorError.UNKNOWN_ACTION.format(name=image.name))

    async def _create_identikit(self, image: Image) -> Identikit:
        print(colored("Creating identikit", "cyan"), image)
        response = await create_identikit(self.openai_client, image.url)
        return response

    async def identikit(self, images: list[Image]) -> str:
        all_identikits = await asyncio.gather(*[self._create_identikit(image) for image in images])
        descriptions = [identikit.text for identikit in all_identikits if identikit.text]
        print(colored("Picking best identikit descriptions", "cyan"), descriptions)
        return await pick_best_identikit(self.openai_client, descriptions)

    async def _as_new_image(self, api_response: str, base_image: Image) -> Image:
        images = await self._parse_as_images(api_response)
        if not images:
            raise InvestigatorError(InvestigatorError.IMAGE_REPAIR_FAILED.format(name=base_image.name))
        return _normalize_image(images[0], _get_base_url(base_image.url))

    async def _parse_as_images(self, response: str) -> list[Image]:
        print(colored("Extract image", "cyan"), response)
        image_names = await extract_images(self.openai_client, response)
        return [_build_image(name_or_url) for name_or_url in image_names]


def _get_base_url(url: str) -> str:
    return "/".join(url.split("/")[:-1])


def _is_url_valid(url: str) -> bool:
    return url.startswith("http")


def _build_image(image: str) -> Image:
    url = image if _is_url_valid(image) else None
    return Image(url=url, name=image.split("/")[-1])


def _normalize_image(image: Image, base_url: str) -> Image:
    if image.url is None:
        return Image(url=f"{base_url}/{image.name}", name=image.name)
    return image
