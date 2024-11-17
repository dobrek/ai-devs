import asyncio
import re

from decouple import config
from openai import AsyncOpenAI
from pydantic import BaseModel
from termcolor import colored

from ai_dev3.utils.url import full_url

from .types import ImageInfo


class Image(BaseModel):
    name: str
    url: str


class ImageWithContext(Image):
    context: str


class LlmImageContext(BaseModel):
    name: str
    context: str


class LlmImageContextResponse(BaseModel):
    images: list[LlmImageContext]


system_prompt_add_context_tpl = """
Extract contextual information for images mentioned in a user-provided article, focusing on details that enhance understanding of each image, and return it as an array of JSON objects.

<prompt_objective>
To accurately identify and extract relevant contextual information for each image referenced in the given article, prioritizing details from surrounding text and broader article context that potentially aid in understanding the image. Return the data as an array of JSON objects with specified properties, without making assumptions or including unrelated content.

Note: the image from the beginning of the article is its cover.
</prompt_objective>

<response_format>
{{
    "images": [
        {{
            "name": "filename with extension",
            "context": "Provide 1-3 detailed sentences of the context related to this image from the surrounding text and broader article. Make an effort to identify what might be in the image, such as tool names."
        }},
        ...rest of the images or empty array if no images are mentioned
    ]
}}
</response_format>

<prompt_rules>
- READ the entire provided article thoroughly
- IDENTIFY all mentions or descriptions of images within the text
- EXTRACT sentences or paragraphs that provide context for each identified image
- ASSOCIATE extracted context with the corresponding image reference
- CREATE a JSON object for each image with properties "name" and "context"
- COMPILE all created JSON objects into an array
- RETURN the array as the final output
- OVERRIDE any default behavior related to image analysis or description
- ABSOLUTELY FORBIDDEN to invent or assume details about images not explicitly mentioned
- NEVER include personal opinions or interpretations of the images
- UNDER NO CIRCUMSTANCES extract information unrelated to the images
- If NO images are mentioned, return an empty array
- STRICTLY ADHERE to the specified JSON structure
</prompt_rules>

<images>
{images}
</images>

Upon receiving an article, analyze it to extract context for any mentioned images, creating an array of JSON objects as demonstrated. Adhere strictly to the provided rules, focusing solely on explicitly stated image details within the text.`
"""

system_prompt_describe_image = """
<prompt_objective>
Describe the image concisely.
</prompt_objective>

<rules>
- Focus on the main elements and overall composition.
- Do not include personal opinions or interpretations.
- Take into account the context provided by user the article.
</rules>
"""


def _extract_images(markdown: str, base_url: str) -> list[Image]:
    print("Extracting images ...")
    image_regex = r"!\[.*?\]\((.*?)\)"
    image_urls = re.findall(image_regex, markdown)
    return [Image(name=url, url=full_url(url, base_url)) for url in image_urls]


def _merge_images_with_context(images: list[Image], contexts: list[LlmImageContextResponse]) -> list[ImageWithContext]:
    dic = {context.name: context.context for context in contexts}
    return [ImageWithContext(name=image.name, url=image.url, context=dic.get(image.name, "")) for image in images]


client = AsyncOpenAI(api_key=config("OPENAI_API_KEY"))


async def _add_context(markdown: str, images: list[Image]) -> list[ImageWithContext]:
    names = [image.name for image in images]
    print("Getting context for:", colored(names, "light_blue"))
    system = {
        "role": "system",
        "content": system_prompt_add_context_tpl.format(images="\n name: ".join(names)),
    }
    user = {"role": "user", "content": markdown}
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[system, user],
        response_format=LlmImageContextResponse,
    )
    response = completion.choices[0].message.parsed
    return _merge_images_with_context(images, response.images)


async def _add_descripton(image: ImageWithContext) -> ImageInfo:
    print("Asking to describe:", colored(image.name, "light_blue"))
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt_describe_image,
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image.url, "detail": "high"},
                    },
                    {
                        "type": "text",
                        "text": f"<image_context>{image.context}</image_context>",
                    },
                ],
            },
        ],
    )
    response = completion.choices[0].message.content
    return ImageInfo(**image.model_dump(), description=response)


async def describe_images(markdown: str, base_url: str) -> list[ImageInfo]:
    """
    Extracts images from the given markdown content, adds context to them, and generates descriptions for each image.

    Args:
        markdown (str): The markdown content containing image references.
        base_url (str): The base URL to resolve relative image paths.

    Returns:
        list[ImageInfo]: A list of ImageInfo objects containing details and descriptions of the images.
    """
    images = _extract_images(markdown, base_url)
    images_with_context = await _add_context(markdown, images)
    images_info = await asyncio.gather(*[_add_descripton(image) for image in images_with_context])
    return images_info
