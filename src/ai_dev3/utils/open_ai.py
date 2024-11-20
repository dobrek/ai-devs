from collections.abc import Awaitable, Callable, Iterable

from decouple import config
from openai import NOT_GIVEN, AsyncOpenAI, NotGiven, OpenAI
from openai.types import ResponseFormatJSONObject
from openai.types.chat import ChatCompletionMessageParam
from termcolor import colored

client = OpenAI(api_key=config("OPENAI_API_KEY"))


def transcribe(file_path: str, promopt: str | None = None) -> str:
    print("transcribing ...", colored(file_path, "cyan"))
    with open(file_path, "rb") as audio_file:
        text = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text", prompt=promopt
        )
        print("transcribe:", colored(text, "green"))
        return text


def send_chat_messages(
    messages: Iterable[ChatCompletionMessageParam],
    model: str,
    response_format: ResponseFormatJSONObject | NotGiven = NOT_GIVEN,
) -> str:
    completion = client.chat.completions.create(model=model, messages=messages, response_format=response_format)
    return completion.choices[0].message.content


def generate_image(prompt: str, width: int, height: int, model: str = "dall-e-3") -> str:
    print("Prompt:", colored(prompt, "cyan"))
    print("Generating ...")
    response = client.images.generate(
        model=model,
        prompt=prompt,
        n=1,
        size=f"{width}x{height}",
        response_format="url",
    )
    print("Generated image:", colored(response.data, "blue"))
    return response.data[0].url


async def create_embeddings(text: str, client: AsyncOpenAI) -> list[float]:
    response = await client.embeddings.create(
        model="text-embedding-3-large",
        input=text,
    )
    return response.data[0].embedding


EmbeddingsFunction = Callable[[str], Awaitable[list[float]]]


def embeddings_function(client: AsyncOpenAI) -> EmbeddingsFunction:
    async def _embeddings(text: str) -> list[float]:
        return await create_embeddings(text, client)

    return _embeddings
