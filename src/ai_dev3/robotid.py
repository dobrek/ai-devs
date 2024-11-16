import requests
from decouple import config
from termcolor import colored

from .utils.api_client import send_answer
from .utils.open_ai import generate_image


def _get_robot_info() -> dict:
    url = f"{config('CENTRALA_URL')}/data/{config('API_KEY')}/robotid.json"
    info = requests.get(url, timeout=10).json()
    print("Robot info:", colored(info, "blue"))
    return info


def _generate_robot_image(description: str) -> str:
    prompt = image_prompt_tpl.format(description=description)
    return generate_image(prompt=prompt, width=1024, height=1024)


image_prompt_tpl = """
<prompt_objective>
The purpose is to generate a realistic image of a fictional security robot based on a witness's description provided in the prompt.
</prompt_objective>

<prompt_rules>
- Use the description or testimonial provided to render the image of the security robot.
- Image must be in PNG format.
- The style of the image should be realistic, ensuring that it doesn't stray into non-realistic interpretations.
- Avoid including elements that are not mentioned in the provided testimony.
</prompt_rules>

<description>
{description}
</description>
"""


def main() -> None:
    try:
        robot_info = _get_robot_info()
        image_url = _generate_robot_image(robot_info["description"])
        send_answer(task="robotid", answer=image_url)
    except Exception as e:
        print("Error :(", colored(e, "red"))


if __name__ == "__main__":
    main()
