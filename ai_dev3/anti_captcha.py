import re

import requests
from decouple import config
from openai import OpenAI
from parsel import Selector


def main() -> None:
    print("Task ANTY-CAPTCHA")
    login_url = config("ANTI_CAPTCHA_LOGIN_URL")

    page = read_page(login_url)
    question = extract_question(page)
    answer = ask_llm(question)
    secure_page = login(url=login_url, captcha=answer)
    flag = extract_flag(secure_page)

    print(f"Result: {flag}")


llm_client = OpenAI(api_key=config("OPENAI_API_KEY"))


def read_page(url: str) -> str:
    print(f"Reading page: {url}")
    return requests.get(url, timeout=10).text


def extract_question(html: str) -> str:
    question = Selector(text=html).css("#human-question::text").getall().pop()
    print(f"Extracted question: {question}")
    return question


def ask_llm(question: str) -> str:
    print(f"Asking LLM: {question}")
    completion = llm_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Please answer the following question in one word.",
            },
            {"role": "user", "content": question},
        ],
    )
    answer = completion.choices[0].message.content
    print(f"LLM Answer: {answer}")
    return answer


def login(url: str, captcha: str) -> str:
    response = requests.post(url, data={"username": "tester", "password": "574e112a", "answer": captcha}, timeout=10)
    return response.text


def extract_flag(html: str) -> str | None:
    pattern = r"\{\{FLG:(.*?)\}\}"
    matches = re.findall(pattern, html)
    print(f"Extracted flags: {matches}")
    return matches[0] if matches else None


if __name__ == "__main__":
    main()
