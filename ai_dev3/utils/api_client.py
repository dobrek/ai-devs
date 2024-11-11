import requests
from decouple import config
from termcolor import colored

answer_api_url = f"{config('CENTRALA_URL')}/report"


def send_answer(answer: dict | str, task: str, url=answer_api_url) -> None:
    data = {
        "apikey": config("API_KEY"),
        "task": task,
        "answer": answer,
    }
    print("Sending answer:", colored(data["answer"], "blue"))
    response = requests.post(url, json=data, timeout=10)
    result = response.json()
    if response.status_code == 200 and result["message"] is not None:
        print(colored(result["message"], "green"))
    else:
        print("Error during verification", colored(result, "red"))
