"""Реклама"""

import hrequests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassAdvertising:
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL


    def home_brands_list(self) -> hrequests.Response:
        """Возвращает список брендов логотипы которых должны отображаться на главной. Является рекламой."""
        return self._parent._request("GET", f"{self.CATALOG_URL}/v1/home/brand")
