from typing import Any, Literal
import os
from dataclasses import dataclass, field
from collections import defaultdict
from human_requests import HumanBrowser, HumanContext, HumanPage
from human_requests.abstraction import Proxy, FetchResponse, HttpMethod
from human_requests.network_analyzer.anomaly_sniffer import (
    HeaderAnomalySniffer, WaitHeader, WaitSource)
from camoufox import AsyncCamoufox
from playwright.async_api import TimeoutError as PWTimeoutError

from .endpoints.catalog import ClassCatalog
from .endpoints.geolocation import ClassGeolocation
from .endpoints.advertising import ClassAdvertising
from .endpoints.general import ClassGeneral


# ---------------------------------------------------------------------------
# Главный клиент
# ---------------------------------------------------------------------------
def _pick_https_proxy() -> str | None:
    """Возвращает прокси из HTTPS_PROXY/https_proxy (если заданы)."""
    return os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")

@dataclass
class FixPriceAPI:
    """Клиент FixPrice."""

    timeout_ms: float       = 10000.0
    """Время ожидания ответа от сервера в миллисекундах."""
    headless: bool = True
    """Запускать браузер в headless режиме?"""
    proxy: str | dict | None = field(default_factory=_pick_https_proxy)
    """Прокси-сервер для всех запросов (если нужен). По умолчанию берет из окружения (если есть).
    Принимает как формат Playwright, так и строчный формат."""
    browser_opts: dict[str, Any] = field(default_factory=dict)
    """Дополнительные опции для браузера (см. https://camoufox.com/python/installation/)"""

    MAIN_SITE_URL: str = "https://fix-price.com/catalog"
    CATALOG_URL:   str = "https://api.fix-price.com/buyer"

    # будет создана в __post_init__
    session: HumanBrowser = field(init=False, repr=False)
    """Внутренняя сессия браузера для выполнения HTTP-запросов."""
    # будет создано в warmup
    ctx: HumanContext = field(init=False, repr=False)
    """Внутренний контекст сессии браузера"""
    page: HumanPage = field(init=False, repr=False)
    """Внутренний страница сессии браузера"""

    unstandard_headers: dict[str, str] = field(init=False, repr=False)
    """Список нестандартных заголовков пойманных при инициализации"""

    Geolocation: ClassGeolocation = field(init=False)
    """API для работы с геолокацией."""
    Catalog: ClassCatalog = field(init=False)
    """API для работы с каталогом товаров."""
    Advertising: ClassAdvertising = field(init=False)
    """API для работы с рекламой."""
    General: ClassGeneral = field(init=False)
    """API для работы с общими функциями."""

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.Geolocation = ClassGeolocation(self)
        self.Catalog = ClassCatalog(self)
        self.Advertising = ClassAdvertising(self)
        self.General = ClassGeneral(self)

    async def __aenter__(self):
        """Вход в контекстный менеджер с автоматическим прогревом сессии."""
        await self._warmup()
        return self

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    async def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения человекоподобности."""
        br = await AsyncCamoufox(
            headless=self.headless,
            proxy=Proxy(self.proxy).as_dict(),
            **self.browser_opts,
            block_images=True
        ).start()

        self.session = HumanBrowser.replace(br)
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()

        sniffer = HeaderAnomalySniffer(
            include_subresources=True,  # или False, если интересны только документы
            url_filter=lambda u: u.startswith(self.CATALOG_URL),
        )
        await sniffer.start(self.ctx)

        await self.page.goto(self.CATALOG_URL, wait_until="networkidle")

        ok = False
        try_count = 3
        while not ok or try_count <= 0:
            try_count -= 1
            try:
                await self.page.wait_for_selector(
                    "div#__nuxt", timeout=self.timeout_ms, state="attached"
                )
                ok = True
            except PWTimeoutError:
                await self.page.reload()
        if not ok:
            raise RuntimeError(self.page.content)
        
        await sniffer.wait(
            tasks=[
                WaitHeader(
                    source=WaitSource.REQUEST,
                    headers=["x-key"],
                )
            ],
            timeout_ms=self.timeout_ms,
        )

        result_sniffer = await sniffer.complete()
        # Результат: {заголовок: [уникальные значения]}
        result = defaultdict(set)

        # Проходим по всем URL в 'request'
        for _url, headers in result_sniffer["request"].items():
            for header, values in headers.items():
                result[header].update(values)  # добавляем значения, set уберёт дубли

        # Преобразуем set обратно в list
        self.unstandard_headers = {k: list(v)[0] for k, v in result.items()}

    async def __aexit__(self, *exc):
        """Выход из контекстного менеджера с закрытием сессии."""
        await self.close()

    async def close(self):
        """Закрыть HTTP-сессию и освободить ресурсы."""
        await self.session.close()
    

    @property
    def city_id(self) -> int | None:
        """ID города используемый как фильтр каталога. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `3` (Москва)."""
        x = self.unstandard_headers.get("x-city", None)
        if x: x = int(x)
        return x

    @city_id.setter
    def city_id(self, value: int | None) -> None:
        if value is None:
            self.unstandard_headers.pop("x-city", None)
        elif (
            not isinstance(value, (int, float)) \
            and(not isinstance(value, str) and value.isdigit())
        ):
            raise TypeError("`city_id` must be int")
        elif int(value) < 1:
            raise ValueError("`city_id` must be greater than 0")
        else:
            self.unstandard_headers.update({"x-city": int(value)})

    @property
    def language(self) -> str | None:
        """Язык используемый как фильтр каталога. ISO-2. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `ru` (Русский)."""
        return self.unstandard_headers.get("x-language", None)

    @language.setter
    def language(self, value: str | None) -> None:
        if not isinstance(value, str):
            raise TypeError("`language` must be str")
        if not len(value) in [2, 5]:
            raise ValueError("`language` must be IETF BCP 47. Length must be 2 (ex. `en`) or 5 (ex. `en-AE`)")
        elif value is None:
            self.unstandard_headers.pop("x-language", None)
        else:
            self.unstandard_headers.update({ # токен пойдёт в каждый запрос
                "x-language": value
            })

    @property
    def token(self) -> str | None:
        """Токен доступа для API запросов. READ-ONLY."""
        return self.unstandard_headers.get("x-key", None)

    @property
    def delivery_type(self) -> Literal["store", "pickup", "courier"] | None:
        """Способ получения заказа (влияет на каталог).
        
        store - самовывоз из магазина
        pickup - получить из ПВЗ
        courier - курьерская доставка"""
        return self.unstandard_headers.get("x-delivery-type", None)
    
    @delivery_type.setter
    def delivery_type(self, value: Literal["store", "pickup", "courier"]) -> None:
        self.unstandard_headers.update({"x-delivery-type": value})

    @property
    def store_id(self) -> str | None:
        """Индификатор магазина или ПВЗ. Обычно состоит из 1 латинской буквы и 3 цифр.
        В терминологии сайта называется PFM"""
        return self.unstandard_headers.get("x-pfm", None)

    @store_id.setter
    def store_id(self, value: str) -> None:
        self.unstandard_headers.update({"x-pfm": value})

    @property
    def client_route(self) -> str | None:
        """Адрес (путь) страницы с которой будет сделан запрос."""
        return self.unstandard_headers.get("x-client-route", None)
    
    @client_route.setter
    def client_route(self, value: str) -> None:
        self.unstandard_headers.update({"x-client-route": value})


    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        add_unstandard_headers: bool = True,
        credentials: bool = True,
    ) -> FetchResponse:
        """Выполнить HTTP-запрос через внутреннюю сессию.

        Единая точка входа для всех HTTP-запросов библиотеки.
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp: FetchResponse = await self.page.fetch(
            url=url,
            method=method,
            body=json_body,
            mode="cors",
            credentials="include" if credentials else "omit",
            timeout_ms=self.timeout_ms,
            referrer=self.MAIN_SITE_URL,
            headers={"Accept": "application/json, text/plain, */*"} | (self.unstandard_headers if add_unstandard_headers else {}),
        )

        return resp
