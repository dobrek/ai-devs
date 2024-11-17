import re

import requests
from decouple import config
from parsel import Selector

from ai_dev3.utils.open_ai import send_chat_messages


def _read_page(url: str) -> str:
    print(f"Reading page: {url}")
    return requests.get(url, timeout=10).text


def _extract_question(html: str) -> str:
    question = Selector(text=html).css("#human-question::text").getall().pop()
    print(f"Extracted question: {question}")
    return question


def _ask_llm(question: str) -> str:
    print(f"Asking LLM: {question}")
    answer = send_chat_messages(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Please answer the following question in one word.",
            },
            {"role": "user", "content": question},
        ],
    )
    print(f"LLM Answer: {answer}")
    return answer


def _login(url: str, captcha: str) -> str:
    response = requests.post(url, data={"username": "tester", "password": "574e112a", "answer": captcha}, timeout=10)
    return response.text


def _extract_flag(html: str) -> str | None:
    pattern = r"\{\{FLG:(.*?)\}\}"
    matches = re.findall(pattern, html)
    print(f"Extracted flags: {matches}")
    return matches[0] if matches else None


def main() -> None:
    print("Task ANTY-CAPTCHA")
    login_url = config("ANTI_CAPTCHA_LOGIN_URL")

    page = _read_page(login_url)
    question = _extract_question(page)
    answer = _ask_llm(question)
    secure_page = _login(url=login_url, captcha=answer)
    flag = _extract_flag(secure_page)

    print(f"Result: {flag}")


if __name__ == "__main__":
    main()
