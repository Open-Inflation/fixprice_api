import asyncio
from api import FixPriceAPI
from pprint import pprint


class FixPrice:
    BASE_URL = "https://api.fix-price.com"
    def __init__(self):
        self.api = FixPriceAPI()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.api.__aexit__(*exc)
    
    async def catalog(self):
        return await self.api.fetch(f"{self.BASE_URL}/buyer/v1/category/menu")



async def main():
    async with FixPrice() as fixprice:
        pprint(await fixprice.catalog())

if __name__ == "__main__":
    asyncio.run(main())