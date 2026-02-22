"""Работа с каталогом"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, TYPE_CHECKING
from .. import abstraction
from human_requests import autotest
from human_requests.abstraction import FetchResponse, HttpMethod
from human_requests import ApiChild, ApiParent, api_child_field

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


@dataclass(init=False)
class ClassCatalog(ApiChild["FixPriceAPI"], ApiParent):
    """Методы для работы с каталогом товаров.

    Включает поиск товаров, получение информации о категориях,
    работу с фидами товаров и отзывами.
    """

    Product: ProductService = api_child_field(
        lambda parent: ProductService(parent.parent)
    )
    """Сервис для работы с товарами в каталоге."""

    def __init__(self, parent: "FixPriceAPI"):
        super().__init__(parent)
        ApiParent.__post_init__(self)

    @autotest
    async def tree(self) -> FetchResponse:
        """Возвращает список категорий."""
        return await self._parent._request(
            HttpMethod.GET, f"{self._parent.CATALOG_URL}/v1/category"
        )

    @autotest
    async def products_list(
        self,
        category_alias: str,
        subcategory_alias: Optional[str] = None,
        page: int = 1,
        limit: int = 24,
        sort: abstraction.CatalogSort | str = abstraction.CatalogSort.POPULARITY,
    ) -> FetchResponse:
        """Возвращает количество и список товаров в категории/подкатегории."""
        if page < 1:
            raise ValueError("`page` must be greater than 0")
        elif limit > 27 or limit < 1:
            raise ValueError("`limit` must be in range 1-27")

        url = f"{self._parent.CATALOG_URL}/v1/product/in/{category_alias}"
        real_route = f"/catalog/{category_alias}"
        if subcategory_alias:
            url += f"/{subcategory_alias}"
            real_route += f"/{subcategory_alias}"
        url += f"?page={page}&limit={limit}&sort={sort}"

        json_body = {
            "category": category_alias,
            "brand": [],
            "price": [],
            "isDividedPrice": False,
            "isNew": False,
            "isHit": False,
            "isSpecialPrice": False,
        }
        if subcategory_alias:
            json_body["category"] += f"/{subcategory_alias}"

        return await self._parent._request(
            HttpMethod.POST, url=url, real_route=real_route, json_body=json_body
        )


class ProductService(ApiChild["FixPriceAPI"]):
    """Сервис для работы с товарами в каталоге."""

    @autotest
    async def balance(
        self, product_id: int, in_stock: bool = True, search: Optional[str] = None
    ) -> FetchResponse:
        """
        Проверка наличия товара в точках города.
        Возвращает информацию о магазине и int количество товара.
        `city_id` в базовом классе должен быть обязательно указан, иначе ошибка!

        `in_stock` - фильтрует только те магазины, в которых есть товар, иначе все.
        `search` - фильтр по поисковому адресу.
        """
        if self._parent.city_id == None:
            raise ValueError("City ID is not set")

        url = f"{self._parent.CATALOG_URL}/v1/store/balance/{product_id}?canPickup=all"
        if search:
            url += f"&addressPart={search}"
        if in_stock:
            url += "&inStock=true"

        return await self._parent._request(HttpMethod.GET, url)
