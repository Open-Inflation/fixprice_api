import hrequests
from typing import Any
import os
from dataclasses import dataclass, field
import json
from requests import Request
import time

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

    MAIN_SITE_URL: str    = "https://fix-price.com/catalog"
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
        self._warmup()
        return self

    def __exit__(self, *exc):
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
        self.session.headers.update({ # токен пойдёт в каждый запрос
            "X-Client-Route": "/catalog"
        })

        with hrequests.BrowserSession(
            session=self.session,
            browser=self.browser,
            headless=self.headless,
            proxy=self.proxy,
            **self.browser_opts,
        ) as page:
            page.goto(self.MAIN_SITE_URL)
            page.awaitSelector('div#__nuxt', timeout=self.timeout)

    def _request(
        self,
        method: str,
        url: str,
        real_route: str | None = None,
        *,
        json_body: Any | None = None,
        retry: int = 3,
    ) -> hrequests.Response:
        """Выполнить HTTP-запрос с возможностью повторов.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            real_route: "реальный" маршрут. Отражает путь на морде сайта.
            json_body: Тело запроса в формате JSON (опционально)
            retry: Количество попыток при ошибке сети или таймауте (по умолчанию 3)
        """
        def check_is_error(data) -> bool:
            errors_keys = ["name", "message", "code", "type", "status", "comment"]
            return len(data) != len(errors_keys) or not all(key in data for key in errors_keys)

        for attempt in range(retry):
            resp = self._fetch(
                method=method,
                url=url,
                real_route=real_route,
                json_body=json_body,
            )
            if check_is_error(resp.json()):
                return resp
            else:
                time.sleep(5)
        else:
            raise RuntimeError(f"Failed to complete request after {retry} attempts")
        
    def _fetch(
        self,
        method: str,
        url: str,
        real_route: str | None = None,
        *,
        json_body: Any | None = None,
    ) -> hrequests.Response:
        """Выполнить HTTP-запрос через внутреннюю сессию.
        
        Единая точка входа для всех HTTP-запросов библиотеки.
        Добавляет к ответу объект Request для совместимости.
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE и т.д.)
            url: URL для запроса
            real_route: "реальный" маршрут. Отражает путь на морде сайта.
            json_body: Тело запроса в формате JSON (опционально)
        """

        if real_route:
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "X-Client-Route": real_route
            })

        # Единая точка входа в чужую библиотеку для удобства
        resp = self.session.request(method.upper(), url, json=json_body, timeout=self.timeout, proxy=self.proxy)
        if hasattr(resp, "request"):
            raise RuntimeError(
                "Response object does have `request` attribute. "
                "This may indicate an update in `hrequests` library."
            )
        elif isinstance(resp, hrequests.ProcessResponse):
            raise RuntimeError(
                "Response object is still a `ProcessResponse`. "
                "This may indicate that the request was not completed. "
                "Check if the proxy or network settings are correct."
            )
        

        ctype = resp.headers.get("content-type", "")
        if "text/html" in ctype:
            # исполним скрипт в браузерном контексте; куки запишутся в сессию
            with resp.render(headless=self.headless, browser=self.browser) as rend:
                rend.awaitSelector(selector="pre", timeout=self.timeout)

                jsn = json.loads(rend.find("pre").text)

                fin_resp = hrequests.Response(
                    url=resp.url,
                    status_code=resp.status_code,
                    headers=resp.headers,
                    cookies=hrequests.cookies.cookiejar_from_dict(
                        self.session.cookies.get_dict()
                    ),
                    raw=json.dumps(jsn, ensure_ascii=True).encode("utf-8"),
                )
        else:
            fin_resp = resp

        if self.city_id == None and fin_resp.headers.get("x-city"): self.city_id = fin_resp.headers["x-city"]
        if self.language == None and fin_resp.headers.get("x-language"): self.language = fin_resp.headers["x-language"]
        tok = self.session.cookies.get(name="token", domain="fix-price.com")
        if tok:
            print("Token acquired:", tok)
            self.session.headers.update({ # токен пойдёт в каждый запрос
                "X-Key": tok
            })

        fin_resp.request = Request(
            method=method.upper(),
            url=url,
            json=json_body,
        )
        return fin_resp
