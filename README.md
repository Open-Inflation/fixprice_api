<div align="center">
# FixPriceAPI

![Tests last run (ISO)](https://img.shields.io/badge/dynamic/json?label=Tests%20last%20run&query=%24.workflow_runs%5B0%5D.updated_at&url=https%3A%2F%2Fapi.github.com%2Frepos%2FOpen-Inflation%2Ffixprice_api%2Factions%2Fworkflows%2Ftests.yml%2Fruns%3Fper_page%3D1%26status%3Dcompleted&logo=githubactions&cacheSeconds=300)
[![Tests](https://github.com/Open-Inflation/fixprice_api/actions/workflows/tests.yml/badge.svg)](https://github.com/Open-Inflation/fixprice_api/actions/workflows/tests.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/fixprice_api)
![PyPI - Package Version](https://img.shields.io/pypi/v/fixprice_api?color=blue)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/fixprice_api?label=PyPi%20downloads)](https://pypi.org/project/fixprice-api/)
[![License](https://img.shields.io/github/license/Open-Inflation/fixprice_api)](https://github.com/Open-Inflation/fixprice_api/blob/main/LICENSE)
[![Ruff](https://img.shields.io/badge/linting-Ruff-blue?logo=ruff&logoColor=white)](https://github.com/astral-sh/ruff)
[![Discord](https://img.shields.io/discord/792572437292253224?label=Discord&labelColor=%232c2f33&color=%237289da)](https://discord.gg/UnJnGHNbBp)
[![Telegram](https://img.shields.io/badge/Telegram-24A1DE)](https://t.me/miskler_dev)

Аснинхронный неофициальный API клиент для сайта fix-price.com

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

```

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

Для более подробной информации смотрите референсы [документации](https://open-inflation.github.io/fixprice_api/quick_start).

<div align="center">

### Report

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/fixprice_api/issues)!

</div>
