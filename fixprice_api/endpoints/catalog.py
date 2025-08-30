"""Работа с каталогом"""

from typing import Optional, TYPE_CHECKING
import ..abstraction
import hrequests

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassCatalog:
    """Методы для работы с каталогом товаров.

    Включает поиск товаров, получение информации о категориях,
    работу с фидами товаров и отзывами.

    Attributes
    ----------
    Product : ProductService
        Сервис для работы с товарами в каталоге.
    """

    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL
        self.Product: ProductService = ProductService(
            parent=self._parent, CATALOG_URL=CATALOG_URL
        )

    def tree(self) -> hrequests.Response:
        """Возвращает список категорий."""
        return self._parent._request("GET", f"{self.CATALOG_URL}/v1/category/menu")

    def products_list(
            self,
            category_alias: str,
            subcategory_alias: Optional[str] = None,
            page: int = 1,
            limit: int = 20,
            sort: abstraction.CatalogSort = abstraction.CatalogSort.POPULARITY
        ) -> hrequests.Response:
        """Возвращает количество и список товаров в категории/подкатегории."""
        if page < 1: raise ValueError("`page` must be greater than 0")
        elif limit > 27 or limit < 1: raise ValueError("`limit` must be in range 1-27")
        
        url = f"{self.CATALOG_URL}/v1/product/in/{category_alias}"
        if subcategory_alias: url += f"/{subcategory_alias}"
        url += f"?page={page}&limit={limit}&sort={sort}"
        
        return self._parent._request("POST", url=url)


class ProductService:
    """Сервис для работы с товарами в каталоге."""
    def __init__(self, parent: "FixPriceAPI", CATALOG_URL: str):
        self._parent: "FixPriceAPI" = parent
        self.CATALOG_URL: str = CATALOG_URL

    def balance(
            self,
            product_id: int,
            in_stock: bool = True,
            search: Optional[str] = None
        ) -> hrequests.Response:
        """
        Проверка наличия товара в точках города.
        Возвращает информацию о магазине и int количество товара.
        `city_id` в базовом классе должен быть обязательно указан, иначе ошибка!

        `in_stock` - фильтрует только те магазины, в которых есть товар, иначе все.
        `search` - фильтр по поисковому адресу.
        """
        if self._parent.city_id == None: raise ValueError("City ID is not set")

        url = f"{self.CATALOG_URL}/v1/store/balance/{product_id}?canPickup=all"
        if search: url += f"&addressPart={search}"
        if in_stock: url += "&inStock=true"

        return self._parent._request("GET", url)
