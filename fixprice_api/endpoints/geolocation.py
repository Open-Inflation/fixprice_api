"""Геолокация"""

import hrequests
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassGeolocation:
    """Методы для работы с геолокацией и выбором магазинов.

    Включает получение информации о городах, адресах, поиск магазинов
    и управление настройками доставки.
    """

    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL


    def country_list(self, alias: str = None) -> hrequests.Response:
        """Возвращает список всех стран, их id и название. `alias` - работает как сортировка."""
        url = f"{self.CATALOG_URL}/v1/location/country"
        if alias:
            if len(alias) != 2: raise ValueError("`alias` must be ISO-2. Length must be 2")

            url += f"?alias={alias.upper()}"

        return self._parent._request("GET", url=url)

    def region_list(self, country_id: int = None) -> hrequests.Response:
        """Возвращает список всех регионов, их id и название. Если фильтр не применен - выдача всех регионов независимо от страны."""
        url = f"{self.CATALOG_URL}/v1/location/region"
        if not country_id: url += f"?countryId={country_id}"

        return self._parent._request("GET", url=url)
    
    def city_list(self, country_id: int) -> hrequests.Response:
        """Возвращает список всех городов, их id и название, геопозицию, регион и тип населенного пункта. По умолчанию - по РФ."""
        url = f"{self.CATALOG_URL}/v1/location/city"
        if country_id: url += f"?countryId={country_id}"

        return self._parent._request("GET", url=url)

    def city_info(self, city_id: int) -> hrequests.Response:
        """Возвращает информацию о городе."""
        return self._parent._request("GET", f"{self.CATALOG_URL}/v1/location/city/{city_id}")

    def my_geoposition(self) -> hrequests.Response:
        """Возвращает информацию о предполагаемой геопозиции на основе IP."""
        return self._parent._request("GET", f"{self.CATALOG_URL}/v2/geo/ip")


class ShopService:
    """Сервис для работы с информацией о магазинах."""
    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL


    def search(
        self,
        country_id: int = None,
        region_id: int = None,
        city_id: int = None,
        search: str = None
    ) -> hrequests.Response:
        """Поиск магазинов."""
        url = f"{self.CATALOG_URL}/v1/store?searchType=metro&canPickup=all&showTemporarilyClosed=all"

        if country_id: url += f"&countryId={country_id}"
        if region_id: url += f"&regionId={region_id}"
        if city_id: url += f"&cityId={city_id}"
        if search: url += f"&addressPart={search}"

        return self._parent._request("GET", url=url)

