import time
#import imghdr


# Advertising
def test_home_brands_list(api, schemashot):
    response = api.Advertising.home_brands_list()
    rjson = response.json()
    schemashot.assert_json_match(rjson, api.Advertising.home_brands_list)

# Catalog

def test_tree(api, schemashot, tree_json):
    # уже распарсено фикстурой, но для привязки к callable передаём эталон из API
    schemashot.assert_json_match(tree_json, api.Catalog.tree)

def test_products_list(api, schemashot, products_list_json):
    schemashot.assert_json_match(products_list_json, api.Catalog.products_list)

def test_product_balance(api, schemashot, products_list_json):
    balance = api.Catalog.Product.balance(product_id=products_list_json[0]["id"])
    bjson = balance.json()
    schemashot.assert_json_match(bjson, api.Catalog.Product.balance)

# General

def test_download_image(api, products_list_json):
    img_url = products_list_json[0]["images"][0]["src"]
    resp = api.General.download_image(url=img_url)
    assert resp.status_code == 200
    assert resp.headers["Content-Type"].startswith("image/")
#    fmt = imghdr.what(None, resp.raw)
#    assert fmt in ("png", "jpeg", "webp")

# Geolocation

def test_countries_list(api, schemashot):
    resp = api.Geolocation.countries_list()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.countries_list)

def test_regions_list(api, schemashot):
    resp = api.Geolocation.regions_list()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.regions_list)

def test_cities_list(api, schemashot, cities_list_json):
    schemashot.assert_json_match(cities_list_json, api.Geolocation.cities_list)

def test_city_info(api, schemashot, cities_list_json):
    info = api.Geolocation.city_info(city_id=cities_list_json[0]["id"])
    rjson = info.json()
    schemashot.assert_json_match(rjson, api.Geolocation.city_info)

def test_search_shops(api, schemashot):
    resp = api.Geolocation.Shop.search()
    rjson = resp.json()
    schemashot.assert_json_match(rjson, api.Geolocation.Shop.search)

