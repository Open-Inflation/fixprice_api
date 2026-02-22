from typing import Any

import pytest
from fixprice_api.endpoints.catalog import ClassCatalog, ProductService
from fixprice_api.endpoints.geolocation import ClassGeolocation
from human_requests import autotest_data, autotest_depends_on, autotest_hook, autotest_params
from human_requests.autotest import AutotestCallContext, AutotestContext, AutotestDataContext
from PIL import Image


@autotest_hook(target=ClassCatalog.tree)
def _capture_first_category(
    resp: Any,
    data: dict[str, Any],
    ctx: AutotestContext,
) -> None:
    del resp
    if not isinstance(data, dict) or not data:
        pytest.fail("Catalog.tree returned empty data.")

    first_node = data[next(iter(data))]
    alias = first_node.get("alias")
    if not isinstance(alias, str) or not alias:
        pytest.fail("Catalog.tree did not return a valid category alias.")

    ctx.state["autotest_first_category_alias"] = alias


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.products_list)
def _products_list_params(ctx: AutotestCallContext) -> dict[str, str]:
    cached_alias = ctx.state.get("autotest_first_category_alias")
    if isinstance(cached_alias, str):
        return {"category_alias": cached_alias}
    pytest.fail("Catalog.products_list depends on Catalog.tree.")


@autotest_params(target=ClassGeolocation.cities_list)
def _cities_list_params(ctx: AutotestCallContext) -> dict[str, int]:
    del ctx
    return {"country_id": 2}


@autotest_hook(target=ClassGeolocation.cities_list)
def _capture_city_id(
    resp: Any,
    data: list[dict[str, Any]],
    ctx: AutotestContext,
) -> None:
    del resp
    if not isinstance(data, list) or not data:
        pytest.fail("Geolocation.cities_list returned empty data.")

    city_id = data[0].get("id")
    if not isinstance(city_id, int):
        pytest.fail("Geolocation.cities_list did not return a valid city id.")

    ctx.state["autotest_city_id"] = city_id


@autotest_depends_on(ClassGeolocation.cities_list)
@autotest_params(target=ClassGeolocation.city_info)
def _city_info_params(ctx: AutotestCallContext) -> dict[str, int]:
    cached_city_id = ctx.state.get("autotest_city_id")
    if isinstance(cached_city_id, int):
        return {"city_id": cached_city_id}
    pytest.fail("Geolocation.city_info depends on Geolocation.cities_list.")


@autotest_hook(target=ClassCatalog.products_list)
def _capture_product_id(
    resp: Any,
    data: list[dict[str, Any]],
    ctx: AutotestContext,
) -> None:
    del resp
    if not isinstance(data, list) or not data:
        pytest.fail("Catalog.products_list returned empty data.")

    product_id = data[0].get("id")
    if not isinstance(product_id, int):
        pytest.fail("Catalog.products_list did not return a valid product id.")

    ctx.state["autotest_product_id"] = product_id


@autotest_depends_on(ClassCatalog.products_list)
@autotest_params(target=ProductService.balance)
def _product_balance_params(ctx: AutotestCallContext) -> dict[str, int]:
    cached_id = ctx.state.get("autotest_product_id")
    if isinstance(cached_id, int):
        return {"product_id": cached_id}
    pytest.fail("ProductService.balance depends on Catalog.products_list.")


@autotest_data(name="unstandard_headers")
def _unstandard_headers_data(ctx: AutotestDataContext) -> dict[str, Any]:
    return ctx.api.unstandard_headers


async def test_download_image(api, products_list_json):
    img_url = products_list_json[0]["images"][0]["src"]
    resp = await api.General.download_image(url=img_url)
    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")
