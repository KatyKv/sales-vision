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
        'товарный знак', 'бренд', 'марка', 'модель', 'артикул', 'код товара',
        'название товара', 'наименование позиции', 'описание', 'продукция',
        'категория', 'тип', 'группа', 'линейка', 'серия',

        # Английские варианты
        'name', 'product', 'item', 'goods', 'article', 'sku', 'model',
        'brand', 'title', 'description', 'product name', 'item name',
        'product title', 'product description', 'product code', 'stock code',
        'item code', 'product group', 'category', 'type', 'series', 'line'
    ]},

    # Для цены
    **{k: 'price' for k in [
        # Русские варианты
        'цена', 'стоимость', 'сумма', 'ценник', 'цена продажи', 'цена покупки', 'выручка',
        'розничная цена', 'оптовая цена', 'себестоимость', 'цена за единицу',
        'цена товара', 'цена позиции', 'цена без скидки', 'финальная цена',
        'рекомендованная цена', 'рыночная цена',

        # Английские варианты
        'price', 'cost', 'amount', 'retail price', 'wholesale price',
        'unit price', 'sale price', 'purchase price', 'list price',
        'market price', 'msrp', 'recommended price', 'final price',
        'item price', 'product price', 'price per unit'
    ]},

    # Для количества
    **{k: 'quantity' for k in [
        # Русские варианты
        'количество', 'кол-во', 'число', 'объем', 'продажи', 'запас',
        'остаток', 'количество на складе', 'доступное количество',
        'количество товара', 'количество позиций', 'штук', 'упаковок',

        # Английские варианты
        'quantity', 'qty', 'amount', 'number', 'count', 'stock',
        'inventory', 'available quantity', 'stock quantity',
        'items in stock', 'units', 'packages', 'pieces'
    ]},

    # Для даты
    **{k: 'date' for k in [
        # Русские варианты
        'дата', 'дата продажи', 'дата покупки', 'дата создания',
        'дата обновления', 'дата транзакции', 'дата заказа',
        'дата поставки', 'дата выполнения', 'время', 'период',
        'год', 'месяц', 'день', 'срок',

        # Английские варианты
        'date', 'sale date', 'purchase date', 'creation date',
        'update date', 'transaction date', 'order date',
        'delivery date', 'fulfillment date', 'time', 'period',
        'year', 'month', 'day', 'datetime', 'timestamp',
        'invoice_date', 'invoicedate'
    ]},

    # Для региона/локации
    **{k: 'region' for k in [
        # Русские варианты
        'регион', 'область', 'город', 'страна', 'территория',
        'зона', 'район', 'округ', 'местоположение', 'локация',
        'место', 'адрес', 'филиал', 'магазин', 'точка продаж',
        'склад', 'центр', 'подразделение',

        # Английские варианты
        'region', 'area', 'city', 'country', 'territory',
        'zone', 'district', 'location', 'place', 'address',
        'branch', 'store', 'shop', 'outlet', 'warehouse',
        'center', 'division', 'department', 'shopping_mall'
    ]},

    # Дополнительные часто используемые поля
    **{k: 'discount' for k in [
        'скидка', 'процент скидки', 'размер скидки', 'discount',
        'discount percent', 'discount amount'
    ]},

    **{k: 'currency' for k in [
        'валюта', 'код валюты', 'currency', 'currency code'
    ]},

    **{k: 'id' for k in [
        'ид', 'код', 'уникальный код', 'идентификатор', 'id',
        'code', 'unique code', 'identifier'
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