import re
from urllib.parse import urljoin

from markdownify import markdownify as md
from pydantic import BaseModel

from ai_dev3.utils.http import get_text

from .types import Link

LINK_PATTERN = re.compile(r'\[([^\]]+)\]\((\S+)(?:\s+"([^"]+)")?\)')


class ScrapedPage(BaseModel):
    url: str
    text: str
    links: list[Link]


class PageScrapper:
    def __init__(self, base_url):
        self.base_url = base_url

    async def _read_page_as_md(self, url: str) -> str:
        return md(await get_text(url))

    def _extract_links_from_markdown(self, markdown: str, base_url: str) -> list[Link]:
        matches = LINK_PATTERN.findall(markdown)
        return [
            Link(
                text=match[0],
                href=urljoin(base_url, match[1]),
                title=match[2] if len(match) > 2 and match[2] else None,
            )
            for match in matches
        ]

    async def scrape_page(self, url: str) -> ScrapedPage:
        text = await self._read_page_as_md(url)
        links = self._extract_links_from_markdown(text, self.base_url)
        return ScrapedPage(url=url, text=text, links=links)
