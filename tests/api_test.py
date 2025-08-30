from fixprice_api import FixPriceAPI

# Advertising
def test_home_brands_list(api, schemashot):
    response = api.Advertising.home_brands_list()
    open("tt.txt", "w").write(str(response.raw))
    schemashot.assert_json_match(response.json(), api.Advertising.home_brands_list)

# Catalog


# General

# Geolocation

