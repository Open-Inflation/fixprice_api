import pytest
from fixprice_api import FixPriceAPI


@pytest.fixture(scope="session")
def anyio_backend():
    """
    Переопределяет фикстуру anyio_backend, чтобы использовать asyncio
    для всей сессии, устраняя ScopeMismatch с фикстурой 'api'.
    """
    return "asyncio"


@pytest.fixture(scope="session")
async def api():
    """
    Открываем один экземпляр клиента на всю сессию тестов.
    Корректно зовём менеджер контекста вручную.
    """
    async with FixPriceAPI() as client:
        yield client


@pytest.fixture(scope="session")
async def cities_list_json(api):
    """Кэш списка городов на сессию."""
    resp = await api.Geolocation.cities_list(country_id=2)
    data = resp.json()
    return data


@pytest.fixture(scope="session")
async def tree_json(api):
    """Кэш дерева категорий на сессию."""
    resp = await api.Catalog.tree()
    data = resp.json()
    return data


@pytest.fixture(scope="session")
async def first_category_alias(tree_json):
    """alias первой категории из дерева."""
    return tree_json[0]["alias"]


@pytest.fixture(scope="session")
async def products_list_json(api: FixPriceAPI, first_category_alias):
    """Кэш списка товаров по первой категории."""
    resp = await api.Catalog.products_list(category_alias=first_category_alias)
    data = resp.json()
    return data