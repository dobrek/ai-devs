from pydantic import BaseModel
from termcolor import colored

from ai_dev3.utils.api_client import send_answer
from ai_dev3.utils.files import read_as_text
from ai_dev3.utils.open_ai import send_chat_messages


class Sample(BaseModel):
    id: str
    text: str


def _parse_line(line: str) -> Sample:
    parts = line.split("=")
    return Sample(id=parts[0], text=parts[1])


def _load_samples(filename: str) -> list[Sample]:
    samples = read_as_text(filename).splitlines()
    return [_parse_line(line) for line in samples]


def _is_valid(item: str) -> bool:
    print("Checking", colored(item, "yellow"))
    result = send_chat_messages(
        messages=[{"role": "system", "content": "S04EO2_Custom_Classification"}, {"role": "user", "content": item}],
        model="ft:gpt-4o-mini-2024-07-18:dunning-kruger-associates:aidev3-s04e02-01:AYJYibPT",
    )
    print("Result", colored(result, "blue"))
    return result == "OK"


def main():
    samples_to_verify = _load_samples("data/verify.txt")
    result = [sample.id for sample in samples_to_verify if _is_valid(sample.text)]
    send_answer(task="research", answer=result)


if __name__ == "__main__":
    main()
