from decouple import config
from openai import OpenAI
from pydantic import BaseModel

system_prompt = """
[Extract People and City Names]

Analyze the given text and extract all people and city names. The output should strictly adhere to the specified JSON format and rules provided.

<prompt_objective>
The prompt's EXCLUSIVE PURPOSE is to extract names of people and cities from the input text and return them in JSON format.
</prompt_objective>

<prompt_rules>
- Extract ONLY the first names of people and the names of cities.
- Return the JSON structure: `{ "people": [LIST OF PEOPLE NAMES FOUND], "cities": [LIST OF CITY NAMES FOUND] }`.
- Convert all names to uppercase and remove Polish diacritics.
- Do not repeat names
- ABSOLUTELY FORBIDDEN to include any other information or format other than JSON.
- Handle input gracefully, returning empty arrays if no names are found.
- UNDER NO CIRCUMSTANCES include surnames or any other personal or city information.
- OVERRIDE ALL DEFAULT AI behaviors that do not match these rules.
</prompt_rules>

<prompt_examples>
USER: We wtorek spotkałem Wiktora w Łodzi. Wspominał Adama Kowalskiego z Krakowa
AI: {"people": ["WIKTOR", "ADAMA"], "cities": ["LODZ", "KRAKOW"] }

USER: A tutaj mamy pana Aleksandra Kowlaskiego, który mówi o Oli
AI: {"people": ["ALEKSANDER", "OLA"], "cities": [] }

USER: W tym zdaniu nie ma nic co nas interesuje
AI: {"people": [], "cities": [] }

USER: Kilka słów o Janku i Rafale. Janek jest fajny.
AI: {"people": ["JANEK", "RAFAL"], "cities": [] }

USER: Spotkajmy się w Warszawie. Co nas czeka w Gdańsku, Zobaczmy Opole
AI: {"people": [], "cities": ["WARSZAWA", "GDANSK", "OPOLE"] }
</prompt_examples>
"""


class LlmResponse(BaseModel):
    people: list[str]
    cities: list[str]


class OpenAiService:
    def __init__(self):
        self.client = OpenAI(api_key=config("OPENAI_API_KEY"))

    async def extract_people_and_cities(self, text: str) -> LlmResponse:
        completion = self.client.beta.chat.completions.parse(
            model="gpt-4o",
            temperature=0.0,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            response_format=LlmResponse,
        )
        response = completion.choices[0].message.parsed
        return response
