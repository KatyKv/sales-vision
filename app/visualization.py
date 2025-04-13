"""
Модуль визуализации данных продаж с помощью Plotly.

Предоставляет функции для создания интерактивных визуализаций:
- Тренды продаж по дням/месяцам
- Топ товаров по выручке или количеству продаж
- Распределение продаж по регионам

Входные данные:
Все функции принимают предварительно обработанные DataFrame:
- Для plot_sales_trend: сгруппированные по дням/месяцам
- Для plot_top_products: агрегированные по товарам
- Для plot_sales_by_region: сгруппированные по регионам

Основные функции:
- plot_sales_trend: линейный график динамики выручки
- plot_top_products: барчарт топовых товаров
- plot_sales_by_region: круговая диаграмма по регионам

Пример использования:
    >>> from app.visualization import plot_sales_trend, plot_top_products
    >>> df_monthly = sales_by_month(df)  # из модуля обработки
    >>> html_plot = plot_sales_trend(df_monthly, period='month')
    >>> top_df = top_products(df)  # из модуля обработки
    >>> html_top = plot_top_products(top_df, by='revenue', top=15)

Возвращаемое значение:
Все функции возвращают HTML-код графика (str), который можно:
- Вставить напрямую в шаблон Flask/Jinja2
- Сохранить в файл для статичной визуализации
"""

from typing import Literal

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

def plot_sales_trend(df: pd.DataFrame,
                     period: Literal['day', 'month']='month') -> str:
    """Строит линейный график динамики выручки за период.
    Принимает УЖЕ АГРЕГИРОВАННЫЕ данные (либо по дням, либо по месяцам).

    Args:
        df: DataFrame с колонками:
            - 'ym' или 'date' (в зависимости от периода)
            - 'revenue' (суммарная выручка)
        period: Группировка по 'day' (дням) или 'month' (месяцам)

    Returns:
        str: HTML-код интерактивного графика

    Example:
        >>> df_monthly = sales_by_month(raw_df)
        >>> plot_html = plot_sales_trend(df_monthly, 'month')
        >>> display(HTML(plot_html))  # для Jupyter
    """
    period_col = 'month_str' if period == 'month' else 'day_date'
    fig = px.line(
        df, x=period_col, y='revenue', markers=True,
        hover_data={period_col: '|Дата', 'revenue': '|'},
        labels={'revenue': 'Выручка'}
    )
    # Форматирование чисел
    max_value = df['revenue'].max()
    tick_values = np.linspace(0, max_value * 1.1, 5)
    if max_value >= 1000:
        # Для больших чисел: без дробной части
        tick_text = [f"{int(round(x)):,}".replace(',', ' ') for x in tick_values]
    else:
        # Для маленьких чисел: 1 знак после запятой
        tick_text = [f"{x:,.1f}".replace(',', ' ').replace('.', ',') for x in tick_values]
    # Общие настройки
    fig.update_layout(
        yaxis_title='Выручка',
        yaxis_tickvals=tick_values,
        yaxis_ticktext=tick_text,
        yaxis_range = [df['revenue'].min() * 0.9,  # 10% "воздуха" снизу
                        df['revenue'].max() * 1.1]  # 10% сверху
    )
    # Специфичные настройки для разных периодов
    if period == 'month':
        fig.update_layout(
            xaxis_title='Месяц',
            xaxis_type='category'  # Важно применить категориальный тип, чтобы отключить автоматическую временную шкалу
        )
        fig.update_traces(
            hovertemplate='<b>Месяц</b>: %{x}<br><b>Выручка</b>: %{y:,}<extra></extra>'.replace(',', ' ')
        )
    else:
        fig.update_layout(xaxis_title='Дата')
        fig.update_xaxes(
            tickformat='%Y-%m-%d',
            hoverformat='%Y-%m-%d'
        )
        fig.update_traces(
            hovertemplate='<b>Дата</b>: %{x|%Y-%m-%d}<br><b>Выручка</b>: %{y:,}<extra></extra>'.replace(',', ' ')
        )
    return pio.to_html(fig, full_html=False)


def plot_top_products(df: pd.DataFrame,
                      by: Literal['revenue', 'quantity']='revenue',
                      top: int=10) -> str:
    """Визуализирует топ товаров в виде горизонтальной гистограммы.
    Args:
        df: DataFrame с товарами в индексе и колонками:
            - 'revenue' (суммарная выручка по товару)
            - 'quantity' (количество продаж)
        by: Критерий сортировки ('revenue' или 'quantity')
        top: Количество отображаемых товаров
    Returns:
        str: HTML-код интерактивного графика
    Note:
        Рекомендуется использовать с DataFrame из top_products()
    Example:
        >>> top_df = top_products(raw_df, by='revenue', top_n=15)
        >>> plot_html = plot_top_products(top_df, top=15)
    """
    # Сортировка данных и выбор топ-N
    df = df.sort_values(by, ascending=False).head(top)
    # Форматирование чисел в данных ДО построения графика
    if by == 'quantity':
        df[by] = df[by].round(0).astype(int)
    else:
        df[by] = df[by].round(1 if df[by].max() < 1000 else 0)
    # Горизонтальная гистограмма
    fig = px.bar(df, y=df.index, x=by, orientation='h',
                 labels={by: 'Выручка' if by == 'revenue' else 'Количество', 'index': 'Товар'},
                 color=df.index,  # цвет для различения товаров
                 color_discrete_sequence=px.colors.sequential.Viridis)
    # Настройка подсказок
    hover_template = (
            '<b>Товар</b>: %{y}<br>'
            f'<b>{"Выручка" if by == "revenue" else "Количество"}</b>: '
            '%{x:,}' + ('' if by == 'quantity' else '.1f' if df[by].max() < 1000 else '') +
            '<extra></extra>'
    ).replace(',', ' ').replace('.', ',')
    fig.update_traces(hovertemplate=hover_template)

    # Общие настройки
    fig.update_layout(
        yaxis_title='Товар',
        xaxis_title="Выручка" if by == "revenue" else "Количество",
        yaxis=dict(categoryorder='total ascending'),
        legend_title_text = 'Товар'
    )
    return pio.to_html(fig, full_html=False)


def plot_sales_by_region(df: pd.DataFrame) -> str:
    """Строит круговую диаграмму с группировкой мелких регионов в 'Другие'.

    Args:
        df: DataFrame с колонками ['region', 'revenue']

    Returns:
        str: HTML-код графика
    """
    # Сортировка по убыванию выручки
    df = df.sort_values('revenue', ascending=False)

    # Доля выручки
    total = df['revenue'].sum()
    df['share'] = df['revenue'] / total


    # Диаграмма
    fig = px.pie(df, names='region', values='revenue',
                 hover_data=['share'])

    # Форматирование подписей
    fig.update_traces(
        textposition='inside',
        texttemplate='%{label}<br>%{percent:.1%}',
        hovertemplate='<b>%{label}</b><br>Выручка: %{value:,.0f}<br>Доля: %{percent:.1%}'
    )

    fig.update_layout(
        uniformtext_minsize=12,
        uniformtext_mode='hide'
    )

    return pio.to_html(fig, full_html=False)


def plot_average_price_per_product(df: pd.DataFrame, top: int = 10) -> str:
    """Строит барчарт по средней цене товаров.

    Args:
        df: DataFrame с колонками:
            - 'name' (название товара)
            - 'average_price' (средняя цена)
        top: Количество отображаемых товаров

    Returns:
        str: HTML-код интерактивного графика

    Example:
        >>> df_avg_prices = average_price_per_product(df)
        >>> plot_html = plot_average_price_per_product(df_avg_prices, top=10)
        >>> display(HTML(plot_html))  # для Jupyter
    """
    # Подготовка данных
    df = df.head(top).copy()
    df['average_price'] = df['average_price'].round(2)

    # Построение графика
    fig = px.bar(
        df,
        x='name',
        y='average_price',
        labels={'name': 'Товар', 'average_price': 'Средняя цена'},
        color='name',
        color_discrete_sequence=px.colors.sequential.Viridis
    )

    # Форматирование чисел
    max_price = df['average_price'].max()
    if max_price >= 1000:
        yaxis_tickformat = ',.0f'
        hover_format = ',.0f'
    else:
        yaxis_tickformat = ',.2f'
        hover_format = ',.2f'

    # Настройка подсказок
    fig.update_traces(
        hovertemplate=(
            '<b>Товар</b>: %{x}<br>'
            '<b>Средняя цена</b>: %{y:,.2f}<extra></extra>'
        ).replace(',', ' ').replace('.', ',')
    )

    # Общие настройки
    fig.update_layout(
        xaxis_title='Товар',
        yaxis_title='Средняя цена',
        showlegend=False,
        yaxis_tickformat=yaxis_tickformat.replace('.', ','),
        separators=', '
    )

    return pio.to_html(fig, full_html=False)

def is_enough_data(df, date_col='ym'):
    return df[date_col].nunique() > 1



