from collections.abc import Iterable

from decouple import config
from openai import NOT_GIVEN, NotGiven, OpenAI
from openai.types import ResponseFormatJSONObject
from openai.types.chat import ChatCompletionMessageParam

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def transcribe(file_path: str, promopt: str | None = None) -> str:
    with open(file_path, "rb") as audio_file:
        return client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text", prompt=promopt
        )


def send_chat_messages(
    messages: Iterable[ChatCompletionMessageParam],
    model: str,
    response_format: ResponseFormatJSONObject | NotGiven = NOT_GIVEN,
) -> str:
    completion = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    return completion.choices[0].message.content
