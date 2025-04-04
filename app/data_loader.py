import os
import csv
from io import StringIO

# Настройки по умолчанию
DEFAULT_UPLOAD_FOLDER = 'uploads'
COLUMN_NAMES = {
    'имя': 'name',
    'name': 'name',
    'название': 'name',
    'товар': 'name',
    'product': 'name',
    'цена': 'price',
    'price': 'price',
    'стоимость': 'price',
    'количество': 'quantity',
    'quantity': 'quantity',
    'кол-во': 'quantity'
}
REQUIRED_COLUMNS = ['name', 'price']


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
        writer = csv.DictWriter(f, fieldnames=REQUIRED_COLUMNS + ['quantity'])
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
        file_content = file.stream.read().decode('utf-8')
        csv_data = list(csv.DictReader(StringIO(file_content)))

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
            file.filename,
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