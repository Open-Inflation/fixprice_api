
class CatalogSort:
    POPULARITY = "sold"
    """Сначало самые популярные"""

    ALPHABET = "abc"

    class Price:
        """Сортировка по цене (выбрать вариант)"""

        ASC = "min"
        """Сначало самые дешевые"""

        DESC = "max"
        """Сначало самые дорогие"""
