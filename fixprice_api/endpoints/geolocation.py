from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.parse import urlencode

from human_requests import autotest
from human_requests.abstraction import HttpMethod

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import FixPriceAPI


class ClassGeolocation:
    """Группа функций для работы с геолокацией, получения информации о странах, регионах и городах."""

    def __init__(self, parent: FixPriceAPI):
        self._parent = parent

    @autotest
    async def cities_list(self, country_id: int) -> abstraction.Output:
        if country_id is None:
            raise ValueError("`country_id` is required")
        if not isinstance(country_id, int) or isinstance(country_id, bool):
            raise TypeError("`country_id` must be int")
        if float(country_id) < 1 or float(country_id) > 2147483647:
            raise ValueError("`country_id` must be between 1 and 2147483647")

        request_url = str(self._parent._CATALOG_URL) + "/v1/location/city"
        query_params: list[tuple[str, object]] = []
        if country_id is not None:
            query_params.append(("countryId", country_id))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )

    @autotest
    async def city_info(self, city_id: int) -> abstraction.Output:
        """Returns a single city by id."""
        if city_id is None:
            raise ValueError("`city_id` is required")
        if not isinstance(city_id, int) or isinstance(city_id, bool):
            raise TypeError("`city_id` must be int")
        if float(city_id) < 1:
            raise ValueError("`city_id` must be greater than or equal to 1")

        if city_id is not None:
            request_url = str(self._parent._CATALOG_URL) + "/v1/location/city/" + str(city_id)
        else:
            raise TypeError("city_info() call is ambiguous; URL cannot be collected")

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )

    @autotest
    async def countries_list(self, alias: str | None = None) -> abstraction.Output:
        if alias is not None and not isinstance(alias, str):
            raise TypeError("`alias` must be str")
        if alias is not None and not (abstraction.RegexCountryAlias.match(alias)):
            raise ValueError(abstraction.RegexCountryAlias.ERROR)

        request_url = str(self._parent._CATALOG_URL) + "/v1/location/country"
        query_params: list[tuple[str, object]] = []
        if alias is not None:
            query_params.append(("alias", alias))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )

    @autotest
    async def regions_list(self, country_id: int | None = None) -> abstraction.Output:
        if country_id is not None and (not isinstance(country_id, int) or isinstance(country_id, bool)):
            raise TypeError("`country_id` must be int")
        if country_id is not None and (float(country_id) < 1 or float(country_id) > 2147483647):
            raise ValueError("`country_id` must be between 1 and 2147483647")

        request_url = str(self._parent._CATALOG_URL) + "/v1/location/region"
        query_params: list[tuple[str, object]] = []
        if country_id is not None:
            query_params.append(("countryId", country_id))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )

    @autotest
    async def search(self, country_id: int | None = None, region_id: int | None = None, city_id: int | None = None, search: str | None = None) -> abstraction.Output:
        if country_id is not None and (not isinstance(country_id, int) or isinstance(country_id, bool)):
            raise TypeError("`country_id` must be int")
        if country_id is not None and (float(country_id) < 1 or float(country_id) > 2147483647):
            raise ValueError("`country_id` must be between 1 and 2147483647")
        if region_id is not None and (not isinstance(region_id, int) or isinstance(region_id, bool)):
            raise TypeError("`region_id` must be int")
        if region_id is not None and (float(region_id) < 1 or float(region_id) > 2147483647):
            raise ValueError("`region_id` must be between 1 and 2147483647")
        if city_id is not None and (not isinstance(city_id, int) or isinstance(city_id, bool)):
            raise TypeError("`city_id` must be int")
        if city_id is not None and (float(city_id) < 1 or float(city_id) > 2147483647):
            raise ValueError("`city_id` must be between 1 and 2147483647")
        if search is not None and not isinstance(search, str):
            raise TypeError("`search` must be str")

        request_url = str(self._parent._CATALOG_URL) + "/v1/store"
        query_params: list[tuple[str, object]] = []
        query_params.append(("searchType", "metro"))
        query_params.append(("canPickup", "all"))
        query_params.append(("showTemporarilyClosed", "all"))
        if country_id is not None:
            query_params.append(("countryId", country_id))
        if region_id is not None:
            query_params.append(("regionId", region_id))
        if city_id is not None:
            query_params.append(("cityId", city_id))
        if search is not None:
            query_params.append(("addressPart", search))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )
