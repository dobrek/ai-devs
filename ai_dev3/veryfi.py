import re

import requests
from decouple import config
from openai import OpenAI
from pydantic import BaseModel
from termcolor import colored


class RobotMessage(BaseModel):
    msg_id: str
    text: str


class LllResponse(BaseModel):
    question: str
    answer: str


def main():
    auth_message = send_message_to_robot(RobotMessage(msg_id="0", text="READY"))
    answer = ask_llm(auth_message.text)
    response = send_message_to_robot(RobotMessage(msg_id=auth_message.msg_id, text=answer))
    if response:
        print("Received flag", colored(extract_flag(response.text), "white", "on_green"))
    else:
        print(colored("Unfriendly robot.", "red"))


def send_message_to_robot(message: RobotMessage, url: str = "https://xyz.ag3nts.org/verify") -> RobotMessage | None:
    data = {"msgID": message.msg_id, "text": message.text}
    print("To Robot:", colored(data, "blue"))
    response = requests.post(url, json=data, timeout=10).json()
    print("From Robot:", colored(response, "green"))
    return RobotMessage(msg_id=f"{response['msgID']}", text=response["text"]) if response["msgID"] else None


def ask_llm(question: str) -> str:
    print("Asking LLM:", colored(question, "blue"))
    completion = llm_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        response_format=LllResponse,
    )
    response = completion.choices[0].message.parsed
    print("LLM answered:", colored(response, "green"))
    return response.answer


def extract_flag(content: str) -> str | None:
    pattern = r"\{\{FLG:(.*?)\}\}"
    matches = re.findall(pattern, content)
    return matches[0] if matches else None


llm_client = OpenAI(api_key=config("OPENAI_API_KEY"))

system_prompt = """
From now on, focus on generating concise pair of question and answer.

<objective>
Create a {"question": "extracted question from user", "answer": "one word answer"} JSON.
</objective>

<rules>
- Include "question" property first, followed by "answer" property
- "question" should contain question that was found in the given text
- "question" has to be in english
- "answer" should be one word in english
- use given facts to provide the answer
- NEVER repeat user's input verbatim; distill to core concepts
</rules>

<facts>
- the capital of Poland is Krakow
- the known number from the book Hitchhiker's Guide to the Galaxy is 69
- the current year is 1999
</facts>
"""

if __name__ == "__main__":
    main()
