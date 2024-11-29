import json

from openai import AsyncOpenAI

system_prompt = """
The exclusive purpose of this prompt is to answer user questions succinctly using a provided web page context.

<prompt_rules>
- The AI must search for information within the provided context to answer the user's question.
- Analyze the context carefully and include your thoughts in the JSON output under "thoughts".
- The AI must return answers in the strict JSON format: `{{"thoughts": "put here your analysis", "answer": "answer to the user question, if answer can be found else leave this field empty"}}`.
- UNDER NO CIRCUMSTANCES should the AI generate an answer that is not found in the context.
- If the answer cannot be found in the context, leave the "answer" field empty.
</prompt_rules>

<context>
{context}
</context>
"""


async def look_for_an_answer(client: AsyncOpenAI, question: str, context: str) -> str | None:
    completion = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt.format(context=context)},
            {"role": "user", "content": question},
        ],
    )
    response = completion.choices[0].message.content
    result = json.loads(response)

    return result["answer"] if result["answer"] else None
