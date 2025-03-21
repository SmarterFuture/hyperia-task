from collections.abc import AsyncIterator, Iterator
from urllib import parse

import requests

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .prospekt_extractor import ProspektExtractor, AsyncProspektExtractor


class HypermarketExtractor:

    def __init__(self, url) -> None:
        request = requests.get(url.strip(), timeout=10)
        self._parsed = BeautifulSoup(request.content, "html.parser")

        sidebar = self._parsed.find(id="sidebar")
        hypermarkets_env = (
            sidebar.find_next(class_="list-unstyled categories") if sidebar else None
        )

        hypermarkets = hypermarkets_env.find_all("a") if hypermarkets_env else None

        if not hypermarkets:
            raise NameError("sidebar and/or hypermarket links were not found")

        self._hypermarkets_links = []

        for link in map(lambda tag: str(tag.get("href")), hypermarkets):
            shop_name = link.replace("/", "")
            self._hypermarkets_links.append((parse.urljoin(url, link), shop_name))

    @property
    async def async_hypermarkets(self) -> AsyncIterator[AsyncProspektExtractor]:
        async with ClientSession() as session:
            for url, shop_name in self._hypermarkets_links:
                web_prospekts = await AsyncProspektExtractor(
                    url, shop_name, session
                ).fetch()
                yield web_prospekts

    @property
    def hypermarkets(self) -> Iterator[ProspektExtractor]:
        return map(lambda data: ProspektExtractor(*data), self._hypermarkets_links)
