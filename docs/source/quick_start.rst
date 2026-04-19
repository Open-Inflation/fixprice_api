Quick Start
===========

.. code-block:: console

    pip install fixprice_api
    python -m camoufox fetch

.. code-block:: python
    
    import asyncio
    from fixprice_api import FixPriceAPI, CatalogSort
    from PIL import Image


    async def main():
        async with FixPriceAPI() as api:
            # 1. Получаем дерево категорий
            tree_data = (await api.Catalog.tree()).json()
            first_alias = tree_data[next(iter(tree_data))]["alias"]
            print(f"Первая категория: {first_alias}")

            # 2. Список товаров в категории
            products = (
                await api.Catalog.products_list(
                    category_alias=first_alias,
                    page=1,
                    limit=24,
                    sort=CatalogSort.POPULARITY,
                )
            ).json()
            first_product_id = products[0]["id"]
            first_product_url = products[0]["url"]
            print(f"Первый товар: {products[0]['title']!s:.60s} ({first_product_id})")

            # 3. Геолокация (влияет на каталог и баланс)
            cities = (await api.Geolocation.cities_list(country_id=2)).json()  # Россия
            api.city_id = cities[0]["id"]
            print(f"Текущий city_id: {api.city_id}")

            # 4. Проверка наличия товара по магазинам
            balance = (await api.Catalog.Product.balance(product_id=first_product_id)).json()
            print(f"Проверено магазинов: {len(balance)}")

            # 5. Подробное инфо о товаре
            info = (await api.Catalog.Product.info(url=first_product_url)).json()
            print(f"Подробно о товаре: {list(info.keys())}")

            # 6. Загрузка изображения
            image_url = products[0]["images"][0]["src"]
            image_stream = await api.General.download_image(image_url)
            with Image.open(image_stream) as img:
                print(f"Image format: {img.format}, size: {img.size}")


    if __name__ == "__main__":
        asyncio.run(main())

.. code-block:: console

    > Active offers output: {'title': 'НАДО УСПЕТЬ', 'description': 'Новые товары каждую неделю.\r\nКоличество ограниченно!', 'i...
    > Cities list output: {'count': 14, 'next': None, 'previous': None, 'page_size': 30, 'total_pages': 1, 'items': [{'distanc...
    > Categories list output: [{'id': 133, 'name': 'Основной каталог', 'image': None, 'icon': None, 'depth': 1, 'is_adults': False...
    > Items list output: {'count': 3800, 'next': 2, 'previous': None, 'page_size': 100, 'total_pages': 38, 'items': [{'id': 2...


Для более подробной информации смотрите референсы :class:`~fixprice_api.endpoints.catalog.ClassCatalog`, :class:`~fixprice_api.endpoints.geolocation.ClassGeolocation`, :class:`~fixprice_api.endpoints.general.ClassGeneral`, :class:`~fixprice_api.endpoints.advertising.ClassAdvertising` документации.
