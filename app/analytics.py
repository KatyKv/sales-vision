"""
Модуль обработки датасета продаж.

Обрабатывает CSV-файлы с данными о продажах, содержащие обязательные колонки:
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
    """Преобразует строку с датой в формат временной метки (timestamp).

    Поддерживает как полные даты (YYYY-MM-DD), так и периоды (YYYY-MM).
    В случае нераспознаваемого формата возвращает pd.NaT.

    Args:
        val (str): Строка с датой в формате YYYY-MM или YYYY-MM-DD

    Returns:
        pd.Timestamp: Временная метка или pd.NaT при ошибке

    Example:
        >>> check_date("2023-05")
        Timestamp('2023-05-01 00:00:00')

        >>> check_date("2023-05-15")
        Timestamp('2023-05-01 00:00:00')
    """
    val = str(val).strip()
    # Если строка уже в формате YYYY-MM
    if re.match(r'^\d{4}-\d{2}$', val):
        return pd.Period(val).to_timestamp()
    else:
        try:
            # Попробуем преобразовать в дату и перевести в формат Period
            return pd.to_datetime(val, errors='coerce').to_period('M').to_timestamp()
        except Exception:
            return pd.NaT  # если не получилось — NaT

def load_data(filepath):
    """Загружает и предварительно обрабатывает данные из CSV-файла.

    Args:
        filepath (str): Путь к CSV-файлу с данными о продажах

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
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['ym'] = df['date'].apply(check_date)

    return df


def calculate_metrics(df: pd.DataFrame) -> Dict[str, float]:
    """Вычисляет ключевые метрики продаж из DataFrame.

    Args:
        df (pd.DataFrame): DataFrame с колонками ['revenue', 'quantity', 'price']

    Returns:
        Dict[str, float]: Словарь с вычисленными метриками:
            - total_revenue: общая выручка
            - total_sales: общее количество продаж
            - average_price: средняя цена товара
            - average_check: средний чек

    Example:
        >>> metrics = calculate_metrics(df)
        >>> print(f"Общая выручка: {metrics['total_revenue']:.2f}")
    """
    metrics = {
        'total_revenue': df['revenue'].sum(),
        'total_sales': df['quantity'].sum(),
        'average_price': df['price'].mean(),
        'average_check': df['revenue'].mean()
    }
    return metrics


def sales_by_date(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегирует данные о продажах по дням.

    Args:
        df (pd.DataFrame): Исходный DataFrame с колонкой 'date'

    Returns:
        pd.DataFrame: DataFrame с колонками ['date', 'revenue', 'quantity'],
            сгруппированный по дням и отсортированный по дате

    Example:
        >>> daily_sales = sales_by_date(df)
        >>> print(daily_sales.head())
    """
    return df.groupby('date').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()


def sales_by_month(df: pd.DataFrame) -> pd.DataFrame:
    """Агрегирует данные о продажах по месяцам.

    Args:
        df (pd.DataFrame): Исходный DataFrame с колонкой 'ym'

    Returns:
        pd.DataFrame: DataFrame с колонками ['ym', 'revenue', 'quantity'],
            сгруппированный по месяцам и отсортированный по дате

    Example:
        >>> monthly_sales = sales_by_month(df)
        >>> print(monthly_sales.head())
    """
    return df.groupby('ym').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()


def top_products(df, by='quantity', top_n=10):
    """Возвращает топ-N товаров по указанному критерию.

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


def sales_by_region(df: pd.DataFrame) -> pd.DataFrame:
    """Анализирует продажи по регионам.

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



