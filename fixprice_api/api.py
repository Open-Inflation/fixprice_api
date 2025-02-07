import aiohttp
from io import BytesIO


class FixPriceAPI:
    def __init__(self):
        self._session = aiohttp.ClientSession()
        self.headers = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        await self._session.close()
    
    async def fetch(self, url: str, method: str = "GET", **kwargs) -> dict:
        kwargs["headers"] = self.headers
        
        async with self._session.request(method, url, **kwargs) as response:
            if response.status != 200:
                if response.status == 403:
                    raise ValueError(f"Failed to fetch data, anti-bot system detected. Change IP to RU. Code: {response.status}")
                elif response.status == 429:
                    raise ValueError(f"Oh, it's superheated! Try slower. Code: {response.status}")
                else:
                    raise ValueError(f"Failed to fetch data, unclassified status code: {response.status}")
            data = {"city": response.headers.get("x-city", None),
                    "count": response.headers.get("x-count", None),
                    "language": response.headers.get("x-language", None)}
            
            if data["city"] not in [None, self.headers.get("x-city", None)] and self.headers.get("x-city", None):
                raise ValueError(f"Unpredictable city ID: {data['city']}, expected: {self.headers.get('x-city', None)}")
            elif data["language"] not in [None, self.headers.get("x-language", None)] and self.headers.get("x-language", None):
                raise ValueError(f"Unpredictable language: {data['language']}, expected: {self.headers.get('x-language', None)}")

            return data, await response.json()

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
