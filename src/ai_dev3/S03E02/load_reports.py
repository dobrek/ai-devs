import os
import tempfile
from datetime import date
from uuid import uuid4

from ai_dev3.utils.files import download_file, read_as_text, unzip

from .types import ReportFile, TextFile


def _as_report_file(file: TextFile) -> ReportFile:
    report_date = date.fromisoformat(file.name.split(".")[0].replace("_", "-"))
    return ReportFile(id=uuid4(), weapon=file.text.split("\n", 1)[0], text=file.text, date=report_date, name=file.name)


def _load_text_files(folder: str) -> list[ReportFile]:
    files_names = [file_name for file_name in os.listdir(folder) if file_name.endswith(".txt")]
    files = [TextFile(name=file_name, text=read_as_text(f"{folder}/{file_name}")) for file_name in files_names]
    return [_as_report_file(file) for file in files]


async def load_reports(url: str, password: str) -> list[ReportFile]:
    """
    Downloads a zip file from the given URL, extracts its contents, and loads text files.
    Args:
        url (str): The URL to download the zip file from.
    Returns:
        list[TextFile]: A list of TextFile objects containing the text from the extracted files.
    Raises:
        Any exceptions raised by the download_file, unzip, or _load_text_files functions.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_file_path = await download_file(url, "pliki_z_fabryki.zip", tmp_dir)
        unzip(zip_file_path, tmp_dir)
        with tempfile.TemporaryDirectory() as temp_test_dir:
            unzip(f"{tmp_dir}/weapons_tests.zip", temp_test_dir, password)
            files = _load_text_files(f"{temp_test_dir}/do-not-share")
            return [_as_report_file(file) for file in files]
