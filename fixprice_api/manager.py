import hrequests
from typing import Any
import os
from dataclasses import dataclass, field
import json
from requests import Request
import urllib

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

    timeout: float          = 15.0
    browser: str            = "firefox"
    headless: bool          = True
    proxy: str | None       = field(default_factory=_pick_https_proxy)
    browser_opts: dict[str, Any] = field(default_factory=dict)

    MAIN_SITE_URL: str    = "https://fix-price.com/"
    CATALOG_URL: str = "https://api.fix-price.com/buyer"

    # будет создана в __post_init__
    session: hrequests.Session = field(init=False, repr=False)

    # ───── lifecycle ─────
    def __post_init__(self) -> None:
        self.session: hrequests.Session = hrequests.Session(
            self.browser,
            timeout=self.timeout,
        )

        self.Geolocation: ClassGeolocation = ClassGeolocation(self, self.CATALOG_URL)
        """Клиент геолокации."""
        self.Catalog:     ClassCatalog     = ClassCatalog(self, self.CATALOG_URL)
        """Методы каталога."""
        self.Advertising: ClassAdvertising = ClassAdvertising(self, self.CATALOG_URL)
        """Методы рекламы."""
        self.General:     ClassGeneral     = ClassGeneral(self, self.CATALOG_URL)
        """Общие методы (например, для формы обратной связи)."""

    def __enter__(self):
        return self

    async def __exit__(self, *exc):
        pass
    

    @property
    def city_id(self) -> str | None:
        """ID города используемый как фильтр каталога. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `3` (Москва)."""
        return self.session.headers.get("x-city", None)

    @city_id.setter
    def city_id(self, value: str | None) -> None:
        if value is None:
            self.session.headers.pop("x-city", None)
        elif (
            not isinstance(value, int) and \
            not isinstance(value, float) \
            and(not isinstance(value, str) and value.isdigit())
        ):
            raise TypeError("`city_id` must be int")
        elif int(value) < 1:
            raise ValueError("`city_id` must be greater than 0")
        else:
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "x-city": value
            })
    
    @property
    def language(self) -> str | None:
        """Язык используемый как фильтр каталога. ISO-2. Если не указан, автоматически назначается в первом ответе сервера. Обычно это `ru` (Русский)."""
        return self.session.headers.get("x-language", None)

    @language.setter
    def language(self, value: str | None) -> None:
        if not isinstance(value, str):
            raise TypeError("`language` must be str")
        if not len(value) in [2, 5]:
            raise ValueError("`language` must be IETF BCP 47. Length must be 2 (ex. `en`) or 5 (ex. `en-AE`)")
        elif value is None:
            self.session.headers.pop("x-language", None)
        else:
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "x-language": value
            })

    # Прогрев сессии (headless ➜ cookie `session` ➜ accessToken)
    def _warmup(self) -> None:
        """Прогрев сессии через браузер для получения токена доступа.
        
        Открывает главную страницу сайта в headless браузере, получает cookie сессии
        и извлекает из неё access token для последующих API запросов.
        """
        with hrequests.BrowserSession(
            session=self.session,
            browser=self.browser,
            headless=self.headless,
            proxy=self.proxy,
            **self.browser_opts,
        ) as page:
            page.goto(MAIN_SITE_URL)
            page.awaitSelector("html[data-lt-installed='true']", timeout=self.timeout)

    def _request(
        self,
        method: str,
        url: str,
        *,
        json_body: Any | None = None,
    ) -> hrequests.Response:
        """Выполнить HTTP-запрос через внутреннюю сессию.
        
        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            json_body: Тело запроса в формате JSON (опционально)
        """
        # Единая точка входа в чужую библиотеку для удобства
        resp: hrequests.Response = self.session.request(method.upper(), url, json=json_body, timeout=self.timeout, proxy=self.proxy)
        if hasattr(resp, "request"):
            raise RuntimeError(
                "Response object does have `request` attribute. "
                "This may indicate an update in `hrequests` library."
            )
        
        if self.city_id == None and resp data["city"]: self.city_id = data["city"]
        if self.language == None and data["language"]: self.language = data["language"]

        resp.request = Request(
            method=method.upper(),
            url=url,
            json=json_body,
        )
        return resp
