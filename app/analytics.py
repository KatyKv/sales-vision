import pandas as pd
import re

def check_date(val):
    """Функция обработки даты в YYYY-MM: поддержка YYYY-MM и полной даты"""
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
    """Загрузка данных из CSV-файла."""
    df = pd.read_csv(filepath)
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


def calculate_metrics(df):
    """Расчет ключевых показателей продаж."""
    metrics = {
        'total_revenue': df['revenue'].sum(),
        'total_sales': df['quantity'].sum(),
        'average_price': df['price'].mean(),
        'average_check': df['revenue'].mean()
    }
    return metrics


def sales_by_date(df):
    """Группировка продаж по дням."""
    return df.groupby('date').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()


def sales_by_month(df):
    """Группировка продаж по месяцам."""
    return df.groupby('ym').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()


def top_products(df, by='quantity', top_n=10):
    """ТОП товаров по количеству продаж или выручке."""
    return df.groupby('name').agg(
        {'quantity': 'sum', 'revenue': 'sum'}
        ).sort_values(by, ascending=False).head(top_n)


def sales_by_region(df):
    """Общая выручка и количество продаж по регионам."""
    return df.groupby('region').agg(
        {'revenue': 'sum', 'quantity': 'sum'}
        ).sort_values('revenue', ascending=False).reset_index()
