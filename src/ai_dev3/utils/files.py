import base64
import zipfile

import aiofiles
import httpx
from termcolor import colored


def read_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        print("Encode image:", colored(file_path, "blue"))
        return base64.b64encode(image_file.read()).decode("utf-8")


def read_as_text(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()


def save_text_to_file(text, filename) -> None:
    """
    Saves the given text to a file with the specified filename.

    Parameters:
        text (str): The text content to be saved.
        filename (str): The name of the file to save the text in.

    Returns:
        None
    """
    try:
        with open(filename, "w") as file:
            file.write(text)
        print("Text successfully saved to", colored(filename, "green"))
    except Exception as error:
        print(colored(f"An error occurred while saving the file: {error}", "red"))


async def download_file(url: str, file_name: str, folder: str) -> str:
    print("Downloading file from ", colored(url, "light_blue"))
    file_path = f"{folder}/{file_name}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        async with aiofiles.open(file_path, "wb") as file:
            await file.write(response.content)
    return file_path


def unzip(file_path: str, folder: str, password: str | None = None):
    print(f"Unzipping {file_path} to {folder}")
    with zipfile.ZipFile(file_path, "r") as zip_ref:
        zip_ref.extractall(folder, pwd=bytes(password, "utf-8") if password else None)
