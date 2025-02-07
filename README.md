# FixPrice API (not official / не официальный)

FixPrice - https://fix-price.com/

# Usage / Использование

> `product_info` не реализован т.к. информация вшита в страницу.


### Базовая структура
```py
import asyncio
from fixprice_api import FixPrice, CatalogSort

async def main():
    ...

if __name__ == "__main__":
    asyncio.run(main())
```

### Взаимодействие с каталогом

```py
async with FixPrice() as Api:
    # Получение списка категорий
    categories = await Api.Catalog.categories_list()
    products = []
    tq = tqdm(categories, desc='Обработано категорий')

    async def process_sub(category_alias, subcategory_alias=None, depth=0):
        page = 1 # Счет от единицы, а не нуля!
        limit = 27 # Максимальное значение

        while page > 0:
            # count - общее количество айтемов на всех страницах (в данном случае не используем)
            count, catalog = await Api.Catalog.products_list(
                category_alias=category_alias,
                subcategory_alias=subcategory_alias,
                page=page,
                limit=limit,
                sort=CatalogSort.POPULARITY
            )
            if not catalog:
                break
            
            for product in catalog:
                products.append(f'{product["title"]} ({product["id"]})')
                tq.set_description(f'Обработано карточек: {len(products)}')
            
            if len(catalog) <= 0:
                break
            
            time.sleep(0.4) # Специально замедляем обработку, чтобы не получить код 429, советую эксперементировать
            page += 1
        
    # Обход всех категорий и подкатегорий
    for category in tq:
        subcategories = category.get("items", [])
        # Можно и не обрабатывать подкатегории отдельно, зависит от желания и ТЗ
        if subcategories:
            for subcategory in subcategories:
                await process_sub(category["alias"], subcategory["alias"])
        else:
            await process_sub(category["alias"])

    tq.close()

    # Вывод статистики
    print(f'Общее количество встреченных карточек: {len(products)}')
    print(f'Уникальных товаров: {len(set(products))}')
    print(f'Среднее количество повторений карточки: {round(len(products) / len(set(products)), 2)}')
```
```bash
> Обработано карточек: 6019: 100%|███████████████| 29/29 [04:29<00:00,  9.29s/it]
> Общее количество встреченных карточек: 6019
> Уникальных товаров: 4900
> Среднее количество повторений карточки: 1.23
```

### Работа с геолокацией в сессии:
*От геолокации зависит выдача каталога!*
```py
async with FixPrice() as Api:
    print(f"ID города перед первым запросом: {Api.city_id}, язык: {Api.language}") # По умолчанию не назначено
    await Api.Catalog.home_brands_list() # Можем обработать любую функцию
    print(f"ID города после первого запроса: {Api.city_id}, язык: {Api.language}") # Сервер прислал стандартные значения

    country = await Api.Geolocation.country_list(alias="RU") # alias работает сортировкой

    # получаем объект "Объединенные Арабские Эмираты"
    print(f"Найдена страна {country[0]['title']} ({country[0]['id']}), валюта: {country[0]['currency']['title']} / {country[0]['currency']['symbol']}")

    citys = await Api.Geolocation.city_list(country_id=country[0]["id"]) # получаем список городов

    Api.city_id = citys[0]["id"] # меняем ID города
    print(f"Город изменен на {citys[0]['name']} ({citys[0]['id']})")

    # Вне РФ каталог не работает
    print(f"Категории: {len(await Api.Catalog.categories_list())} штук")
```
```bash
> ID города перед первым запросом: None, язык: None
> ID города после первого запроса: 3, язык: ru
> Найдена страна Россия (2), валюта: Рубль / ₽
> Город изменен на Щербинка (229)
> Категории: 29 штук
```

### Проверка наличия товара
```py
async with FixPrice() as Api:
    Api.city_id = 3 # Обязательно указываем перед запросом город, иначе ошибка
    check = await Api.Store.product_balance(1851089) # Круассан, 7DAYS, 110 г, с двойным кремом

    stoks = []
    for i in check:
        stoks.append(i.get("count", 0))

    print(f"Самое большое количество: {max(stoks)}")
    print(f"Самое малое количество: {min(stoks)}")
    print(f"Среднее количество: {round(sum(stoks) / len(stoks), 2)}")
    print(f"Обработано {len(stoks)} магазинов")
```
```bash
> Самое большое количество: 67
> Самое малое количество: 10
> Среднее количество: 28.5
> Обработано 339 магазинов
```

### Загрузка изображений
```py
async with FixPrice() as Api:
    img = await Api.General.download_image("https://img.fix-price.com/190x190/_marketplace/images/origin/90/903ce795a221a6978444a86391816f93.jpg")

    with open(img.name, "wb") as f:
        f.write(img.read())
```

### Или параллельная загрузка
```py
async with FixPrice() as Api:
    tasks = [
        Api.General.download_image("https://img.fix-price.com/190x190/_marketplace/images/origin/90/903ce795a221a6978444a86391816f93.jpg"),
        Api.General.download_image("https://img.fix-price.com/190x190/_marketplace/images/origin/51/519a1d3c838e3e7e30493fb9b1f69a05.jpg")
    ]

    results = await asyncio.gather(*tasks)
    for result in results:
        with open(result.name, "wb") as f:
            f.write(result.read())
```

---

### Report / Обратная связь

If you have any problems using it / suggestions, do not hesitate to write to the [project's GitHub](https://github.com/Open-Inflation/fixprice_api/issues)!

Если у вас возникнут проблемы в использовании / пожелания, не стесняйтесь писать на [GitHub проекта](https://github.com/Open-Inflation/fixprice_api/issues)!
