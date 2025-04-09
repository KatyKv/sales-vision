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

import pandas as pd
import plotly.express as px
import plotly.io as pio

def plot_sales_trend(df: pd.DataFrame,
                     period: Literal['day', 'month']='month') -> str:
    """Строит линейный график динамики выручки за период.

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
    period_col = 'ym' if period=='month' else 'date'
    fig = px.line(df, x=period_col, y='revenue', markers=True,
                  title=f'Динамика выручки по {"месяцам" if period=="month" else "дням"}')
    fig.update_layout(xaxis_title='Дата', yaxis_title='Выручка')
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
    # Сортировка данных и выбор топ-10 (или др.)
    df = df.sort_values(by, ascending=False).head(top)

    # Создаем горизонтальную гистограмму
    fig = px.bar(df, y=df.index, x=by, orientation='h',
                 title=f'ТОП-{top} товаров по {"выручке" if by == "revenue" else "продажам"}',
                 labels={by: 'Значение', 'index': 'Товар'},
                 color=df.index,  # цвет для различения товаров
                 color_discrete_sequence=px.colors.sequential.Viridis)

    # Обновление макета для добавления сетки по оси Y
    fig.update_layout(yaxis_title='Товар', xaxis_title='Значение',
                      yaxis=dict(categoryorder='total ascending'))
    return pio.to_html(fig, full_html=False)


def plot_sales_by_region(df) -> str:
    """Строит круговую диаграмму распределения выручки по регионам.

    Args:
        df: DataFrame с колонками:
            - 'region' (название региона)
            - 'revenue' (суммарная выручка)

    Returns:
        str: HTML-код интерактивной диаграммы

    Example:
        >>> region_df = sales_by_region(raw_df)
        >>> plot_html = plot_sales_by_region(region_df)
    """
    fig = px.pie(df, values='revenue', names='region',
                 title='Доля выручки по регионам',
                 color_discrete_sequence=px.colors.sequential.tempo)

    # Обновление макета, чтобы изменить угол поворота
    fig.update_traces(textinfo='percent+label', hole=0)
    fig.update_layout(showlegend=True)  # Отображение легенды
    fig.update_traces(rotation=140)  # Установка начального угла

    return pio.to_html(fig, full_html=False)



