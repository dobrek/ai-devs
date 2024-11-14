import base64

from termcolor import colored


def read_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        print("Encode image:", colored(file_path, "blue"))
        return base64.b64encode(image_file.read()).decode("utf-8")


def read_as_text(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()
