"""Общий (не класифицируемый) функционал"""

from typing import TYPE_CHECKING
from io import BytesIO
from human_requests.abstraction import Proxy
from aiohttp_retry import ExponentialRetry, RetryClient

if TYPE_CHECKING:
    from fixprice_api.manager import FixPriceAPI


class ClassGeneral:
    """Общие методы API Перекрёстка.

    Включает методы для работы с изображениями, формой обратной связи,
    получения информации о пользователе и других общих функций.
    """

    def __init__(self, parent: "FixPriceAPI"):
        self._parent: "FixPriceAPI" = parent

    
    async def download_image(
        self, url: str, retry_attempts: int = 3, timeout: float = 10
    ) -> BytesIO:
        """Скачать изображение по URL."""
        retry_options = ExponentialRetry(
            attempts=retry_attempts, start_timeout=3.0, max_timeout=timeout
        )

        async with RetryClient(retry_options=retry_options) as retry_client:
            async with retry_client.get(url, raise_for_status=True, proxy=Proxy(self._parent.proxy).as_str()) as resp:
                body = await resp.read()
                file = BytesIO(body)
                file.name = url.split("/")[-1]
        return file
