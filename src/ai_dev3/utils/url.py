def full_url(url: str, base_url: str) -> str:
    return url if url.startswith("http") else f"{base_url}/{url}"
