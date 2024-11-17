import requests
from decouple import config
from openai import OpenAI
from termcolor import colored

from ai_dev3.utils.api_client import send_answer


def _get_text() -> str:
    text_url = f"{config('CENTRALA_URL')}/data/{config('API_KEY')}/cenzura.txt"
    raw_text = requests.get(text_url, timeout=10).text
    return raw_text


def _censor_text(text: str) -> str:
    censored_text = _ask_llm(text).replace("XXX", "CENZURA").strip()
    print("Censored:", colored(censored_text, "blue"))
    return censored_text


def _ask_llm(question: str) -> str:
    print("To LLM:", colored(question, "cyan"))
    completion = OpenAI(base_url="http://localhost:1234/v1").chat.completions.create(
        model="gemma-2-2b-it",
        temperature=0.0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
    )
    answer = completion.choices[0].message.content
    print("From LLM:", colored(answer, "blue"))
    return answer


system_prompt = """
Act like a censorship. Find and replace all sensitive information like name, city, address, and age with the word "XXX".

<examples>
USER: Tożsamość podejrzanego: Janek Wiśniewski. Zamieszkały we Szczecinie na ul. Porannej 21. Wiek: 30 lat.
AI: Tożsamość podejrzanego: XXX. Zamieszkały we XXX na ul. XXX. Wiek: XXX lat.

USER: Osoba: Anna Wiśniewska. Zamieszkały we Rzeszowie na ulicy Porannej 21. Wiek: 30 lat.
AI: Osoba: XXX. Zamieszkały we XXX na ulicy XXX. Wiek: XXX lat.

USER: Dane personalne: Damian Kuzniak. Adres: Ligota, ul. Zielona 4a. Wiek: 43 lata.
AI: Dane personalne: XXX. Adres: XXX, ul. XXX. Wiek: XXX lata.

USER: Dane personalne podejrzanego: Alicja Górska. Przebywa w Zielonej Górze, ul. Akacjowa 7. Ma 34 lata.
AI: Dane personalne podejrzanego: XXX. Przebywa w XXX, ul. XXX. Ma XXX lata.

USER: Dane osoby podejrzanej: Ania Wyszkoń. Zamieszkała w Opolu przy ulicy Ciemnej 5. Ma 28 lat.
AI: Dane osoby podejrzanej: XXX. Zamieszkała w XXX przy ulicy XXX. Ma XXX lat.
</examples>
"""


def task() -> None:
    raw_text = _get_text()
    censored_text = _censor_text(raw_text)
    send_answer(task="CENZURA", answer=censored_text)


if __name__ == "__main__":
    task()
