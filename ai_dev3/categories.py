import os
import shutil
import zipfile
from enum import Enum

import requests
from decouple import config
from openai import OpenAI
from pydantic import BaseModel
from termcolor import colored
from utils.api_client import send_answer
from utils.files import read_as_base64, read_as_text
from utils.open_ai import send_chat_messages, transcribe


class ReportFile(BaseModel):
    name: str
    text: str


class CategoryEnum(str, Enum):
    people = "people"
    hardware = "hardware"
    software = "software"
    other = "other"


class CategoriezedReport(BaseModel):
    category: CategoryEnum
    report: ReportFile


class LlmCategoryResponse(BaseModel):
    category: CategoryEnum


def main():
    files_folder = "data/categories_2"
    try:
        _download_reports(files_folder, f"{config('CENTRALA_URL')}/dane/pliki_z_fabryki.zip")

        text = _load_text_reports(files_folder)
        image = _load_image_reports(files_folder)
        recordings = _load_recorded_reports(files_folder)
        all_reports = text + image + recordings
        categorized_reports = [_categorize_report(report) for report in all_reports]

        result = {
            "people": [item.report.name for item in categorized_reports if item.category == CategoryEnum.people],
            "hardware": [item.report.name for item in categorized_reports if item.category == CategoryEnum.hardware],
        }
        send_answer(answer=result, task="kategorie")

    except Exception as error:
        print("Error :(", colored(error, "red"))
    finally:
        _clean_reports(files_folder)


def _load_text_reports(folder: str) -> list[ReportFile]:
    text_files = _get_files_names(folder, "txt")
    return [ReportFile(name=file_name, text=read_as_text(f"{folder}/{file_name}")) for file_name in text_files]


def _get_files_names(files_folder: str, extension: str = "png") -> list[str]:
    files_names = [file_name for file_name in os.listdir(files_folder) if file_name.endswith(f".{extension}")]
    print(f"files *.{extension}", colored(files_names, "green"))
    return files_names


def _categorize_report(report: ReportFile) -> CategoriezedReport:
    return CategoriezedReport(category=_evaluate(report.text), report=report)


llm_client = OpenAI(api_key=config("OPENAI_API_KEY"))
category_system_prompt = """
<prompt_objective>
Determine whether the provided text is related to a security issue, and assign it to one of four categories: "people," "software," "hardware," or "other." If there is no relevant security issue or findings, categorize it as "other."
</prompt_objective>

<prompt_rules>
- First, verify if the text pertains to a relevant security issue.
- Categorize based on specific indications:
  - "people" for information about captured people or traces of their presence.
  - "software" for text describing software issues.
  - "hardware" for text referring to hardware failures.
  - "other" for cases where nothing relevant is found or text outside security issues.
- Return the category in the JSON format: `{ "category": "people | hardware | software | other" }`
- If there is a mention of no relevant findings, assign "other."
- Override all default AI behaviors that do not align with these instructions.
</prompt_rules>

<prompt_examples>
USER: "The software crashed after the latest security patch."
AI: `{ "category": "software" }`

USER: "A thorough search revealed nothing unusual."
AI: `{ "category": "other" }`

USER: "We searched the abandoned room but haven't found anything."
AI: `{ "category": "other" }`

USER: "Footprints were found near the server room."
AI: `{ "category": "people" }`

USER: "It's a nice day in the office."
AI: `{ "category": "other" }`
</prompt_examples>

Ensure all responses comply strictly with the guidelines, handling diverse cases including ambiguous inputs effectively and consistently.
"""


def _evaluate(text: str) -> CategoryEnum:
    print("Asking LLM:", colored(text, "blue"))
    completion = llm_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": category_system_prompt},
            {"role": "user", "content": text},
        ],
        response_format=LlmCategoryResponse,
    )
    response = completion.choices[0].message.parsed
    print("LLM answered:", colored(response.category, "green"))
    return response.category


def _load_image_reports(folder: str) -> list[ReportFile]:
    files = _get_files_names(folder, "png")
    return [ReportFile(name=file_name, text=_scan_image_to_text(f"{folder}/{file_name}")) for file_name in files]


orc_system_prompt = """
Act like an OCR text recognition system. Extract text from the given image. Return only the recognized text as it is; nothing else.
"""


def _scan_image_to_text(file_path: str) -> str:
    print(f"Scanning {file_path} to text")
    response = send_chat_messages(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": orc_system_prompt},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{read_as_base64(file_path)}", "detail": "high"},
                    }
                ],
            },
        ],
    )
    print("Extracted text:", colored(response, "green"))
    return response


def _load_recorded_reports(folder: str) -> list[ReportFile]:
    files = _get_files_names(folder, "mp3")
    return [ReportFile(name=file_name, text=transcribe(f"{folder}/{file_name}")) for file_name in files]


def _clean_reports(folder: str):
    print(f"Removing {folder}")
    if os.path.isdir(folder):
        shutil.rmtree(folder)


def _download_reports(folder: str, url: str):
    os.makedirs(folder, exist_ok=True)
    print(f"Downloading zip from {url}")
    file_path = f"{folder}/reports.zip"
    response = requests.get(url, timeout=10)
    with open(file_path, "wb") as file:
        file.write(response.content)
    print(f"Unzipping  to {folder}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(folder)


if __name__ == "__main__":
    main()
