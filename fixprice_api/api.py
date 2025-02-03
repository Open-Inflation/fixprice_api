import aiohttp
from io import BytesIO


class FixPriceAPI:
    def __init__(self):
        self._session = aiohttp.ClientSession()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self._session.close()
    
    async def fetch(self, url: str, method: str = "GET", **kwargs) -> dict:
        # TODO Возвращать так же поля x-city (id города), x-count (количество товаров удовлетворяющих запросу), x-launguage (язык ответа)

        async with self._session.request(method, url, **kwargs) as response:
            if response.status != 200:
                raise ValueError(f"Failed to fetch data, status code: {response.status}")
            return await response.json()

    async def download_image(self, url: str) -> BytesIO:
        if not self._session:
            await self.__aenter__()
        
        async with self._session.get(url) as response:
            if response.status == 200:
                image = BytesIO(await response.read())
                image.name = f"{url.split('/')[-1]}"

                return image
            else:
                raise ValueError(f"Failed to download image, status code: {response.status}")
