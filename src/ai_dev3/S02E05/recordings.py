import asyncio
import re
import tempfile

import httpx
from decouple import config
from openai import AsyncOpenAI
from pydantic import BaseModel
from termcolor import colored

from ai_dev3.utils.url import full_url

from .types import RecordingInfo


class RecordingLink(BaseModel):
    name: str
    url: str


class DownloadedRecording(RecordingLink):
    name: str
    url: str
    file_path: str


def _extract_links(markdown: str, base_url) -> list[RecordingLink]:
    print("Extracting recording links ...")
    audio_regex = r"\[.*?\]\((.*?\.mp3)\)"
    audio_urls = re.findall(audio_regex, markdown)
    return [RecordingLink(name=url, url=full_url(url, base_url)) for url in audio_urls]


async def _download_file(link: RecordingLink, folder: str) -> DownloadedRecording:
    print("Downloading:", colored(link.url, "light_blue"))
    async with httpx.AsyncClient() as client:
        response = await client.get(link.url)
        file_path = f"{folder}/{link.name.replace('/', '_')}"
        with open(file_path, "wb") as file:
            file.write(response.content)
        return DownloadedRecording(name=link.name, url=link.url, file_path=file_path)


client = AsyncOpenAI(api_key=config("OPENAI_API_KEY"))


async def transcibe(recording: DownloadedRecording) -> RecordingInfo:
    print("Transcribing ...", colored(recording.file_path, "cyan"))
    with open(recording.file_path, "rb") as audio_file:
        text = await client.audio.transcriptions.create(model="whisper-1", file=audio_file, response_format="text")
        return RecordingInfo(name=recording.name, url=recording.url, description=text)


async def describe_recordings(markdown: str, base_url: str) -> list[RecordingInfo]:
    """
    Extracts links from the provided markdown, downloads the recordings, and transcribes them.

    Args:
        markdown (str): The markdown content containing the recording links.
        base_url (str): The base URL to resolve relative links.

    Returns:
        list[RecordingInfo]: A list of RecordingInfo objects containing the transcribed recordings.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        links = _extract_links(markdown, base_url)
        downloaded = await asyncio.gather(*[_download_file(link, tmp_dir) for link in links])
        return await asyncio.gather(*[transcibe(recording) for recording in downloaded])
