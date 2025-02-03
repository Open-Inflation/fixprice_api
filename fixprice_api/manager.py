from .api import FixPriceAPI
from io import BytesIO
from .abstraction import CatalogSort


class FixPrice:
    BASE_URL = "https://api.fix-price.com/buyer/v1"
    def __init__(self):
        self.api = FixPriceAPI()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.api.__aexit__(*exc)
    
    async def categories_list(self) -> dict:
        return await self.api.fetch(f"{self.BASE_URL}/category/menu")
    
    async def products_list(
            self,
            category_alias: str,
            subcategory_alias: str = None,
            page: int = 1,
            limit: int = 20,
            sort: CatalogSort = CatalogSort.POPULARITY
        ) -> dict:
        url = f"{self.BASE_URL}/product/in/{category_alias}"
        if subcategory_alias: url += f"/{subcategory_alias}"
        url += f"?page={page}&limit={limit}&sort={sort}"
        
        print(url)
        return await self.api.fetch(url=url, method="POST")
    
    async def download_image(self, url: str) -> BytesIO:
        """Скачать изображение с сайта."""
        return await self.api.download_image(url)

    # TODO функция выбора города (поиск id городов по названию), информация о городе по id, страница товара, проверка наличия товара в точках города, получение информации о точках, получение списка городов, получение списка стран
