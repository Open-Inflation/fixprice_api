import pytest
from fixprice_api import FixPriceAPI

@pytest.fixture(scope="session")
def api():
    """
    Открываем один экземпляр клиента на всю сессию тестов.
    Корректно зовём менеджер контекста вручную.
    """
    client = FixPriceAPI()
    client.__enter__()  # эквивалент 'with FixPriceAPI() as api'
    try:
        yield client
    finally:
        client.__exit__(None, None, None)



@pytest.fixture(scope="session")
def tree_json(api):
    """Кэш дерева категорий на сессию."""
    resp = api.Catalog.tree()
    data = resp.json()
    return data


@pytest.fixture(scope="session")
def first_category_alias(tree_json):
    """alias первой категории из дерева."""
    return tree_json[0]["alias"]


@pytest.fixture(scope="session")
def products_list_json(api: FixPriceAPI, first_category_alias):
    """Кэш списка товаров по первой категории."""
    resp = api.Catalog.products_list(category_alias=first_category_alias)
    data = resp.json()
    return data
