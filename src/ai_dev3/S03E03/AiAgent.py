import json
from typing import Literal

from decouple import config
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic_core import from_json
from termcolor import colored

from .DbApiService import DbApiService

system_message = {
    "role": "system",
    "content": """
You are an expert in SQL, possessing extensive knowledge in constructing SQL queries to extract relevant information from databases. Your primary goal is to create a SQL query that answers the user question, execute it, and provide a very concise answer in text form. You can gather the necessary information by asking the user

- response only with followed JSON structure
{
 "thoughts": "Put here your thoughts and analysis",
 "action": "schema | sql_query | final_answer",
 "sql_query": "This is an optional field that contains a query to execute in order to gather more details from the database."
 "answer": "This is an optional field with a final answer to the user; please keep it as concise as possible. It could be just one word or one number or comma separated list with those elements. Replay with 'none' if answer can be given".
}

- use action "schema" to get a database schema.
- use action: "sql-query" to execute sql and get response from database.
- use action: "final-answer" to mark text in "answer" field as a final answer.
    """,
}


class LlmResponse(BaseModel):
    thoughts: str | None = None
    action: Literal["schema", "sql_query", "final_answer"]
    sql_query: str | None = None
    answer: str | None = None


class AiAgent:
    def __init__(self, max_tries: int = 4):
        self.client = AsyncOpenAI(api_key=config("OPENAI_API_KEY"))
        self.dbService = DbApiService(api_url=f"{config('CENTRALA_URL')}/apidb")
        self.messeges = [system_message]
        self.max_tries = max_tries

    async def _send_messages(self) -> LlmResponse:
        print("Asking Ai ...")
        completion = await self.client.chat.completions.create(model="gpt-4o", messages=self.messeges)
        response = completion.choices[0].message.content
        print("AI response", colored(response, "yellow"))
        self.messeges.append({"role": "system", "content": response})
        return LlmResponse.model_validate(from_json(response))

    async def answer(self, question: str) -> str | None:
        return await self._run_conversation(question)

    def _total_user_messages(self) -> int:
        return len([message for message in self.messeges if message["role"] == "user"])

    async def _run_conversation(self, text: str) -> str | None:
        self.messeges.append({"role": "user", "content": text})
        if self._total_user_messages() > self.max_tries:
            print(colored("Error - too many tries", "red"))
            return None
        response = await self._send_messages()
        if response.action == "final_answer":
            return response.answer
        action_result = await self._run_action(response)
        return await self._run_conversation(action_result)

    async def _run_action(self, response: LlmResponse) -> str:
        print("Running action", colored(response.action, "green"))
        if response.action == "final_answer":
            print(colored("Final answer", "green"))
            return response.answer
        if response.action == "schema":
            print(colored("Getting schema", "blue"))
            return await self.dbService.get_schema()
        if response.action == "sql_query":
            print(colored("Running query", "light_blue"))
            result = await self.dbService.query(response.sql_query)
            print("query result", colored(result, "light_blue"))
            return json.dumps(result)
        return "try again"

    def reset_chat(self):
        self.messeges = [system_message]
