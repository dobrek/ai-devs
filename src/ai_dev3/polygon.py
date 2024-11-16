import requests
from decouple import config

from .utils.api_client import send_answer


def main() -> None:
    polygon_url = config("POLYGON_URL")
    content = requests.get(f"{polygon_url}/dane.txt", timeout=10).text
    text_lines = content.splitlines()
    print(f"lines: {text_lines}")
    send_answer(task="POLIGON", answer=text_lines, url=f"{polygon_url}/verify")


if __name__ == "__main__":
    main()
