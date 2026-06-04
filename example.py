import asyncio

from fixprice_api import FixPriceAPI


async def main():
    async with FixPriceAPI() as api:
        assert api is not None
        # Catalog
        tree = (await api.Catalog.tree()).json()
        print(f"Первая категория: {tree[next(iter(tree))]['alias']}")
        products_list = (await api.Catalog.products_list(category_alias=tree[next(iter(tree))]["alias"])).json()
        print(f"Первый товар: {products_list[0]}")
        balance = (await api.Catalog.Products.balance(product_id=products_list[0]["id"])).json()
        print(f"Первый баланс: {balance[0]}")
        info = (await api.Catalog.Products.info(url=products_list[0]["url"])).json()
        print(f"Информация о товаре: {info}")

        # Geolocation
        en = (await api.Geolocation.countries_list(alias="en")).json()
        print(f"Первая страна en: {en[0]}")
        ru = (await api.Geolocation.countries_list(alias="ru")).json()
        print(f"Первая страна ru: {ru[0]}")
        regions = (await api.Geolocation.regions_list()).json()
        print(f"Первый регион: {regions[0]}")
        cities = (await api.Geolocation.cities_list(country_id=en[1]["id"])).json()
        print(f"Первый город: {cities[0]}")
        city_info = (await api.Geolocation.city_info(city_id=cities[0]["id"])).json()
        print(f"Информация о городе: {city_info}")
        search = (await api.Geolocation.search(country_id=en[0]["id"], city_id=cities[0]["id"])).json()
        print(f"Первый магазин: {search[0]}")

        # Advertising
        home_brands = (await api.Advertising.home_brands_list()).json()
        print(f"Первая рекламная запись: {home_brands[0]}")

        # General
        # Загрузка изображения по прямой ссылке.
        download_image = (await api.General.download_image(url=products_list[0]["images"][0]["src"])).image()
        _ = download_image


if __name__ == "__main__":
    asyncio.run(main())
