"""Геолокация"""

from human_requests.abstraction import FetchResponse, HttpMethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    def __init__(self, parent: "FixPriceAPI"):
        self._parent: "FixPriceAPI" = parent

        self.Shop: ShopService = ShopService(self._parent)
        """Работа с магазинами."""

    async def countries_list(self, alias: str = None) -> FetchResponse:
        """Возвращает список всех стран, их id и название. `alias` - работает как сортировка."""
        url = f"{self._parent.CATALOG_URL}/v1/location/country"
        if alias:
            if len(alias) != 2: raise ValueError("`alias` must be ISO-2. Length must be 2")

            url += f"?alias={alias.upper()}"

        return await self._parent._request(HttpMethod.GET, url=url)

    async def regions_list(self, country_id: int = None) -> FetchResponse:
        """Возвращает список всех регионов, их id и название. Если фильтр не применен - выдача всех регионов независимо от страны."""
        url = f"{self._parent.CATALOG_URL}/v1/location/region"
        if not country_id: url += f"?countryId={country_id}"

        return await self._parent._request(HttpMethod.GET, url=url)
    
    async def cities_list(self, country_id: int) -> FetchResponse:
        """Возвращает список всех городов, их id и название, геопозицию, регион и тип населенного пункта. По умолчанию - по РФ."""
        url = f"{self._parent.CATALOG_URL}/v1/location/city"
        if country_id: url += f"?countryId={country_id}"

        return await self._parent._request(HttpMethod.GET, url=url)

    async def city_info(self, city_id: int) -> FetchResponse:
        """Возвращает информацию о городе."""
        return await self._parent._request(HttpMethod.GET, f"{self._parent.CATALOG_URL}/v1/location/city/{city_id}")


class ShopService:
    """Сервис для работы с информацией о магазинах."""
    def __init__(self, parent: "FixPriceAPI"):
        self._parent: "FixPriceAPI" = parent


    async def search(
        self,
        country_id: int = None,
        region_id: int = None,
        city_id: int = None,
        search: str = None
    ) -> FetchResponse:
        """Поиск магазинов."""
        url = f"{self._parent.CATALOG_URL}/v1/store?searchType=metro&canPickup=all&showTemporarilyClosed=all"

        if country_id: url += f"&countryId={country_id}"
        if region_id: url += f"&regionId={region_id}"
        if city_id: url += f"&cityId={city_id}"
        if search: url += f"&addressPart={search}"

        return await self._parent._request(HttpMethod.GET, url=url)

