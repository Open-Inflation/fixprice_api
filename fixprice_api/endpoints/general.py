from __future__ import annotations

from typing import TYPE_CHECKING

from .. import abstraction

if TYPE_CHECKING:
    from ..manager import FixPriceAPI


class ClassGeneral:
    """Разные функции, не вошедшие в другие группы."""

    def __init__(self, parent: FixPriceAPI):
        self._parent = parent

    async def download_image(self, url: str) -> abstraction.Output:
        """Direct image download helper; bypasses the browser request pipeline and returns Output with .image()."""
        if url is None:
            raise ValueError("`url` is required")
        if not isinstance(url, str):
            raise TypeError("`url` must be str")

        if url is not None:
            request_url = url
        else:
            raise TypeError("download_image() call is ambiguous; URL cannot be collected")

        return await self._parent._direct_request(request_url)
