import json

from decouple import config
from openai import OpenAI
from termcolor import colored

system_prompt = """
Od teraz pomagasz pilotowi nawigować na podstawie uproszczonej mapy.
Twoja mapa to matryca z 16 miejscami (4 wiersze na 4 kolumny).
Każde miejsce na mapie ma swój krótki opis.

Twoim celem jest analiza opisu lotu i wskazanie nazwy docelowego miejsca.
Odpowiadaj w formie obiektu JSON.

{"thoughts": "twoja analiza", "final_place": "nazwa miejsce w którym kończy się lot" }

Każdy lot zaczyna się z miejsca "start".

<mapa>
<miejsce rząd="1" kolumna="1">start</miejsce>
<miejsce rząd="1" kolumna="2">trawa</miejsce>
<miejsce rząd="1" kolumna="3">drzewo</miejsce>
<miejsce rząd="1" kolumna="4">budynek</miejsce>

<miejsce rząd="2" kolumna="1">trawa</miejsce>
<miejsce rząd="2" kolumna="2">wiatrak</miejsce>
<miejsce rząd="2" kolumna="3">trawa</miejsce>
<miejsce rząd="2" kolumna="4">trawa</miejsce>

<miejsce rząd="3" kolumna="1">trawa</miejsce>
<miejsce rząd="3" kolumna="2">trawa</miejsce>
<miejsce rząd="3" kolumna="3">skała</miejsce>
<miejsce rząd="3" kolumna="4">dwa drzewa</miejsce>

<miejsce rząd="4" kolumna="1">góry</miejsce>
<miejsce rząd="4" kolumna="2">góry</miejsce>
<miejsce rząd="4" kolumna="3">samochód</miejsce>
<miejsce rząd="4" kolumna="4">jaskinia</miejsce>
</mapa>

"""

openai_client = OpenAI(api_key=config("OPENAI_API_KEY"))


def verify_flight(flight: str) -> str | None:
    print(colored("Verifying flight", "blue"), flight)
    completion = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": flight},
        ],
        response_format={"type": "json_object"},
    )
    response = completion.choices[0].message.content
    result = json.loads(response)
    print(colored("Analysis", "cyan"), result["thoughts"])
    print(colored("Place", "green"), result["final_place"])

    return result["final_place"] if result["final_place"] else None
