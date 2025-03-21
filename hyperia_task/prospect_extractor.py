from collections.abc import Iterator
import datetime as dt
from typing import Self

import re
import requests

from bs4 import BeautifulSoup
from bs4.element import PageElement
from aiohttp import ClientSession

from .prospect import Prospect


class ProspectExtractor:
    """ProspectExtractor.
    Extracts and handles prospects of specified hypermarket
    """

    DATE_FORMAT = "%d.%m.%Y"
    PROSPEKT_REGEX = re.compile(r"brochure\-thumb.*")

    def __init__(self, url: str, shop_name: str) -> None:
        """__init__.

        Args:
            url (str): hypermarket url
            shop_name (str): shop/vendor's name
        """
        self._url = url.strip()
        self._shop_name = shop_name

        self._is_fetched = False

        self._parsed = BeautifulSoup()
        self._parsed_at = dt.datetime(1970, 1, 1)

        self._prospects = []

    def __repr__(self) -> str:
        fetch_status = (
            self._parsed_at.strftime(self.DATE_FORMAT) if self._is_fetched else "never"
        )
        return f"ProspectExtractor<{self._url}, fetched_at={fetch_status}>"

    def __prospect_parser(self, tag: PageElement) -> Prospect:
        """__prospect_parser.
        Parses fetched data of specified hypermarket to desired format

        Args:
            tag (PageElement): prospect web tile element

        Returns:
            Prospect
        """
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

        return Prospect(
            title, thumbnail, self._shop_name, valid_from, valid_to, self._parsed_at
        )

    async def async_fetch(self, session: ClientSession) -> Self:
        """async_fetch.
        Same as .fetch() but asynchronous

        Args:
            session (ClientSession): asynchronous network IO session

        Returns:
            Self
        """
        if self._is_fetched:
            return self

        async with session.get(self._url) as response:
            self._parsed = BeautifulSoup(await response.read(), "html.parser")
            self._parsed_at = dt.datetime.now()

            self._prospects = self._parsed.find_all(class_=self.PROSPEKT_REGEX)

        self._is_fetched = True
        return self

    def fetch(self) -> Self:
        """fetch.
        Fetches page content

        Returns:
            Self
        """
        if self._is_fetched:
            return self

        response = requests.get(self._url, timeout=10)
        self._parsed = BeautifulSoup(response.content, "html.parser")
        self._parsed_at = dt.datetime.now()

        self._prospects = self._parsed.find_all(class_=self.PROSPEKT_REGEX)

        self._is_fetched = True
        return self

    @property
    def is_fetched(self):
        """is_fetched.
        Returns whether page was fetched already or not
        """
        return self._is_fetched

    @property
    def prospects(self) -> Iterator[Prospect]:
        """prospects.
        Returns lazy list of prospects of specified hypermarket

        Returns:
            Iterator[Prospect]
        """
        return map(self.__prospect_parser, self._prospects)
