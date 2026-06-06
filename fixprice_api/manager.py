from collections import defaultdict
from dataclasses import dataclass, field
from time import perf_counter, time
from typing import Any, ClassVar, Literal, cast

from aiohttp_retry import ExponentialRetry, RetryClient
from camoufox import AsyncCamoufox, DefaultAddons
from human_requests import HumanBrowser, HumanPage
from human_requests.abstraction import HttpMethod, Proxy, Warmup, WarmupError
from human_requests.network_analyzer.anomaly_sniffer import HeaderAnomalySniffer

from . import abstraction
from .endpoints.advertising import ClassAdvertising
from .endpoints.catalog import ClassCatalog
from .endpoints.general import ClassGeneral
from .endpoints.geolocation import ClassGeolocation


@dataclass
class FixPriceAPI:
    """Аснинхронный неофициальный API клиент для сайта fix-price.com"""

    timeout_ms: int = 35000
    """Global timeout, in milliseconds, used by warmup and browser-backed requests."""
    headless: bool = False
    """Whether the browser is started without a visible window."""
    test_mode: bool = False
    """Enable the test-only warmup branch and its extra state."""
    proxy: str | dict | Proxy | None = None
    """Proxy settings for browser startup and direct requests. When omitted or set to None, the client reads the proxy from the environment."""
    browser_opts: dict[str, Any] | None = None
    """Extra keyword arguments forwarded to AsyncCamoufox during browser startup."""

    _MAIN_SITE_URL: ClassVar[str] = "https://fix-price.com/catalog"
    _MAIN_SITE_ORIGIN: ClassVar[str] = "https://fix-price.com"
    _CATALOG_URL: ClassVar[str] = "https://api.fix-price.com/buyer"

    Catalog: ClassCatalog = field(init=False)
    """Группа функций для работы с каталогом товаров."""
    Geolocation: ClassGeolocation = field(init=False)
    """Группа функций для работы с геолокацией, получения информации о странах, регионах и городах."""
    Advertising: ClassAdvertising = field(init=False)
    """Группа функций для получения информации о рекламных акциях и брендах на главной странице."""
    General: ClassGeneral = field(init=False)
    """Разные функции, не вошедшие в другие группы."""

    def __post_init__(self):
        self.proxy = Proxy.from_env() if self.proxy is None else self.proxy
        browser_opts: dict[str, Any] = {} if self.browser_opts is None else dict(self.browser_opts)
        self.browser_opts = browser_opts
        self.session = None
        self.ctx = None
        self.page = None
        self.unstandard_headers = {}
        self.unstandard_urls = {}

        self._city_id = None
        self._language = None
        self._token = None
        self._delivery_type = None
        self._store_id = None
        self._client_route = None

        self.Catalog = ClassCatalog(self)
        self.Geolocation = ClassGeolocation(self)
        self.Advertising = ClassAdvertising(self)
        self.General = ClassGeneral(self)

    async def __aenter__(self):
        await self._warmup()
        return self

    async def _warmup(self) -> None:
        if self.headless:
            raise ValueError("headless=True is not allowed when @DisallowHeadless is set")
        px = self.proxy if isinstance(self.proxy, Proxy) else Proxy(self.proxy)
        browser_opts: dict[str, Any] = {} if self.browser_opts is None else dict(self.browser_opts)
        br = await AsyncCamoufox(
            headless=self.headless,
            proxy=px.as_dict(),
            humanize=True,
            **browser_opts,
            block_images=True,
            i_know_what_im_doing=True,
            exclude_addons=[DefaultAddons.UBO],
        ).start()

        self.session = HumanBrowser.replace(cast(Any, br))
        self.ctx = await self.session.new_context()
        self.page = await self.ctx.new_page()
        self.page.on_error_screenshot_path = "screenshot.png"

        sniffer = HeaderAnomalySniffer(
            include_subresources=True,
        )
        await sniffer.start(self.ctx)

        warmup = self._make_warmup_context(page=self.page, sniffer=sniffer)
        from .pipelines.warmup import pipeline as warmup_runner

        try:
            await warmup_runner(warmup)
        except WarmupError:
            raise
        except Exception as exc:
            raise WarmupError(str(exc)) from exc

        result_sniffer: dict[str, Any] = await sniffer.complete() if sniffer else {"request": {}}

        result = defaultdict(set)

        for _url, headers in result_sniffer.get("request", {}).items():
            for header, values in headers.items():
                result[header].update(values)

        self.unstandard_headers = {k: list(v)[0] for k, v in result.items()}
        _city_id_raw = self.unstandard_headers.get("x-city")
        if _city_id_raw is None:
            self._city_id = None
        else:
            _city_id_value = int(_city_id_raw)
            if float(_city_id_value) < 1 or float(_city_id_value) > 2147483647:
                raise ValueError("`city_id` must be between 1 and 2147483647")
            self._city_id = _city_id_value

        _language_raw = self.unstandard_headers.get("x-language")
        if _language_raw is None:
            self.language = None
        else:
            _language_value = _language_raw if isinstance(_language_raw, str) else str(_language_raw)
            self.language = cast(str | None, _language_value)

        _token_raw = self.unstandard_headers.get("x-key")
        if _token_raw is None:
            self._token = None
        else:
            _token_value = _token_raw if isinstance(_token_raw, str) else str(_token_raw)
            self._token = _token_value

        _delivery_type_raw = self.unstandard_headers.get("x-delivery-type")
        if _delivery_type_raw is None:
            self.delivery_type = None
        else:
            _delivery_type_value = _delivery_type_raw if isinstance(_delivery_type_raw, str) else str(_delivery_type_raw)
            self.delivery_type = cast(Literal["store", "pickup", "courier"] | None, _delivery_type_value)

        _store_id_raw = self.unstandard_headers.get("x-pfm")
        if _store_id_raw is None:
            self.store_id = None
        else:
            _store_id_value = _store_id_raw if isinstance(_store_id_raw, str) else str(_store_id_raw)
            self.store_id = cast(str | None, _store_id_value)

        _client_route_raw = self.unstandard_headers.get("x-client-route")
        if _client_route_raw is None:
            self.client_route = None
        else:
            _client_route_value = _client_route_raw if isinstance(_client_route_raw, str) else str(_client_route_raw)
            self.client_route = cast(str | None, _client_route_value)

        self.unstandard_urls = result_sniffer.get("request", {})

    async def __aexit__(self, *exc):
        await self.close()

    async def close(self):
        await self.session.close()

    def _make_warmup_context(
        self,
        *,
        page: HumanPage,
        sniffer: HeaderAnomalySniffer | None,
    ) -> Warmup:
        return Warmup(
            browser=self.session,
            context=self.ctx,
            page=page,
            sniffer=sniffer,
            timeout_ms=self.timeout_ms,
            test_mode=self.test_mode,
            prefixes={
                "MAIN_SITE_URL": self._MAIN_SITE_URL,
                "MAIN_SITE_ORIGIN": self._MAIN_SITE_ORIGIN,
                "CATALOG_URL": self._CATALOG_URL,
            },
        )

    async def _create_pipeline_sniffer(self) -> HeaderAnomalySniffer:
        sniffer = HeaderAnomalySniffer(
            include_subresources=True,
        )
        await sniffer.start(self.ctx)
        return sniffer

    @property
    def city_id(self) -> int | None:
        """Current city id used by catalog and balance requests."""
        return self._city_id

    @property
    def language(self) -> str | None:
        return self._language

    @language.setter
    def language(self, value: str | None) -> None:
        if value is None:
            self._language = None
            return

        if not isinstance(value, str):
            raise TypeError("`language` must be str")
        if not (abstraction.RegexLanguageTag.match(value)):
            raise ValueError(abstraction.RegexLanguageTag.ERROR)
        self._language = value

    @property
    def token(self) -> str | None:
        """Access token captured by the warmup sniffer."""
        return self._token

    @property
    def delivery_type(self) -> Literal["store", "pickup", "courier"] | None:
        return self._delivery_type

    @delivery_type.setter
    def delivery_type(self, value: Literal["store", "pickup", "courier"] | None) -> None:
        if value is None:
            self._delivery_type = None
            return

        if not isinstance(value, str):
            raise TypeError("`delivery_type` must be str")
        allowed_values = ["store", "pickup", "courier"]
        if value not in allowed_values:
            raise ValueError(f"`delivery_type` must be one of {allowed_values}")
        self._delivery_type = value

    @property
    def store_id(self) -> str | None:
        return self._store_id

    @store_id.setter
    def store_id(self, value: str | None) -> None:
        if value is None:
            self._store_id = None
            return

        if not isinstance(value, str):
            raise TypeError("`store_id` must be str")
        if not (abstraction.RegexStoreId.match(value)):
            raise ValueError(abstraction.RegexStoreId.ERROR)
        self._store_id = value

    @property
    def client_route(self) -> str | None:
        return self._client_route

    @client_route.setter
    def client_route(self, value: str | None) -> None:
        if value is None:
            self._client_route = None
            return

        if not isinstance(value, str):
            raise TypeError("`client_route` must be str")
        self._client_route = value

    async def _request(
        self,
        method: HttpMethod,
        url: str,
        *,
        json_body: Any | None = None,
        mode: str | None = None,
        credentials: str | None = None,
        referrer: str | None = None,
        headers: dict[str, Any] | None = None,
    ) -> abstraction.Output:
        request_headers = headers if headers is not None else {"Accept": "application/json, text/plain, */*", "x-city": str(self.city_id), "X-Key": str(self.token), "x-language": str(self.language)}
        fetch_kwargs: dict[str, Any] = {
            "url": url,
            "method": method,
            "body": json_body,
            "mode": mode if mode is not None else "cors",
            "credentials": credentials if credentials is not None else "same-origin",
            "timeout_ms": self.timeout_ms,
            "headers": request_headers,
        }
        if referrer is not None:
            fetch_kwargs["referrer"] = referrer
        response = await self.page.fetch(**fetch_kwargs)
        return abstraction.Output.from_fetch_response(response)

    async def _direct_request(
        self,
        url: str,
        *,
        retry_attempts: int = 3,
        timeout: float = 10,
    ) -> abstraction.Output:
        start_t = perf_counter()
        retry_options = ExponentialRetry(attempts=retry_attempts, start_timeout=3.0, max_timeout=timeout)
        px = self.proxy if isinstance(self.proxy, Proxy) else Proxy(self.proxy)
        async with (
            RetryClient(retry_options=retry_options) as retry_client,
            retry_client.get(url, raise_for_status=True, proxy=px.as_str()) as resp,
        ):
            body = await resp.read()
            return abstraction.Output.from_raw(
                body,
                url=str(resp.url),
                headers=dict(resp.headers),
                status_code=resp.status,
                status_text=resp.reason,
                redirected=bool(resp.history),
                response_type="basic",
                duration=perf_counter() - start_t,
                end_time=time(),
                page=self.page,
            )
