import httpx
from termcolor import colored

from ai_dev3.utils.api_client import send_answer


def _get_public_url():
    data = httpx.get("http://localhost:4040/api/tunnels").json()
    return data["tunnels"][0]["public_url"]


def main():
    try:
        local_api_url = _get_public_url()
        send_answer(task="webhook", answer=local_api_url)
    except Exception as error:
        print(colored("Failed to get public URL", "red"), error)


if __name__ == "__main__":
    main()
