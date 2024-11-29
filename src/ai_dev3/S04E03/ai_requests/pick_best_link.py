from openai import AsyncOpenAI
from pydantic import TypeAdapter

from ai_dev3.utils.url import is_valid_url

from ..types import Link

system_prompt = """
From now on, determine which link is the most likely to direct users to the page containing the answer.

return only link nothing else

<links>
{context}
</links>
"""

links_list_adapter = TypeAdapter(list[Link])


def _build_context(links: list[Link]) -> str:
    return links_list_adapter.dump_json(links, indent=2)


async def pick_best_link(client: AsyncOpenAI, question: str, links: list[Link]) -> str | None:
    completion = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt.format(context=_build_context(links))},
            {"role": "user", "content": question},
        ],
    )
    url = completion.choices[0].message.content
    return url if is_valid_url(url) else None
