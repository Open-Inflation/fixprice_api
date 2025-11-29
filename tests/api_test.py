from io import BytesIO
from PIL import Image

# Advertising
async def test_home_brands_list(api, schemashot):
    response = await api.Advertising.home_brands_list()
    rjson = response.json()
    schemashot.assert_json_match(rjson, api.Advertising.home_brands_list)

# Catalog

async def test_tree(api, schemashot, tree_json):
    # уже распарсено фикстурой, но для привязки к callable передаём эталон из API
    schemashot.assert_json_match(tree_json, api.Catalog.tree)

async def test_products_list(api, schemashot, products_list_json):
    schemashot.assert_json_match(products_list_json, api.Catalog.products_list)

async def test_product_balance(api, schemashot, products_list_json):
    balance = await api.Catalog.Product.balance(product_id=products_list_json[0]["id"])
    bjson = balance.json()
    schemashot.assert_json_match(bjson, api.Catalog.Product.balance)

# General

async def test_unstandard_headers(api, schemashot):
    schemashot.assert_json_match(api.unstandard_headers, "unstandard_headers")

async def test_download_image(api, products_list_json):
    img_url = products_list_json[0]["images"][0]["src"]
    resp = await api.General.download_image(url=img_url)
    with Image.open(resp) as img:
        fmt = img.format.lower()
    assert fmt in ("png", "jpeg", "webp")

# Geolocation

async def test_countries_list(api, schemashot):
    resp = await api.Geolocation.countries_list()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.countries_list)

async def test_regions_list(api, schemashot):
    resp = await api.Geolocation.regions_list()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.regions_list)

async def test_cities_list(api, schemashot, cities_list_json):
    schemashot.assert_json_match(cities_list_json, api.Geolocation.cities_list)

async def test_city_info(api, schemashot, cities_list_json):
    info = await api.Geolocation.city_info(city_id=cities_list_json[0]["id"])
    rjson = info.json()
    schemashot.assert_json_match(rjson, api.Geolocation.city_info)

async def test_search_shops(api, schemashot):
    resp = await api.Geolocation.Shop.search()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.Shop.search)

#import asyncio
#async def test_ttr_shops(api, schemashot):
#    await asyncio.sleep(9999999)
