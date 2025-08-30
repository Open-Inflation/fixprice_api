"""Общий (не класифицируемый) функционал"""

import hrequests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassGeneral:
    """Общие методы API Перекрёстка.

    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """

    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL

    def download_image(self, url: str) -> hrequests.Response:
        """Скачать изображениe с сайта."""
        return self._parent._request("GET", url=url)
