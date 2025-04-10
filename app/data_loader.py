import chardet
import csv
import os
from io import StringIO
from werkzeug.utils import secure_filename

# Настройки по умолчанию
DEFAULT_UPLOAD_FOLDER = 'uploads'
COLUMN_NAMES = {
    # Для названия товара/продукта
    **{k: 'name' for k in [
        # Русские варианты
        'имя', 'название', 'наименование', 'товар', 'продукт', 'изделие',
        'товарный знак', 'товарный_знак', 'бренд', 'марка', 'модель', 'артикул', 'код товара', 'код_товара',
        'название товара', 'название_товара', 'наименование позиции', 'наименование_позиции',
        'описание', 'продукция', 'категория', 'тип', 'группа', 'линейка', 'серия',

        # Английские варианты
        'name', 'product', 'item', 'goods', 'article', 'sku', 'model',
        'brand', 'title', 'description',
        'product name', 'product_name', 'productname',
        'item name', 'item_name', 'itemname',
        'product title', 'product_title', 'producttitle',
        'product description', 'product_description', 'productdescription',
        'product code', 'product_code', 'productcode',
        'stock code', 'stock_code', 'stockcode',
        'item code', 'item_code', 'itemcode',
        'product group', 'product_group', 'productgroup',
        'category', 'type', 'series', 'line'
    ]},

    # Для цены
    **{k: 'price' for k in [
        # Русские варианты
        'цена', 'стоимость', 'сумма', 'ценник',
        'цена продажи', 'цена_продажи',
        'цена покупки', 'цена_покупки',
        'выручка', 'розничная цена', 'розничная_цена',
        'оптовая цена', 'оптовая_цена',
        'себестоимость', 'цена за единицу', 'цена_за_единицу',
        'цена товара', 'цена_товара',
        'цена позиции', 'цена_позиции',
        'цена без скидки', 'цена_без_скидки',
        'финальная цена', 'финальная_цена',
        'рекомендованная цена', 'рекомендованная_цена',
        'рыночная цена', 'рыночная_цена',

        # Английские варианты
        'price', 'cost', 'amount',
        'retail price', 'retail_price', 'retailprice',
        'wholesale price', 'wholesale_price', 'wholesaleprice',
        'unit price', 'unit_price', 'unitprice',
        'sale price', 'sale_price', 'saleprice',
        'purchase price', 'purchase_price', 'purchaseprice',
        'list price', 'list_price', 'listprice',
        'market price', 'market_price', 'marketprice',
        'msrp', 'recommended price', 'recommended_price', 'recommendedprice',
        'final price', 'final_price', 'finalprice',
        'item price', 'item_price', 'itemprice',
        'product price', 'product_price', 'productprice',
        'price per unit', 'price_per_unit', 'priceperunit'
    ]},

    # Для количества
    **{k: 'quantity' for k in [
        # Русские варианты
        'количество', 'кол-во', 'число', 'объем',
        'продажи', 'запас', 'остаток',
        'количество на складе', 'количество_на_складе',
        'доступное количество', 'доступное_количество',
        'количество товара', 'количество_товара',
        'количество позиций', 'количество_позиций',
        'штук', 'упаковок',

        # Английские варианты
        'quantity', 'qty', 'amount', 'number', 'count', 'stock',
        'inventory',
        'available quantity', 'available_quantity', 'availablequantity',
        'stock quantity', 'stock_quantity', 'stockquantity',
        'items in stock', 'items_in_stock', 'itemsinstock',
        'units', 'packages', 'pieces'
    ]},

    # Для даты
    **{k: 'date' for k in [
        # Русские варианты
        'дата',
        'дата продажи', 'дата_продажи',
        'дата покупки', 'дата_покупки',
        'дата создания', 'дата_создания',
        'дата обновления', 'дата_обновления',
        'дата транзакции', 'дата_транзакции',
        'дата заказа', 'дата_заказа',
        'дата поставки', 'дата_поставки',
        'дата выполнения', 'дата_выполнения',
        'время', 'период', 'год', 'месяц', 'день', 'срок',

        # Английские варианты
        'date',
        'sale date', 'sale_date', 'saledate',
        'purchase date', 'purchase_date', 'purchasedate',
        'creation date', 'creation_date', 'creationdate',
        'update date', 'update_date', 'updatedate',
        'transaction date', 'transaction_date', 'transactiondate',
        'order date', 'order_date', 'orderdate',
        'delivery date', 'delivery_date', 'deliverydate',
        'fulfillment date', 'fulfillment_date', 'fulfillmentdate',
        'time', 'period', 'year', 'month', 'day',
        'datetime', 'timestamp', 'invoice_date', 'invoicedate'
    ]},

    # Для региона/локации
    **{k: 'region' for k in [
        # Русские варианты
        'регион', 'область', 'город', 'страна', 'территория',
        'зона', 'район', 'округ',
        'местоположение', 'локация', 'место',
        'адрес', 'филиал', 'магазин',
        'точка продаж', 'точка_продаж',
        'склад', 'центр', 'подразделение',

        # Английские варианты
        'region', 'area', 'city', 'country', 'territory',
        'zone', 'district',
        'location', 'place', 'address',
        'branch', 'store', 'shop', 'outlet',
        'warehouse', 'center', 'division', 'department',
        'shopping mall', 'shopping_mall', 'shoppingmall'
    ]},

    # Дополнительные часто используемые поля
    **{k: 'discount' for k in [
        'скидка',
        'процент скидки', 'процент_скидки',
        'размер скидки', 'размер_скидки',
        'discount',
        'discount percent', 'discount_percent', 'discountpercent',
        'discount amount', 'discount_amount', 'discountamount'
    ]},

    **{k: 'currency' for k in [
        'валюта',
        'код валюты', 'код_валюты',
        'currency',
        'currency code', 'currency_code', 'currencycode'
    ]},

    **{k: 'id' for k in [
        'ид', 'код',
        'уникальный код', 'уникальный_код',
        'идентификатор',
        'id', 'code',
        'unique code', 'unique_code', 'uniquecode',
        'identifier'
    ]}
}

REQUIRED_COLUMNS = ['name', 'price', 'quantity', 'date', 'region']


def init_upload_folder(upload_folder=DEFAULT_UPLOAD_FOLDER):
    """Создаем папку для загрузок, если её нет"""
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def validate_file(file):
    """Проверяем файл перед обработкой"""
    if not file:
        return False, 'Файл не найден'
    if file.filename == '':
        return False, 'Не выбран файл'
    if not file.filename.endswith('.csv'):
        return False, 'Разрешены только CSV-файлы'
    return True, ''


def standardize_columns(csv_data):
    """Приводим названия колонок к стандартному виду"""
    standardized_data = []
    for row in csv_data:
        new_row = {}
        for original_key in row:
            lower_key = original_key.lower().strip()
            if lower_key in COLUMN_NAMES:
                new_row[COLUMN_NAMES[lower_key]] = row[original_key].strip()
        standardized_data.append(new_row)
    return standardized_data


def check_required_columns(data):
    """Проверяем наличие обязательных колонок"""
    if not data:
        return False, 'Файл пуст после стандартизации'

    missing = [col for col in REQUIRED_COLUMNS if col not in data[0]]
    if missing:
        return False, f'Не хватает обязательных колонок: {", ".join(missing)}'
    return True, ''


def check_empty_values(data):
    """Проверяем на пустые значения в обязательных колонках"""
    for i, row in enumerate(data, start=1):
        for col in REQUIRED_COLUMNS:
            if not row.get(col):
                return False, f'Пустое значение в колонке "{col}", строка {i}'
    return True, ''


def save_standardized_file(data, original_filename, upload_folder):
    """Сохраняем стандартизированный файл"""
    output_filename = f"standardized_{original_filename}"
    output_path = os.path.join(upload_folder, output_filename)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(data)

    return output_filename


def process_csv(file, upload_folder=DEFAULT_UPLOAD_FOLDER):
    """Основная функция обработки CSV файла"""
    # Проверка файла
    is_valid, error = validate_file(file)
    if not is_valid:
        return {'status': 'error', 'message': error}

    try:
        # Чтение файла
        raw_data = file.stream.read()
        encoding = chardet.detect(raw_data)['encoding']
        file_content = raw_data.decode(encoding, errors='replace')
        csv_data = list(csv.DictReader(StringIO(file_content)))

        if not csv_data:
            return {'status': 'error', 'message': 'Файл пуст или не содержит данных'}

        # Стандартизация
        standardized_data = standardize_columns(csv_data)

        # Проверки
        is_valid, error = check_required_columns(standardized_data)
        if not is_valid:
            return {'status': 'error', 'message': error}

        is_valid, error = check_empty_values(standardized_data)
        if not is_valid:
            return {'status': 'error', 'message': error}

        # Сохранение
        saved_name = save_standardized_file(
            standardized_data,
            secure_filename(file.filename),  # Защита от небезопасных имён
            upload_folder
        )

        return {
            'status': 'success',
            'message': 'Файл успешно обработан',
            'original_filename': file.filename,
            'saved_as': saved_name,
            'columns': list(standardized_data[0].keys())
        }

    except Exception as e:
        return {'status': 'error', 'message': f'Ошибка обработки файла: {str(e)}'}