from collections.abc import AsyncIterator, Iterator
from urllib import parse

import requests

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from .prospect_extractor import ProspectExtractor


class HypermarketExtractor:
    """HypermarketExtractor.
    Extracts and handles all of hypermarkets on specified url
    """

    def __init__(self, url: str) -> None:
        """__init__.

        Args:
            url (str): hypermarket title page url (in this case: https://www.prospectmaschine.de/hypermarkte/)

        Raises:
            NameError: when sidebar and/or hypermarkets urls were not found
        """
        self._url = url

        request = requests.get(url.strip(), timeout=10)
        self._parsed = BeautifulSoup(request.content, "html.parser")

        sidebar = self._parsed.find(id="sidebar")
        hypermarkets_env = (
            sidebar.find_next(class_="list-unstyled categories") if sidebar else None
        )

        hypermarkets = hypermarkets_env.find_all("a") if hypermarkets_env else None

        if not hypermarkets:
            raise NameError("sidebar and/or hypermarkets urls were not found")

        self._hypermarkets_urls: dict[str, ProspectExtractor] = {}

        for pathname in map(lambda tag: str(tag.get("href")), hypermarkets):
            shop_name = pathname.replace("/", "")
            full_url = parse.urljoin(url, pathname)
            self._hypermarkets_urls[shop_name] = ProspectExtractor(full_url, shop_name)

    def __repr__(self) -> str:
        fetched = sum(
            map(
                lambda extractor: int(extractor.is_fetched),
                self._hypermarkets_urls.values(),
            )
        )
        total = len(self._hypermarkets_urls)
        return f"HypermarketExtractor<{self._url}, fetched={fetched}/{total}>"

    def get_hypermarket(self, shop_name: str) -> ProspectExtractor:
        """get_hypermarket.
        Fetches and returns specified hypermarket by its handle

        Args:
            shop_name (str): shop/vendor's name

        Returns:
            ProspectExtractor

        Raises:
            KeyError: when shop/vendor's name is not in the list of fetched hypermarkets
        """
        if shop_name not in self._hypermarkets_urls:
            raise KeyError("shop name was either not found or is not part of list")

        return self._hypermarkets_urls[shop_name].fetch()

    @property
    async def async_hypermarkets(self) -> AsyncIterator[ProspectExtractor]:
        """async_hypermarkets.
        Same as .hypermarkets but asynchronous
        """
        async with ClientSession() as session:
            for extractor in self._hypermarkets_urls.values():
                yield await extractor.async_fetch(session)

    @property
    def hypermarkets(self) -> Iterator[ProspectExtractor]:
        """hypermarkets.
        Fetches ans returns all hypermarkets found on specified url
        """
        for extractor in self._hypermarkets_urls.values():
            yield extractor.fetch()
