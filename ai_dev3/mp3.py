import os
import re
import zipfile

import requests
from decouple import config
from utils.api_client import send_answer
from utils.open_ai import send_chat_messages, transcribe


def task():
    recordings_folder = "mp3_files"
    try:
        _create_recordings_folder(recordings_folder)
        _download_recordings(recordings_folder, f"{config('CENTRALA_URL')}/dane/przesluchania.zip")
        testimonies = _build_testimonies(recordings_folder)
        answer = _ask_llm(testimonies)
        street_name = _extract_street_name(answer)
        if street_name:
            send_answer(task="MP3", answer=street_name)
        else:
            print("Street name not found")
    except Exception as e:
        print("Error :(", e)
    finally:
        _clean_recordings_folder(recordings_folder)


def _create_recordings_folder(folder_name: str):
    print(f"Creating {folder_name}")
    os.makedirs(folder_name, exist_ok=True)


def _clean_recordings_folder(folder_name: str):
    for file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, file)
        os.remove(file_path)
    print(f"Removing {folder_name}")
    os.rmdir(folder_name)


def _download_recordings(folder_name: str, url: str):
    print(f"Downloading zip from {url}")
    file_path = f"{folder_name}/mp3.zip"
    response = requests.get(url, timeout=10)
    with open(file_path, "wb") as file:
        file.write(response.content)
    print(f"Unzipping  to {folder_name}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(folder_name)


def _build_testimonies(folder_name: str) -> list[dict]:
    return [
        {"text": _transcribe_recording(recording["file"]), "name": recording["name"]}
        for recording in _getAllRecordings(folder_name)
    ]


def _getAllRecordings(folder_name: str) -> list[dict]:
    return [
        {"file": f"{folder_name}/{item}", "name": item.split(".")[0]}
        for item in os.listdir(folder_name)
        if item.endswith(".m4a")
    ]


def _transcribe_recording(audio_file_path: str) -> dict:
    print(f"Transcribing {audio_file_path}")
    return transcribe(audio_file_path, promopt="Andrzej Maj")


def _ask_llm(testimonies: list[dict]) -> str:
    print("Asking LLM")
    system_prompt = system_prompt_tpl.format(
        context="\n".join([f"- {item['name']}: {item['text']}" for item in testimonies])
    )
    print("System prompt:\n", system_prompt)
    answer = send_chat_messages(
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        model="gpt-4o",
    )
    print("Answer from LLM:", answer)
    return answer


system_prompt_tpl = """
Poniżej lista zeznań w sprawie profesora matematyki Andrzeja Maja

<zeznania>
{context}
</zeznania>
"""

user_prompt = """
- Przeanalizuj podane zeznania pod kątem informacji o miejscu pracy profesora matematyki Andrzeja Maja.
- Pamiętaj, że zeznania  mogą być sprzeczne, niektórzy z nich mogą się mylić, a inni odpowiadać w dość dziwaczny sposób.
- Weź pod uwagę akademicki charakter jego pracy, oraz fakt, że struktura uczelni opiera się na wydziałach i instytutach.
- Wypisz wnioski i fakty jakie udało Ci się ustalić.
- Zastanów się i na podstawie zebranych informacji określ ulice na jakiej mieści się miejsce pracy Andrzeja Maja.
- Wypisz nazwę ulicy w tagu XML <NAZWA_ULICY>Nazwa ulicy</NAZWA_ULICY>
"""


def _extract_street_name(text: str) -> str | None:
    match = re.search(r"<NAZWA_ULICY>(.*?)</NAZWA_ULICY>", text)
    if match:
        return match.group(1)
    else:
        return None


if __name__ == "__main__":
    task()
