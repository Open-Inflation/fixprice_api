import asyncio

from fixprice_api import FixPriceAPI


async def main():
    async with FixPriceAPI() as api:
        assert api is not None
        # Catalog
        tree = (await api.Catalog.tree()).json()
        print(f"Первая категория: {tree[next(iter(tree))]['alias']}")
        products_list = (await api.Catalog.products_list(category_alias=tree[next(iter(tree))]["alias"])).json()
        print(f"Первый товар: {products_list[0]['title']}")
        balance = (await api.Catalog.Products.balance(product_id=products_list[0]["id"])).json()
        print(f"Первый баланс: {balance[0]['address']}; {balance[0]['count']} шт")
        info = (await api.Catalog.Products.info(url=products_list[0]["url"])).json()
        print(f"Информация о товаре: {info['title']}")

        # Geolocation
        first_country = (await api.Geolocation.countries_list()).json()
        print(f"Первая страна: {first_country[0]['title']}")
        regions = (await api.Geolocation.regions_list()).json()
        print(f"Первый регион: {regions[0]['title']}")
        cities = (await api.Geolocation.cities_list(country_id=first_country[1]["id"])).json()
        print(f"Первый город: {cities[0]['name']}")
        city_info = (await api.Geolocation.city_info(city_id=cities[0]["id"])).json()
        print(f"Информация о городе: {city_info['name']} ({city_info['fiasid']})")
        search = (await api.Geolocation.search(country_id=first_country[0]["id"], city_id=cities[0]["id"])).json()
        print(f"Первый магазин: {search[0]['address']}")

        # Advertising
        home_brands = (await api.Advertising.home_brands_list()).json()
        print(f"Первая рекламная запись: {home_brands[0]['title']} {home_brands[0]['updatedAt']}")

        # General
        # Загрузка изображения по прямой ссылке.
        download_image = (await api.General.download_image(url=products_list[0]["images"][0]["src"])).image()
        _ = download_image


if __name__ == "__main__":
    asyncio.run(main())
