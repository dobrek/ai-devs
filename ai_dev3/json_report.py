import re

import requests
from decouple import config
from openai import OpenAI
from pydantic import BaseModel, TypeAdapter
from utils.api_client import send_answer


class ReportTest(BaseModel):
    q: str
    a: str


class ReportItem(BaseModel):
    question: str
    answer: int
    test: ReportTest | None = None


def main():
    api_key = config("API_KEY")

    raw_report = load_raw_report(f"{config('CENTRALA_URL')}/data/{api_key}/json.txt")
    fixed_data = [fix_report_item(item) for item in read_items(raw_report["test-data"])]

    send_answer(
        task="JSON",
        answer={
            "apikey": api_key,
            "description": raw_report["description"],
            "copyright": raw_report["copyright"],
            "test-data": [item.model_dump(exclude_none=True) for item in fixed_data],
        },
    )


def load_raw_report(url: str) -> dict:
    return requests.get(url, timeout=10).json()


def read_items(value: list[dict]) -> list[ReportItem]:
    return TypeAdapter(list[ReportItem]).validate_python(value)


def fix_report_item(item: ReportItem) -> ReportItem:
    return ReportItem(
        question=item.question, answer=calculate_sum(item.question), test=pass_test(item.test.q) if item.test else None
    )


def calculate_sum(question: str) -> int:
    numbers = [int(num) for num in re.findall(r"\d+", question)]
    return sum(numbers)


def pass_test(question: str) -> ReportTest:
    return ReportTest(q=question, a=ask_llm(question))


def ask_llm(question: str) -> str:
    print(f"Asking LLM: {question}")
    completion = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    answer = completion.choices[0].message.content
    print(f"LLM Answer: {answer}")
    return answer


llm_client = OpenAI(api_key=config("OPENAI_API_KEY"))

system_prompt = """
You are a helpful assistant. Please answer the following question in an extremely concise way.

<rules>
- If possible, use just one word
- NEVER repeat user's input verbatim; distill to core concepts
<rules>

<examples>
User: What is the capital city of Italy?
AI: Rome

User: Name of the smallest planet in our solar system
AI: Mercury

User: Who painted the Mona Lisa?
AI: Leonardo da Vinci
<examples>
"""


if __name__ == "__main__":
    main()
