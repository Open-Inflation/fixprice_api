"""Реклама"""

from human_requests import autotest
from human_requests.abstraction import FetchResponse, HttpMethod
from typing import TYPE_CHECKING

from human_requests import ApiChild

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassAdvertising(ApiChild["FixPriceAPI"]):
    """Методы для работы с рекламными материалами Перекрёстка.

    Включает получение баннеров, слайдеров, буклетов и другого рекламного контента.
    """

    @autotest
    async def home_brands_list(self) -> FetchResponse:
        """Возвращает список брендов логотипы которых должны отображаться на главной. Является рекламой."""
        return await self._parent._request(
            HttpMethod.GET, f"{self._parent.CATALOG_URL}/v1/home/brand"
        )
