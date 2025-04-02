import pandas as pd


def load_data(filepath):
    """Загрузка данных из CSV-файла."""
    df = pd.read_csv(filepath, parse_dates=['date'])
    if 'revenue' not in df.columns:
        df['revenue'] = df['quantity'] * df['price']
    df['ym'] = df['date'].dt.to_period('M').apply(lambda x: x.to_timestamp())
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
    return df.groupby('product_name').agg(
        {'quantity': 'sum', 'revenue': 'sum'}
        ).sort_values(by, ascending=False).head(top_n)


def sales_by_region(df):
    """Общая выручка и количество продаж по регионам."""
    return df.groupby('region').agg(
        {'revenue': 'sum', 'quantity': 'sum'}
        ).sort_values('revenue', ascending=False).reset_index()



