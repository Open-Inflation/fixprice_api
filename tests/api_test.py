from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from human_requests import autotest_data, autotest_depends_on, autotest_hook, autotest_params

from fixprice_api.endpoints.advertising import ClassAdvertising
from fixprice_api.endpoints.catalog import ClassCatalog
from fixprice_api.endpoints.catalog.products import ClassProducts
from fixprice_api.endpoints.geolocation import ClassGeolocation

if TYPE_CHECKING:
    from human_requests.autotest import AutotestCallContext, AutotestContext, AutotestDataContext


@autotest_hook(target=ClassCatalog.tree)
def _capture_catalog_tree_json(resp, data, ctx: AutotestContext) -> None:
    del resp
    ctx.state["catalog_tree_json"] = data


@autotest_hook(target=ClassCatalog.products_list)
def _capture_catalog_products_list_json(resp, data, ctx: AutotestContext) -> None:
    del resp
    ctx.state["catalog_products_list_json"] = data


@autotest_hook(target=ClassGeolocation.countries_list)
def _capture_geolocation_countries_list_json(resp, data, ctx: AutotestContext) -> None:
    del resp
    ctx.state["geolocation_countries_list_json"] = data


@autotest_hook(target=ClassGeolocation.cities_list)
def _capture_geolocation_cities_list_json(resp, data, ctx: AutotestContext) -> None:
    del resp
    ctx.state["geolocation_cities_list_json"] = data


@autotest_params(target=ClassCatalog.tree)
def _params_catalog_tree_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {}
    except Exception as exc:
        pytest.fail(f"[app.func.CATALOG_TREE.examples.tree] could not derive test parameters: {exc}")


@autotest_depends_on(ClassCatalog.tree)
@autotest_params(target=ClassCatalog.products_list)
def _params_catalog_products_list_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"category_alias": ctx.state["catalog_tree_json"][next(iter(ctx.state["catalog_tree_json"]))]["alias"]}
    except Exception as exc:
        pytest.fail(f"[app.func.CATALOG_PRODUCTS_LIST.examples.products_list] could not derive test parameters: {exc}")


@autotest_depends_on(ClassCatalog.products_list)
@autotest_params(target=ClassProducts.balance)
def _params_catalog__products_balance_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"product_id": ctx.state["catalog_products_list_json"][0]["id"]}
    except Exception as exc:
        pytest.fail(f"[app.func.CATALOG_PRODUCT_BALANCE.examples.balance] could not derive test parameters: {exc}")


@autotest_depends_on(ClassCatalog.products_list)
@autotest_params(target=ClassProducts.info)
def _params_catalog__products_info_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"url": ctx.state["catalog_products_list_json"][0]["url"]}
    except Exception as exc:
        pytest.fail(f"[app.func.CATALOG_PRODUCT_INFO.examples.info] could not derive test parameters: {exc}")


@autotest_params(target=ClassGeolocation.countries_list)
def _params_geolocation_countries_list_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"alias": "en"}
    except Exception as exc:
        pytest.fail(f"[app.func.GEOLOCATION_COUNTRIES_LIST.examples.en] could not derive test parameters: {exc}")


@autotest_params(target=ClassGeolocation.regions_list)
def _params_geolocation_regions_list_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {}
    except Exception as exc:
        pytest.fail(f"[app.func.GEOLOCATION_REGIONS_LIST.examples.regions] could not derive test parameters: {exc}")


@autotest_depends_on(ClassGeolocation.countries_list)
@autotest_params(target=ClassGeolocation.cities_list)
def _params_geolocation_cities_list_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"country_id": ctx.state["geolocation_countries_list_json"][1]["id"]}
    except Exception as exc:
        pytest.fail(f"[app.func.GEOLOCATION_CITIES_LIST.examples.cities] could not derive test parameters: {exc}")


@autotest_depends_on(ClassGeolocation.cities_list)
@autotest_params(target=ClassGeolocation.city_info)
def _params_geolocation_city_info_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"city_id": ctx.state["geolocation_cities_list_json"][0]["id"]}
    except Exception as exc:
        pytest.fail(f"[app.func.GEOLOCATION_CITY_INFO.examples.city_info] could not derive test parameters: {exc}")


@autotest_depends_on(ClassGeolocation.countries_list)
@autotest_depends_on(ClassGeolocation.cities_list)
@autotest_params(target=ClassGeolocation.search)
def _params_geolocation_search_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {"country_id": ctx.state["geolocation_countries_list_json"][0]["id"], "city_id": ctx.state["geolocation_cities_list_json"][0]["id"]}
    except Exception as exc:
        pytest.fail(f"[app.func.GEOLOCATION_SHOP_SEARCH.examples.search] could not derive test parameters: {exc}")


@autotest_params(target=ClassAdvertising.home_brands_list)
def _params_advertising_home_brands_list_json(ctx: AutotestCallContext) -> dict[str, object]:
    try:
        return {}
    except Exception as exc:
        pytest.fail(f"[app.func.ADVERTISING_HOME_BRANDS_LIST.examples.home_brands] could not derive test parameters: {exc}")


@autotest_data(name="unstandard_headers")
def _unstandard_headers_data(ctx: AutotestDataContext) -> dict[str, object]:
    return ctx.api.unstandard_headers


@autotest_data(name="unstandard_urls")
def _unstandard_urls_data(ctx: AutotestDataContext) -> dict[str, object]:
    return ctx.api.unstandard_urls


async def test_class_general_download_image(api, catalog_products_list_json):
    """Загрузка изображения по прямой ссылке."""
    response = await api.General.download_image(url=catalog_products_list_json[0]["images"][0]["src"])
    image = response.image()
    assert image.size[0] > 0
    assert image.size[1] > 0
    assert image.format is not None
