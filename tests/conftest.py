from __future__ import annotations

import pytest

from fixprice_api import FixPriceAPI


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def api():
    async with FixPriceAPI(test_mode=True) as client:
        yield client


@pytest.fixture(scope="session")
async def catalog_tree_json(api):
    resp = await api.Catalog.tree()
    data = resp.json()
    return data


@pytest.fixture(scope="session")
async def catalog_products_list_json(api, catalog_tree_json):
    resp = await api.Catalog.products_list(category_alias=catalog_tree_json[next(iter(catalog_tree_json))]["alias"])
    data = resp.json()
    return data
