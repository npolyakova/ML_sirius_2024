import requests
import pandas as pd
from matplotlib.pyplot import pause
from retry import retry

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

def save_excel(data: list, filename: str):
  "сохранение результата в excel файл"
  df = pd.DataFrame(data)    # Указываем правильное имя движка: 'xlsxwriter'
  writer = pd.ExcelWriter(f'{filename}.xlsx', engine='xlsxwriter')
  df.to_excel(writer, sheet_name='data', index=False)

# Настраиваем ширину столбцов
  worksheet = writer.sheets['data']
  worksheet.set_column(0, 1, 10)
  worksheet.set_column(1, 2, 34)
  worksheet.set_column(2, 3, 8)
  worksheet.set_column(3, 4, 9)
  worksheet.set_column(4, 5, 8)
  worksheet.set_column(5, 6, 4)
  worksheet.set_column(6, 7, 20)
  worksheet.set_column(7, 8, 6)
  worksheet.set_column(8, 9, 23)
  worksheet.set_column(9, 10, 13)
  worksheet.set_column(10, 11, 11)
  worksheet.set_column(11, 12, 12)
  worksheet.set_column(12, 13, 15)
  worksheet.set_column(13, 14, 15)
  worksheet.set_column(14, 15, 67)

  writer.close()
  print(f'Все сохранено в {filename}.xlsx\n')

def search_category_in_catalog(url: str, catalog_list: list) -> dict:
    """проверка пользовательской ссылки на наличии в каталоге"""
    for catalog in catalog_list:
        if catalog['url'] == url.split('https://www.wildberries.ru')[-1]:
            print(f'найдено совпадение: {catalog["name"]}')
            return catalog


def get_data_from_json(json_file: dict) -> list:
    """извлекаем из json данные"""
    data_list = []
    for data in json_file['data']['products']:
        sku = data.get('id')
        name = data.get('name')
        price = int(data.get("priceU") / 100)
        salePriceU = int(data.get('salePriceU') / 100)
        cashback = data.get('feedbackPoints')
        sale = data.get('sale')
        brand = data.get('brand')
        rating = data.get('rating')
        supplier = data.get('supplier')
        supplierRating = data.get('supplierRating')
        feedbacks = data.get('feedbacks')
        reviewRating = data.get('reviewRating')
        promoTextCard = data.get('promoTextCard')
        promoTextCat = data.get('promoTextCat')
        data_list.append({
            'id': sku,
            'name': name,
            'price': price,
            'salePriceU': salePriceU,
            'cashback': cashback,
            'sale': sale,
            'brand': brand,
            'rating': rating,
            'supplier': supplier,
            'supplierRating': supplierRating,
            'feedbacks': feedbacks,
            'reviewRating': reviewRating,
            'promoTextCard': promoTextCard,
            'promoTextCat': promoTextCat,
            'link': f'https://www.wildberries.ru/catalog/{data.get("id")}/detail.aspx?targetUrl=BP'
        })
    return data_list

#@retry(Exception, tries=-1, delay=0)
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
    # try:
    #     save_excel(catalog_data, "categories")
    # except PermissionError:
    #     print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')

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
                products_list = get_data_from_json(data)
                for i in range (0, 10):
                    data_list.append(products_list[i])

            print(category['name'])
            #pause(1)
        print(f'Сбор данных завершен. Собрано: {len(data_list)} товаров.')
    # сохранение найденных данных
        save_excel(data_list, "products")
    except PermissionError:
        print('Ошибка! Вы забыли закрыть созданный ранее excel файл. Закройте и повторите попытку')


if __name__ == '__main__':
    parser()