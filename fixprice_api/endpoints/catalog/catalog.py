from __future__ import annotations

from typing import TYPE_CHECKING, Literal
from urllib.parse import urlencode

from human_requests import autotest
from human_requests.abstraction import HttpMethod

from ... import abstraction
from .products import ClassProducts

if TYPE_CHECKING:
    from ...manager import FixPriceAPI


class ClassCatalog:
    """Группа функций для работы с каталогом товаров."""

    def __init__(self, parent: FixPriceAPI):
        self._parent = parent
        self.Products: ClassProducts = ClassProducts(parent)

    @autotest
    async def products_list(self, category_alias: str, subcategory_alias: str | None = None, page: int = 1, limit: int = 24, sort: Literal["sold", "abc", "min", "max"] = "sold") -> abstraction.Output:
        """Fetches products inside a category or subcategory; the JSON body mirrors the request built in products_list()."""
        if category_alias is None:
            raise ValueError("`category_alias` is required")
        if not isinstance(category_alias, str):
            raise TypeError("`category_alias` must be str")
        if subcategory_alias is not None and not isinstance(subcategory_alias, str):
            raise TypeError("`subcategory_alias` must be str")
        if page is not None and (not isinstance(page, int) or isinstance(page, bool)):
            raise TypeError("`page` must be int")
        if page is not None and (float(page) < 1 or float(page) > 2147483647):
            raise ValueError("`page` must be between 1 and 2147483647")
        if limit is not None and (not isinstance(limit, int) or isinstance(limit, bool)):
            raise TypeError("`limit` must be int")
        if limit is not None and (float(limit) < 1 or float(limit) > 27):
            raise ValueError("`limit` must be between 1 and 27")
        if sort is not None and not isinstance(sort, str):
            raise TypeError("`sort` must be str")
        if sort is not None and sort not in ["sold", "abc", "min", "max"]:
            raise ValueError("`sort` must be one of ['sold', 'abc', 'min', 'max']")

        if category_alias is not None:
            request_url = str(self._parent._CATALOG_URL) + "/v1/product/in/" + str(category_alias)
        else:
            raise TypeError("products_list() call is ambiguous; URL cannot be collected")
        query_params: list[tuple[str, object]] = []
        if page is not None:
            query_params.append(("page", page))
        if limit is not None:
            query_params.append(("limit", limit))
        if sort is not None:
            query_params.append(("sort", sort))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = {"category": category_alias, "brand": [], "price": [], "isDividedPrice": False, "isNew": False, "isHit": False, "isSpecialPrice": False}
        return await self._parent._request(
            HttpMethod.POST,
            url=request_url,
            json_body=json_body,
        )

    @autotest
    async def tree(self) -> abstraction.Output:

        request_url = str(self._parent._CATALOG_URL) + "/v1/category"

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )
