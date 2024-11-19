import os
import tempfile

from pydantic import BaseModel

from ai_dev3.utils.files import download_file, read_as_text, unzip

from .types import TextFile


class DataSet(BaseModel):
    reports: list[TextFile]
    facts: list[TextFile]


def _load_text_files(folder: str) -> list[TextFile]:
    files_names = [file_name for file_name in os.listdir(folder) if file_name.endswith(".txt")]
    return [TextFile(name=file_name, text=read_as_text(f"{folder}/{file_name}")) for file_name in files_names]


async def load_data(url: str) -> DataSet:
    """
    Downloads a zip file from the given URL, extracts its contents, and loads text files into a DataSet.
    Args:
        url (str): The URL to download the zip file from.
    Returns:
        DataSet: An object containing the loaded reports and facts.
    Raises:
        Any exceptions raised by the download_file, unzip, or _load_text_files functions.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        zip_file_path = await download_file(url, "pliki_z_fabryki.zip", tmp_dir)
        unzip(zip_file_path, tmp_dir)
        reports = _load_text_files(tmp_dir)
        facts = _load_text_files(f"{tmp_dir}/facts")
        relevant_facts = [fact for fact in facts if len(fact.text) > 30]
        return DataSet(reports=reports, facts=relevant_facts)
