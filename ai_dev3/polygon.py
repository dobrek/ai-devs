import requests
from decouple import config


def main() -> None:
    print("Task POLIGON")

    content = requests.get("https://poligon.aidevs.pl/dane.txt", timeout=10).text
    text_lines = content.splitlines()
    print(f"lines: {text_lines}")

    data = {"task": "POLIGON", "answer": text_lines, "apikey": config("API_KEY")}
    response = requests.post("https://poligon.aidevs.pl/verify", json=data, timeout=10)
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print("Error during verification")


if __name__ == "__main__":
    main()
