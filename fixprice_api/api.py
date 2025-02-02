import aiohttp

class FixPriceAPI:
    def __init__(self):
        self.session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self.session.close()
    
    async def fetch(self, path: str) -> dict:
        async with self.session.get(f"{path}") as response:
            return await response.json()
