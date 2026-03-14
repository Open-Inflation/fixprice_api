<div align="center">

# FixPrice API (not official)

![Tests last run (ISO)](https://img.shields.io/badge/dynamic/json?label=Tests%20last%20run&query=%24.workflow_runs%5B0%5D.updated_at&url=https%3A%2F%2Fapi.github.com%2Frepos%2FOpen-Inflation%2Ffixprice_api%2Factions%2Fworkflows%2Ftests.yml%2Fruns%3Fper_page%3D1%26status%3Dcompleted&logo=githubactions&cacheSeconds=300)
[![Tests](https://github.com/Open-Inflation/fixprice_api/actions/workflows/tests.yml/badge.svg)](https://github.com/Open-Inflation/fixprice_api/actions/workflows/tests.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fixprice_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/fixprice_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fixprice_api?label=PyPi%20downloads)](https://pypi.org/project/fixprice-api/)
[![License](https://img.shields.io/github/license/Open-Inflation/fixprice_api)](https://github.com/Open-Inflation/fixprice_api/blob/main/LICENSE)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)

FixPrice (Фикс Прайс) - https://fix-price.com/

**[⭐ Star us on GitHub](https://github.com/Open-Inflation/fixprice_api)** | **[📚 Read the Docs](https://open-inflation.github.io/fixprice_api/quick_start)** | **[🐛 Report Bug](https://github.com/Open-Inflation/fixprice_api/issues)**

### Принцип работы

</div>

> Библиотека полностью повторяет сетевую работу обычного пользователя на сайте.

<div align="center">

# Usage

</div>

```bash
pip install fixprice_api
python -m camoufox fetch
```

```py
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
```

```bash
> Первая категория: kosmetika-i-gigiena
> Первый товар: Крем для рук и тела, 150 мл (2345678)
> Текущий city_id: 3
> Проверено магазинов: 339
> Image format: WEBP, size: (190, 190)
```

Для более подробной информации смотрите референсы [документации](https://open-inflation.github.io/fixprice_api/quick_start).

---

## Автотесты API (pytest + snapshots)

В проекте используется автотест-фреймворк из `human_requests`:

- endpoint-методы в бизнес-коде помечаются `@autotest`;
- pytest-плагин сам находит эти методы и запускает их;
- JSON-ответы проверяются через `pytest-jsonschema-snapshot` (`schemashot`);
- параметры вызова и пост-обработка результата регистрируются в `tests/api_test.py` через:
  - `@autotest_params`
  - `@autotest_hook`
  - `@autotest_depends_on`

Минимальная конфигурация уже включена в `pyproject.toml`:

```ini
[tool.pytest.ini_options]
anyio_mode = "auto"
autotest_start_class = "fixprice_api.FixPriceAPI"
```

Запуск тестов:

```bash
pytest
```

Важно:

- используется `pytest-anyio` (не `pytest-asyncio`);
- ручные тесты остаются только для кейсов, которые не относятся к JSON-схемам endpoint-методов (например, `download_image`).

---

<div align="center">

### Report

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/fixprice_api/issues)!

</div>
