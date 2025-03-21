from collections.abc import Iterator
import datetime as dt
from typing import Self

import re
import requests

from bs4 import BeautifulSoup
from bs4.element import PageElement
from aiohttp import ClientSession

from .prospekt import Prospekt


class ProspektExtractor:
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, url: str, shop_name: str) -> None:
        response = requests.get(url.strip(), timeout=10)
        self._parsed = BeautifulSoup(response.content, "html.parser")
        self._parsed_at = dt.datetime.now()

        self._prospekts = self._parsed.find_all(class_=re.compile(r"brochure\-thumb.*"))

        self._shop_name = shop_name

    def __prospekt_parser(self, tag: PageElement) -> Prospekt:
        title_env = tag.find_next("strong")
        title = title_env.get_text() if title_env else "not found"

        picture_env = tag.find("picture") if tag else None

        thumbnail = "not found"

        if picture_env:

            thumbnail_env = picture_env.img
            thumbnail = thumbnail_env.get("src") or thumbnail_env.get("data-src")

        validity_env = tag.find_next(class_="hidden-sm")
        validity = validity_env.get_text().split(" - ") if validity_env else []

        valid_from = dt.datetime(1970, 1, 1)
        valid_to = dt.datetime(1970, 1, 1)
        if len(validity) == 2:
            valid_from = dt.datetime.strptime(validity[0], self.DATE_FORMAT)
            valid_to = dt.datetime.strptime(validity[1], self.DATE_FORMAT)

        return Prospekt(
            title, thumbnail, self._shop_name, valid_from, valid_to, self._parsed_at
        )

    @property
    def prospekts(self) -> Iterator[Prospekt]:
        return map(self.__prospekt_parser, self._prospekts)


class AsyncProspektExtractor(ProspektExtractor):

    def __init__(self, url: str, shop_name: str, session: ClientSession) -> None:
        self._shop_name = shop_name
        self._url = url
        self._session = session

        self._parsed = BeautifulSoup()
        self._parsed_at = dt.datetime(1970, 1, 1)

        self._prospekts = []

    async def fetch(self) -> Self:
        async with self._session.get(self._url) as response:
            self._parsed = BeautifulSoup(await response.read(), "html.parser")
            self._parsed_at = dt.datetime.now()

            self._prospekts = self._parsed.find_all(
                class_=re.compile(r"brochure\-thumb.*")
            )

            return self
