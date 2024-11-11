from collections.abc import Iterable

from decouple import config
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def transcribe(file_path: str, promopt: str | None = None) -> str:
    with open(file_path, "rb") as audio_file:
        return client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text", prompt=promopt
        )


def send_chat_messages(messages: Iterable[ChatCompletionMessageParam], model: str) -> str:
    completion = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    return completion.choices[0].message.content
