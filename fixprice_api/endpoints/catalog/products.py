from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, overload
from urllib.parse import urlencode

from human_requests import autotest
from human_requests.abstraction import HttpMethod, MethodPipelineError

from ... import abstraction

if TYPE_CHECKING:
    from ...manager import FixPriceAPI


class ClassProducts:
    """Функции для получения информации о товарах, их наличии и балансе."""

    def __init__(self, parent: FixPriceAPI):
        self._parent = parent

    @autotest
    async def balance(self, product_id: int, in_stock: bool = True, search: str | None = None) -> abstraction.Output:
        """Checks store balance for a product in the current city."""
        if product_id is None:
            raise ValueError("`product_id` is required")
        if not isinstance(product_id, int) or isinstance(product_id, bool):
            raise TypeError("`product_id` must be int")
        if float(product_id) < 1 or float(product_id) > 2147483647:
            raise ValueError("`product_id` must be between 1 and 2147483647")
        if in_stock is not None and not isinstance(in_stock, bool):
            raise TypeError("`in_stock` must be bool")
        if search is not None and not isinstance(search, str):
            raise TypeError("`search` must be str")

        if product_id is not None:
            request_url = str(self._parent._CATALOG_URL) + "/v1/store/balance/" + str(product_id)
        else:
            raise TypeError("balance() call is ambiguous; URL cannot be collected")
        query_params: list[tuple[str, object]] = []
        query_params.append(("canPickup", "all"))
        if search is not None:
            query_params.append(("addressPart", search))
        query_params.append(("inStock", "true"))
        if query_params:
            request_url += "?" + urlencode(query_params, doseq=True)

        json_body = None
        return await self._parent._request(
            HttpMethod.GET,
            url=request_url,
            json_body=json_body,
        )

    @overload
    async def info(self, *, url: str) -> abstraction.Output: ...

    @overload
    async def info(self, *, category: str, product_id: int, slug: str) -> abstraction.Output: ...

    @autotest
    async def info(self, *, url: str | None = None, category: str | None = None, product_id: int | None = None, slug: str | None = None) -> abstraction.Output:
        """Loads the product page, extracts window.__NUXT__, and overrides resp.json to return the product payload."""
        matched = []
        if url is not None and category is None and product_id is None and slug is None:
            matched.append("fullurl")
        if url is None and category is not None and product_id is not None and slug is not None:
            matched.append("structured")
        if not matched:
            raise TypeError("info() expected one of: fullurl, structured")
        elif len(matched) > 1:
            raise TypeError(f"info() call is ambiguous; matched overloads: {matched}")
        else:
            matched_overload = matched[0]
        if matched_overload == "fullurl":
            pass
        if matched_overload == "structured":
            pass
        if url is not None and not isinstance(url, str):
            raise TypeError("`url` must be str")
        if url is None and matched_overload == "fullurl":
            raise ValueError("`url` is required")
        if category is not None and not isinstance(category, str):
            raise TypeError("`category` must be str")
        if category is None and matched_overload == "structured":
            raise ValueError("`category` is required")
        if product_id is not None and (not isinstance(product_id, int) or isinstance(product_id, bool)):
            raise TypeError("`product_id` must be int")
        if product_id is None and matched_overload == "structured":
            raise ValueError("`product_id` is required")
        if product_id is not None and (float(product_id) < 1 or float(product_id) > 2147483647):
            raise ValueError("`product_id` must be between 1 and 2147483647")
        if slug is not None and not isinstance(slug, str):
            raise TypeError("`slug` must be str")
        if slug is None and matched_overload == "structured":
            raise ValueError("`slug` is required")

        if url is not None:
            request_url = str(self._parent._MAIN_SITE_ORIGIN) + "/catalog/" + str(url)
        elif category is not None and product_id is not None and slug is not None:
            request_url = str(self._parent._MAIN_SITE_ORIGIN) + "/catalog/" + str(category) + "/p-" + str(product_id) + "-" + str(slug)
        else:
            raise TypeError("info() call is ambiguous; URL cannot be collected")

        page = await self._parent.ctx.new_page()
        pipeline_sniffer = None
        try:
            pipeline_sniffer = await self._parent._create_pipeline_sniffer()
            resp = await page.goto(request_url, wait_until="domcontentloaded")
            if resp is None:
                raise RuntimeError("page.goto() returned None")
            json_override = None
            text_override = None
            await page.wait_for_load_state("networkidle")
            warmup = self._parent._make_warmup_context(page=page, sniffer=pipeline_sniffer)
            from ...pipelines.goto_pipeline import pipeline as goto_pipeline_runner

            try:
                await goto_pipeline_runner(warmup)
            except MethodPipelineError:
                raise
            except Exception as exc:
                raise MethodPipelineError(str(exc)) from exc
            evaluate_script = (Path(__file__).resolve().parents[2] / "extractors/catalog-product-info.js").read_text(encoding="utf-8")
            evaluate_result = await page.evaluate(evaluate_script)
            if isinstance(evaluate_result, dict):
                result_type = str(evaluate_result.get("type", "")).lower()
                if result_type in {"json", "text/json"}:
                    json_override = json.loads(evaluate_result.get("data", "null"))
                elif result_type in {"text", "text/plain"}:
                    text_override = str(evaluate_result.get("data", ""))
            return await abstraction.Output.from_playwright_response(
                resp,
                page=page,
                json_override=json_override,
                text_override=text_override,
            )
        finally:
            try:
                if pipeline_sniffer is not None:
                    await pipeline_sniffer.complete()
            finally:
                await page.close()
