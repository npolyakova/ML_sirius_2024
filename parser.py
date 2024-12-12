import requests
import pandas as pd
import csv

def get_catalogs_wb() -> dict:
    "Отправляем гет запрос и получаем полный каталог Wildberries"
    url = 'https://static-basket-01.wbbasket.ru/vol0/data/main-menu-ru-ru-v3.json'
    headers = {'Accept': '*/*', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    return requests.get(url, headers=headers).json()

def get_data_category(catalogs_wb: dict) -> list:
    "Собираем только подкатегории из категорий первого уровня"
    catalog_data = []
    for category in catalogs_wb:
      if 'childs' in category:
         for child in category['childs']:
          catalog_data.append({
            'name': f"{child['name']}",
            'shard': child.get('shard', None),
            'url': child['url'],
            'query': child.get('query', None)
          })
    return catalog_data

def save_csv(data: list, file_name: str):
    f = open(file_name, 'w', encoding="utf-8")

    writer = csv.writer(f)
    writer.writerow(data)
    f.close()

def search_category_in_catalog(url: str, catalog_list: list) -> dict:
    """проверка пользовательской ссылки на наличии в каталоге"""
    for catalog in catalog_list:
        if catalog['url'] == url.split('https://www.wildberries.ru')[-1]:
            print(f'найдено совпадение: {catalog["name"]}')
            return catalog


def get_data_from_json(json_file: dict, category: str) -> list:
    """извлекаем из json данные"""
    data_list = []
    for data in json_file['data']['products.csv']:
        sku = data.get('id')
        name = data.get('name')
        price = int(data.get("priceU") / 100)
        brand = data.get('brand')
        rating = data.get('rating')
        category = category
        data_list.append({
            'id': sku,
            'name': name,
            'price': price,
            'brand': brand,
            'rating': rating,
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP',
            'category': category['name']
        })
    return data_list

def scrap_page(page: int, shard: str, query: str) -> dict:
    """Сбор данных со страниц"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0)"}
    url = f'https://catalog.wb.ru/catalog/{shard}/catalog?appType=1&curr=rub' \
          f'&dest=-1257786' \
          f'&locale=ru' \
          f'&page={page}' \
          f'&sort=popular&spp=0' \
          f'&{query}'
    r = requests.get(url, headers=headers)
    print(f'Статус: {r.status_code} Страница {page} Идет сбор...')
    if r.status_code == 200:
        return r.json()
    else:
        return {}

def parser():
    # Сохраняем категории в эксель
    catalog_data = get_data_category(get_catalogs_wb())
    try:
        save_csv(catalog_data, "categories.csv")
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')

    # Сохраняем товары в эксель
    # поиск введенной категории в общем каталоге
    data_list = []

    try:
        for category in catalog_data:
            data = scrap_page(
                page=1,
                shard=category['shard'],
                query=category['query']
            )
            if data != {}:
                products_list = get_data_from_json(data, category)
                for i in range (0, 10):
                    data_list.append(products_list[i])

            print(category['name'])

        print(f'Сбор данных завершен. Собрано: {len(data_list)} товаров.')
    # сохранение найденных данных
        save_csv(data_list, "products.csv.csv")
    except PermissionError:
        print('Ошибка! Повторите попытку')


if __name__ == '__main__':
    parser()