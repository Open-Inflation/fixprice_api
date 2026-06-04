class CatalogSort:
    """Опции сортировки для каталога товаров."""

    POPULARITY = "sold"
    """Сортировка по популярности"""

    ALPHABET = "abc"
    """Сортировка по алфавиту"""

    class Price:
        """Сортировка по цене."""

        ASC = "min"
        DESC = "max"
