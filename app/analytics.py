"""
Модуль обработки датасета продаж.

Обрабатывает CSV-файлы с данными о продажах, содержащие обязательные колонки
(наличие обязательных колонок проверяется при загрузке в модуле data_loader.py):
- name: название товара
- price: цена товара
- quantity: количество проданных единиц
- date: дата продажи (поддерживает форматы YYYY-MM-DD и YYYY-MM)
- region: регион продажи

Основные функции:
- load_data(): загрузка и предварительная обработка данных
- calculate_metrics(): расчет ключевых метрик продаж
- sales_by_date/month(): агрегация данных по временным периодам
- top_products(): анализ топовых товаров
- sales_by_region(): анализ продаж по регионам

Пример использования:
    >>> df = load_data('sales.csv')
    >>> metrics = calculate_metrics(df)
    >>> monthly_sales = sales_by_month(df)
"""
import logging
import re
from typing import Dict, Any

import pandas as pd

logger = logging.getLogger(__name__)

def check_date(val: str) -> pd.Timestamp:
    """Преобразование строки с датой в pd.Timestamp, без времени.

    Поддерживает разные форматы:
    - MM/DD/YYYY или DD/MM/YYYY (определяется автоматически)
    - YYYY-MM
    - YYYY-MM-DD
    Возвращает только дату без времени.
    В случае нераспознаваемого формата возвращает pd.NaT.

    Args:
        val (str): Строка с датой

    Returns:
        pd.Timestamp: Временная метка или pd.NaT при ошибке

    Example:
        >>> check_date("2023-05")
        Timestamp('2023-05-01')

        >>> check_date("2023-05-15")
        Timestamp('2023-05-01')
    """
    val = str(val).strip()

    # 1. Год-месяц (например, "2023-01")
    if re.match(r'^\d{4}-\d{2}$', val):
        return pd.Period(val).to_timestamp()

    # 2. Явно DD/MM/YYYY — если день > 12
    if re.match(r'^\d{1,2}/\d{1,2}/\d{4}$', val):
        parts = val.split("/")
        day, month = int(parts[0]), int(parts[1])
        if day > 12:
            try:
                return pd.to_datetime(val, dayfirst=True).normalize()
            except Exception:
                return pd.NaT

    # 3. Всё остальное — парсинг с нормализацией
    try:
        parsed = pd.to_datetime(val)
        return parsed.normalize()
    except Exception:
        logger.warning(f"Не удалось распознать дату: {val}")
        return pd.NaT

def load_data(filepath: str) -> pd.DataFrame:
    """Загрузка и предварительная обработка данных из CSV-файла.

    Args:
        filepath (str): Путь к CSV-файлу с данными о продажах.
        Файл должен содержать обязательные колонки:
        name, price, quantity, date, region

    Returns:
        pd.DataFrame: Обработанный DataFrame с дополнительными колонками:
            - revenue: выручка (price * quantity)
            - ym: период в формате YYYY-MM (тип Period)

    Raises:
        ValueError: Если файл не содержит обязательных колонок
    """
    logger.info(f'Загрузка данных из {filepath}')
    try:
        df = pd.read_csv(filepath)
        logger.info(f'Успешно загружено {len(df)} строк')
        logger.info(f'Первые 3 строки данных:\n{df.head(3)}')
    except Exception as e:
        logger.error(f"Ошибка загрузки файла: {e}")
        raise
    numeric_columns = ['price', 'quantity']
    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    if 'revenue' not in df.columns:
        df['revenue'] = df['quantity'] * df['price']
    else:
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce')


    df['date'] = df['date'].apply(check_date)
    # Проверка на успешное преобразование дат
    if df['date'].isnull().any():
        logger.warning("Некоторые даты не были распознаны правильно")
    # df['ym'] = df['date'].dt.to_period('M')
    # Создание производных колонок
    df['day_date'] = df['date'].dt.normalize()  # Для дневных данных
    df['month_str'] = df['date'].dt.strftime('%Y-%m')  # Для месячных
    # df['ym'] = df['date'].dt.to_period('M')  # Дополнительная колонка для совместимости
    _preview_dates(df)
    logger.info(f'Первые 3 строки после обработки:\n{df.head(3)}')

    return df


def _preview_dates(df, column='date', limit=10):
    """ТЕСТОВАЯ ВРЕМЕННАЯ ФУНКЦИЯ проверки загруженной даты"""
    print(f"{'Исходная строка':<25} | {'Обработанная дата'}")
    print("-" * 50)
    seen = set()
    count = 0
    for val in df[column].unique():
        if val in seen:
            continue
        seen.add(val)
        parsed = check_date(val)
        print(f"{str(val):<25} | {parsed}")
        count += 1
        if count >= limit:
            break

def calculate_metrics(df: pd.DataFrame) -> Dict[str, Dict[str, Any]]:
    """Вычисление ключевых метрик продаж из DataFrame.

    Args:
        df (pd.DataFrame): DataFrame с колонками ['revenue', 'quantity', 'price']

    Returns:
        Dict[str, float]: Словарь с вычисленными метриками:
            - total_revenue: выручка
            - total_sales: объем продаж
            - average_price: средняя цена товара

    Example:
        >>> metrics = calculate_metrics(df)
        >>> print(f"Общая выручка: {metrics['total_revenue']:.2f}")
    """
    metrics = {
        'total_revenue': {'value': round(df['revenue'].sum(), 2), 'name_ru': 'Выручка'},
        'total_sales': {'value': int(df['quantity'].sum()), 'name_ru': 'Объем продаж'},  # целое, не округляю
        'average_price': {'value': round(df['price'].mean(), 2), 'name_ru': 'Средняя цена'},
        'median_price': {'value': round(df['price'].median(), 2), 'name_ru': 'Медианная цена'}
    }
    return metrics


def sales_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегация данных о продажах по дням.

    Args:
        df (pd.DataFrame): Исходный DataFrame с колонкой 'date'

    Returns:
        pd.DataFrame: DataFrame с колонками ['date', 'revenue', 'quantity'],
            сгруппированный по дням и отсортированный по дате

    Example:
        >>> daily_sales = sales_by_date(df)
        >>> print(daily_sales.head())
    """
    return df.groupby('day_date').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()


def sales_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегация данных о продажах по месяцам.

    Args:
        df (pd.DataFrame): Исходный DataFrame с колонкой 'ym'

    Returns:
        pd.DataFrame: DataFrame с колонками ['ym', 'revenue', 'quantity'],
            сгруппированный по месяцам и отсортированный по дате

    Example:
        >>> monthly_sales = sales_by_month(df)
        >>> print(monthly_sales.head())
    """
    result = df.groupby('month_str').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
    # result['month_str'] = result['month_str'].dt.to_timestamp()  # преобразование Period в Timestamp
    return result

def top_products(
        df: pd.DataFrame,
        by: str = 'quantity',
        top_n: int = 10) -> pd.DataFrame:
    """Топ-N товаров по указанному критерию.

    Args:
        df (pd.DataFrame): Исходный DataFrame
        by (str): Критерий сортировки ('quantity' или 'revenue')
        top_n (int): Количество возвращаемых товаров

    Returns:
        pd.DataFrame: DataFrame с колонками ['quantity', 'revenue']

    Example:
        >>> top = top_products(df, by='revenue', top_n=5)
        >>> print(top.head())
    """
    return df.groupby('name').agg(
        {'quantity': 'sum', 'revenue': 'sum'}
        ).sort_values(by, ascending=False).head(top_n)

def average_price_per_product(df: pd.DataFrame) -> pd.DataFrame:
    """Расчет средней цены по каждому товару.

    Учитывает случаи, когда один товар продавался по разной цене.

    Args:
        df (pd.DataFrame): DataFrame с колонками ['name', 'price']

    Returns:
        pd.DataFrame: DataFrame с колонками ['name', 'average_price'],
            отсортированный по убыванию средней цены

    Example:
        >>> avg_prices = average_price_per_product(df)
        >>> print(avg_prices.head())
    """
    return df.groupby('name')['price'].mean().reset_index(
        ).rename(columns={'price': 'average_price'}
        ).sort_values('average_price', ascending=False)


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Анализ продаж по регионам.

    Группирует данные по регионам, вычисляя общую выручку и количество продаж.
    Результат сортируется по убыванию выручки.

    Args:
        df: DataFrame с колонками ['region', 'revenue', 'quantity']

    Returns:
        DataFrame с колонками ['region', 'revenue', 'quantity'],
        отсортированный по выручке

    Example:
        >>> df = load_data('sales.csv')
        >>> region_stats = sales_by_region(df)
        >>> print(region_stats.head(3))

                   region  revenue  quantity
        0        Москва    1.2e6      1200
        1  Санкт-Петербург 8.5e5       950
        2      Новосибирск 3.2e5       420
    """
    return df.groupby('region').agg(
        {'revenue': 'sum', 'quantity': 'sum'}
        ).sort_values('revenue', ascending=False).reset_index()


def top_products_by_region(df: pd.DataFrame, by='quantity', top_n=3) -> pd.DataFrame:
    """Определение топ-N товаров по каждому региону.

    Args:
        df (pd.DataFrame): Исходный DataFrame с колонками ['region', 'name', 'quantity', 'revenue']
        by (str): Критерий сортировки ('quantity' или 'revenue')
        top_n (int): Количество топ-товаров на регион

    Returns:
        pd.DataFrame: DataFrame с мультииндексом ['region', 'rank'] и колонками ['name', 'quantity', 'revenue']

    Example:
        >>> top = top_products_by_region(df, by='revenue', top_n=2)
        >>> print(top.head())
    """
    grouped = df.groupby(['region', 'name']).agg({'quantity': 'sum', 'revenue': 'sum'})
    grouped = grouped.sort_values([by], ascending=False).reset_index()

    result = (
        grouped.groupby('region')
        .head(top_n)
        .reset_index(drop=True)
        .assign(rank=lambda x: x.groupby('region').cumcount() + 1)
        .set_index(['region', 'rank'])
    )
    return result




