from .api import FixPriceAPI
from io import BytesIO
from .abstraction import CatalogSort


class FixPrice:
    BASE_URL_V1 = "https://api.fix-price.com/buyer/v1"
    BASE_URL_V2 = "https://api.fix-price.com/buyer/v2"

    def __init__(self):
        self._api = FixPriceAPI()

        self._geolocation = self._ClassGeolocation(self)
        self._catalog = self._ClassCatalog(self)
        self._store = self._ClassStore(self)
        self._general = self._ClassGeneral(self)

        self._city_id = None
        self._language = None

        self._set_headers()

    async def __aenter__(self):
        await self._api.__aenter__()
        return self

    async def __aexit__(self, *exc):
        await self._api.__aexit__(*exc)
    
    @property
    def city_id(self):
        """ID города используемый как фильтр каталога. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `3` (Москва)."""
        return self._city_id

    @city_id.setter
    def city_id(self, city_id: int):
        if (
            not isinstance(city_id, int) and \
            not isinstance(city_id, float) \
            and(not isinstance(city_id, str) and city_id.isdigit())
        ):
            raise TypeError("`city_id` must be int")
        elif int(city_id) < 1:
            raise ValueError("`city_id` must be greater than 0")

        self._city_id = str(int(city_id))
        self._set_headers()

    @property
    def language(self):
        """Язык используемый как фильтр каталога. ISO-2. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `ru` (Русский)."""
        return self._language

    @language.setter
    def language(self, language: str):
        if not isinstance(language, str): raise TypeError("`language` must be str")
        if not len(language) in [2, 5]: raise ValueError("`language` must be IETF BCP 47. Length must be 2 (ex. `en`) or 5 (ex. `en-AE`)")

        self._language = language
        self._set_headers()
    
    def _set_headers(self):
        self._api.headers = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"}
        if self.city_id: self._api.headers["x-city"] = self.city_id
        if self.language: self._api.headers["x-language"] = self.language

    async def _fetch(self, url: str, method: str = "GET", return_data: bool = False, **kwargs) -> tuple[dict, dict]:
        data, response = await self._api.fetch(url, method, **kwargs)

        if self.city_id == None and data["city"]: self.city_id = data["city"]
        if self.language == None and data["language"]: self.language = data["language"]

        if return_data:
            return data, response
        else:
            return response

    class _ClassCatalog:
        def __init__(self, parent):
            self._parent = parent

        async def categories_list(self) -> dict:
            """Возвращает список категорий."""
            return await self._parent._fetch(f"{self._parent.BASE_URL_V1}/category/menu")
        
        async def products_list(
                self,
                category_alias: str,
                subcategory_alias: str = None,
                page: int = 1,
                limit: int = 20,
                sort: CatalogSort = CatalogSort.POPULARITY
            ) -> tuple[int, dict]:
            """Возвращает количество и список товаров в категории/подкатегории."""
            if page < 1: raise ValueError("`page` must be greater than 0")
            elif limit > 27 or limit < 1: raise ValueError("`limit` must be in range 1-27")
            
            url = f"{self._parent.BASE_URL_V1}/product/in/{category_alias}"
            if subcategory_alias: url += f"/{subcategory_alias}"
            url += f"?page={page}&limit={limit}&sort={sort}"
            
            data, response = await self._parent._fetch(url=url, method="POST", return_data=True)

            return data["count"], response
        
        async def home_brands_list(self) -> dict:
            """Возвращает список брендов логотипы которых должны отображаться на главной. Является рекламой."""
            return await self._parent._fetch(f"{self._parent.BASE_URL_V1}/home/brand")

    class _ClassGeolocation:
        def __init__(self, parent):
            self._parent = parent

        async def country_list(self, alias: str = None) -> dict:
            """Возвращает список всех стран, их id и название. `alias` - работает как сортировка."""
            url = f"{self._parent.BASE_URL_V1}/location/country"
            if alias:
                if len(alias) != 2: raise ValueError("`alias` must be ISO-2. Length must be 2")

                url += f"?alias={alias.upper()}"
            
            return await self._parent._fetch(url=url)

        async def region_list(self, country_id: int = None) -> dict:
            """Возвращает список всех регионов, их id и название. Если фильтр не применен - выдача всех регионов независимо от страны."""
            url = f"{self._parent.BASE_URL_V1}/location/region"
            if not country_id: url += f"?countryId={country_id}"

            return await self._parent._fetch(url=url)
        
        async def city_list(self, country_id: int) -> dict:
            """Возвращает список всех городов, их id и название, геопозицию, регион и тип населенного пункта. По умолчанию - по РФ."""
            url = f"{self._parent.BASE_URL_V1}/location/city"
            if country_id: url += f"?countryId={country_id}"

            return await self._parent._fetch(url=url)

        async def city_info(self, city_id: int) -> dict:
            """Возвращает информацию о городе."""
            return await self._parent._fetch(f"{self._parent.BASE_URL_V1}/location/city/{city_id}")
        
        async def my_geoposition(self) -> dict:
            """Возвращает информацию о предполагаемой геопозиции на основе IP."""
            return await self._parent._fetch(f"{self._parent.BASE_URL_V2}/geo/ip")

    class _ClassStore:
        def __init__(self, parent):
            self._parent = parent

        async def search(
            self,
            country_id: int = None,
            region_id: int = None,
            city_id: int = None,
            search: str = None
        ) -> dict:
            """Поиск магазинов."""
            url = f"{self._parent.BASE_URL_V1}/store?searchType=metro&canPickup=all&showTemporarilyClosed=all"

            if country_id: url += f"&countryId={country_id}"
            if region_id: url += f"&regionId={region_id}"
            if city_id: url += f"&cityId={city_id}"
            if search: url += f"&addressPart={search}"

            return await self._parent._fetch(url)
        
        async def product_balance(
                self,
                product_id: int,
                in_stock: bool = True,
                search: str = None
            ) -> list[dict]:
            """
            Проверка наличия товара в точках города.
            Возвращает информацию о магазине и int количество товара.
            `city_id` в базовом классе должен быть обязательно указан, иначе ошибка!

            `in_stock` - фильтрует только те магазины, в которых есть товар, иначе все.
            `search` - фильтр по поисковому адресу.
            """
            if self._parent.city_id == None: raise ValueError("City ID is not set")

            url = f"{self._parent.BASE_URL_V1}/store/balance/{product_id}?canPickup=all"
            if search: url += f"&addressPart={search}"
            if in_stock: url += "&inStock=true"

            return await self._parent._fetch(url)

    class _ClassGeneral:
        def __init__(self, parent):
            self._parent = parent

        async def download_image(self, url: str) -> BytesIO:
            """Скачать изображение с сайта."""
            return await self._parent._api.download_image(url)

    @property
    def Geolocation(self):
        """Инструментарий для получения стран, регионов, городов, получение геопозиции."""
        return self._geolocation

    @property
    def Catalog(self):
        """Работа с каталогом."""
        return self._catalog

    @property
    def Store(self):
        """Поиск и работа с магазинами."""
        return self._store

    @property
    def General(self):
        """Загрузка изображений."""
        return self._general
