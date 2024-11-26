from openai import AsyncOpenAI

system_prompt = """
Pick the best identikit from the given examples.

- Add extra points for unique signs or features.
- Each example is given wrapped in the XML tag <identikit>.
- Only the text of the best identikit is should be returned, nothing else.
"""


async def pick_best_identikit(client: AsyncOpenAI, examples: list[str]) -> str:
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": "\n".join([f"<identikit>{example}</identikit>" for example in examples]),
            },
        ],
    )
    return completion.choices[0].message.content
