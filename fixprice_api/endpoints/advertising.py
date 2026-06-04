from __future__ import annotations

from typing import TYPE_CHECKING

from human_requests import autotest
from human_requests.abstraction import HttpMethod

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import FixPriceAPI


class ClassAdvertising:
    """Группа функций для получения информации о рекламных акциях и брендах на главной странице."""

    def __init__(self, parent: FixPriceAPI):
        self._parent = parent

    @autotest
    async def home_brands_list(self) -> abstraction.Output:

        request_url = str(self._parent._CATALOG_URL) + "/v1/home/brand"

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )
