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

