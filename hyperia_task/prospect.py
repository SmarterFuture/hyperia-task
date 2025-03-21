import datetime as dt


class Prospect:
    """Prospect.
    Formater to desired format
    """

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
        """__init__.

        Args:
            title (str): prospect title
            thumbnail (str): thumbnail url
            shop_name (str): shop/vendor's name
            valid_from (dt.datetime): prospect is valid from [date]
            valid_to (dt.datetime): prospect is valid until [date]
            parsed_at (dt.datetime): prospect was fetched at [date]
        """
        self._title = title
        self._thumbnail = thumbnail
        self._shop_name = shop_name
        self._valid_from = valid_from
        self._valid_to = valid_to
        self._parsed_time = parsed_at

    def __repr__(self) -> str:
        return f"Prospect<{self._shop_name}, {self._parsed_time.strftime(self.DATETIME_FORMAT)}>"

    def to_json(self) -> dict[str, str | dt.datetime]:
        """to_json.
        Converts Prospect object to JSON format

        Args:

        Returns:
            dict[str, str | dt.datetime]: JSON-like fromat
        """
        return {
            "title": self._title,
            "thumbnail": self._thumbnail,
            "shop_name": self._shop_name,
            "valid_from": self._valid_from.strftime(self.DATE_FORMAT),
            "valid_to": self._valid_to.strftime(self.DATE_FORMAT),
            "parsed_time": self._parsed_time.strftime(self.DATETIME_FORMAT),
        }
