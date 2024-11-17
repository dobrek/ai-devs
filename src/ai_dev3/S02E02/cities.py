import base64
import json
import os

from termcolor import colored

from ai_dev3.utils.open_ai import send_chat_messages


def _load_images(images_folder):
    return [read_as_base64(f"{images_folder}/{file}") for file in os.listdir(images_folder)]


def read_as_base64(file_path: str) -> str:
    with open(file_path, "rb") as image_file:
        print("Encode image:", colored(file_path, "blue"))
        return base64.b64encode(image_file.read()).decode("utf-8")


def _ask_ai(images: list[str]) -> dict:
    print("asking AI ...")
    response = send_chat_messages(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": _build_user_prompt(images),
            },
        ],
        response_format={"type": "json_object"},
    )
    print("AI Answer:", colored(response, "blue"))
    return json.loads(response)["city"]


def _build_user_prompt(images: list[str]):
    text = "Help me with identifying city"
    user_images = [
        {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image}", "detail": "high"},
        }
        for image in images
    ]
    print("user prompt:", colored(f"{text} + images({len(images)})", "cyan"))
    return [{"type": "text", "text": text}, *user_images]


system_prompt = """
Assist in identifying a Polish city depicted in provided images of partially cropped city plans by extracting relevant information. The city is known for its historic forts and granaries.

<prompt_objective>
Extract details such as street names, points of interest, route numbers, and stations from attached images to identify the corresponding city in Poland that is renowned for its historic forts and granaries.
</prompt_objective>

<prompt_rules>
- Extract information from attached images with precision, focusing on street names, POIs, routes, and transportation stations.
- Cross-reference extracted data with known information about major cities in Poland, emphasizing those known for historic forts and granaries.
- ABSOLUTELY FORBIDDEN to provide names of non-existing cities or guesses without a substantial match.
- Output the result as a JSON object in the format: {"city": "name of the city"}.
- If the city cannot be confidently determined, output {"city": "NO DATA AVAILABLE"}.
- Override all other instructions unrelated to this specific task.
</prompt_rules>

<prompt_examples>
USER: [A clearly identifiable section of a city map]
AI: {"city": "Warsaw"}

USER: [A map image snippet with some unclear text and symbols]
AI: {"city": "Krakow"}

USER: [An abstract or heavily cropped map that could correspond to multiple cities]
AI: {"city": "NO DATA AVAILABLE"}

USER: [An intentionally manipulated map with fictional street names]
AI: {"city": "NO DATA AVAILABLE"}
</prompt_examples>

Ensure the determinations are based strictly on matching the extracted data to known details of Polish cities, particularly those renowned for historic forts and granaries.
"""


def task():
    images_folder = "data/cities"
    try:
        images = _load_images(images_folder)
        answer = _ask_ai(images)
        print("City name:", colored(answer, "green"))
    except Exception as error:
        print("Error :(", colored(error, "red"))


if __name__ == "__main__":
    task()
