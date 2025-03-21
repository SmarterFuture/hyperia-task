import datetime as dt
import json
import re
import requests

from bs4 import BeautifulSoup
from bs4.element import PageElement
from collections.abc import Iterator
from urllib import parse


class Prospekt:
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = f"{DATE_FORMAT} %H:%M:%S"

    def __init__(
        self,
        title: str,
        thumbnail: str,
        shop_name: str,
        valid_from: dt.datetime,
        valid_to: dt.datetime,
        parsed_at: dt.datetime,
    ) -> None:
        self._title = title
        self._thumbnail = thumbnail
        self._shop_name = shop_name
        self._valid_from = valid_from
        self._valid_to = valid_to
        self._parsed_time = parsed_at

    def __repr__(self) -> str:
        return f"Prospekt<{self._shop_name}, {self._parsed_time.strftime(self.DATETIME_FORMAT)}>"

    def to_json(self) -> dict[str, str | dt.datetime]:
        return {
            "title": self._title,
            "thumbnail": self._thumbnail,
            "shop_name": self._shop_name,
            "valid_from": self._valid_from.strftime(self.DATE_FORMAT),
            "valid_to": self._valid_to.strftime(self.DATE_FORMAT),
            "parsed_time": self._parsed_time.strftime(self.DATETIME_FORMAT),
        }

class WebProspektsDataHandler:
    DATE_FORMAT = "%d.%m.%Y"

    def __init__(self, url: str) -> None:
        request = requests.get(url.strip(), timeout=10)
        self._parsed = BeautifulSoup(request.content, "html.parser")
        self._parsed_at = dt.datetime.now()
        
        self._prospekts = self._parsed.find_all(class_=re.compile(r"brochure\-thumb.*"))
    
    @property
    def bulletins(self) -> Iterator[Prospekt]:
        return map(self.__bulletin_parser, self._prospekts)

    def __bulletin_parser(self, tag: PageElement) -> Prospekt:
        title_env = tag.find_next("strong")
        title = title_env.get_text() if title_env else "not found"

        picture_envs: list = tag.find_all("picture") if tag else []
        print(picture_envs)

        thumbnail = "not found"
        shop_name = "not found"

        if len(picture_envs) == 2:

            thumbnail_env = picture_envs[0].img
            thumbnail = thumbnail_env.get("src") or thumbnail_env.get("data-src")

            logo_text = picture_envs[1].img.get("alt") or "" 
            shop_name_raw = logo_text.split(maxsplit=1) or [""]
            shop_name = shop_name_raw.pop()
        
        validity_env = tag.find_next(class_="hidden-sm")
        validity = validity_env.get_text().split(" - ") if validity_env else []
        
        valid_from = dt.datetime(1970, 1, 1)
        valid_to =  dt.datetime(1970, 1, 1)
        if len(validity) == 2:
            valid_from = dt.datetime.strptime(validity[0], self.DATE_FORMAT)
            valid_to = dt.datetime.strptime(validity[1], self.DATE_FORMAT)
        
        return Prospekt(title, thumbnail, shop_name, valid_from, valid_to, self._parsed_at)


class HypermarkteDataHandler:
    def __init__(self, url) -> None:
        request = requests.get(url.strip(), timeout=10)
        self._parsed = BeautifulSoup(request.content, "html.parser")
        
        sidebar = self._parsed.find(id="sidebar")
        hypermarket_box = sidebar.find_next(class_="list-unstyled categories") if sidebar else None

        hypermarkets = hypermarket_box.find_all("a") if hypermarket_box else None
        
        if not hypermarkets:
            raise NameError("sidebar and/or hypermarket links were not found")
        
        self._hypermarkets_links = []


        for link in map(lambda tag: str(tag.get("href")), hypermarkets):
            self._hypermarkets_links.append(parse.urljoin(url, link))
        
    @property
    def hypermarkets(self) -> Iterator[WebProspektsDataHandler]:
        return map(WebProspektsDataHandler, self._hypermarkets_links)


if __name__ == "__main__":
    url = "https://www.prospektmaschine.de/hypermarkte/"

    # web = WebProspektsDataHandler(url)
    # print(list(map(lambda x: x.to_json(), web.bulletins)))

    complete = HypermarkteDataHandler(url)
    
    raw_out = []

    # for market in complete.hypermarkets:
    market = next(complete.hypermarkets)
    raw_out += list(map(lambda x: x.to_json(), market.bulletins))

    with open("tmp_out.json", "w") as f:
        json.dump(raw_out, f)

