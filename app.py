import requests
from decouple import config


def main():
    print("Task POLIGON")
    api_key = config("API_KEY")
    api_url = config("POLIGON_API_URL")

    content = requests.get("https://poligon.aidevs.pl/dane.txt", timeout=10).text
    text_lines = content.splitlines()
    print(f"lines: {text_lines}")

    data = {"task": "POLIGON", "answer": text_lines, "apikey": api_key}
    response = requests.post(api_url, json=data, timeout=10)
    if response.status_code == 200:
        print(response.json()["message"])
    else:
        print("Error during verification")


if __name__ == "__main__":
    main()
