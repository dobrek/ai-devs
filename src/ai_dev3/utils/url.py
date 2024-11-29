import re


def full_url(url: str, base_url: str) -> str:
    return url if url.startswith("http") else f"{base_url}/{url}"


def is_valid_url(url: str) -> bool:
    """
    Validate if the given string is a valid URL.

    Args:
        url (str): The URL to validate.

    Returns:
        bool: True if the URL is valid, False otherwise.
    """
    url_regex = re.compile(
        r"^(https?:\/\/)?"  # Optional scheme
        r"((([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})|"  # Domain name
        r"localhost|"  # or localhost
        r"(\d{1,3}\.){3}\d{1,3})"  # or IPv4
        r"(:\d+)?"  # Optional port
        r"(\/[a-zA-Z0-9-._~:\/?#\[\]@!$&\'()*+,;=%]*)?$"  # Path
    )
    return re.match(url_regex, url) is not None
