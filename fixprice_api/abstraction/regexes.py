import re
from typing import Any


class RegexBase:
    REGEX = r""
    ERROR: str | None = None

    @classmethod
    def match(cls, value: Any) -> bool:
        return re.fullmatch(cls.REGEX, str(value)) is not None


class RegexCountryAlias(RegexBase):
    REGEX = r"^[A-Za-z]{2}$"
    ERROR = "Alias страны должен состоять ровно из двух латинских букв"


class RegexLanguageTag(RegexBase):
    """Языковой тег в формате xx или xx-YY, где xx - код языка из двух строчных букв, а YY - код страны из двух заглавных букв."""

    REGEX = r"^[a-z]{2}(?:-[A-Z]{2})?$"


class RegexStoreId(RegexBase):
    REGEX = r"^[A-Za-z]\\d{3}$"
