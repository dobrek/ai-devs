from decouple import config
from langfuse.decorators import observe
from langfuse.openai import AsyncOpenAI
from pydantic import BaseModel

from .types import IndexedTextFile, TextFile

system_prompt = """
<objective>
Extract keywords from the given user text that describe its content most effectively to ensure the output is as accurate and complete as possible.
</objective>

<rules>
- All keywords MUST be in Polish
- Focus on selecting words that capture the main themes or core concepts
- COLLECT ALL IMPORTANT OR ADDITIONAL facts and information mentioned in the text before generating the keywords
- The keywords should index persons, their jobs, roles, relations, locations, actions, memories, skills, used tools and other relevant entities
- Keywords should contain information about proper names, sector names, programming languages, tools, places, animals and other relevant entities mentioned in the text
- ONLY output in {{"keywords": [keywords for full-text search]}} JSON format
- Each keyword MUST BE a noun in the nominative case
- DO NOT use adjectives or verbs as keywords
</rules>
"""

client = AsyncOpenAI(api_key=config("OPENAI_API_KEY"))


class LlmKeywordsResponse(BaseModel):
    keywords: list[str]


@observe
async def _extract_keywords(text: str) -> list[str]:
    completion = await client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": text},
        ],
        response_format=LlmKeywordsResponse,
    )
    response = completion.choices[0].message.parsed
    return response.keywords


async def index_file(report: TextFile) -> IndexedTextFile:
    result = await _extract_keywords(report.text)
    return IndexedTextFile(name=report.name, text=report.text, keywords=result)
