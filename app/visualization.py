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
    # Выбор колонки для оси X
    period_col = 'month_str' if period == 'month' else 'day_date'

    fig = px.line(
        df, x=period_col, y='revenue', markers=True,
        title=f'Динамика выручки по {"месяцам" if period == "month" else "дням"}',
        hover_data={period_col: '|Дата', 'revenue': '|'},
        labels={'revenue': 'Выручка'}
    )
    # Форматирование чисел
    max_value = df['revenue'].max()
    tick_values = np.linspace(0, max_value * 1.1, 5)

    if max_value >= 1000:
        # Для больших чисел: без дробной части
        tick_text = [f"{int(round(x)):,}".replace(',', ' ') for x in tick_values]
        hover_format = '%{y:,}'.replace(',', ' ')  # Без .1f
    else:
        # Для маленьких чисел: 1 знак после запятой
        tick_text = [f"{x:,.1f}".replace(',', ' ').replace('.', ',') for x in tick_values]
        hover_format = '%{y:,.1f}'.replace(',', ' ').replace('.', ',')
    # Общие настройки
    fig.update_layout(
        # xaxis_title='Дата',
        yaxis_title='Выручка',
        yaxis_tickvals=tick_values,
        yaxis_ticktext=tick_text,
        yaxis_range = [df['revenue'].min() * 0.9,  # 10% "воздуха" снизу
                        df['revenue'].max() * 1.1]  # 10% сверху
    )

    # fig.update_xaxes(
    #     tickformat='%Y-%m-%d',
    #     hoverformat='%Y-%m-%d'
    # )
    #
    # fig.update_traces(
    #     hovertemplate=f'<b>Дата</b>: %{{x|%Y-%m-%d}}<br><b>Выручка</b>: {hover_format}<extra></extra>'
    # )
    # Специфичные настройки для разных периодов
    if period == 'month':
        fig.update_layout(
            xaxis_title='Месяц',
            xaxis_type='category'  # Важно! Отключаем автоматическую временную шкалу
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


def plot_sales_by_region(df: pd.DataFrame, threshold: float = 0.05) -> str:
    """Строит круговую диаграмму с группировкой мелких регионов в 'Другие'.

    Args:
        df: DataFrame с колонками ['region', 'revenue']
        threshold: Порог (0-1) для объединения в 'Другие' (по умолчанию 5%)

    Returns:
        str: HTML-код графика
    """
    # Сортируем по убыванию выручки
    df = df.sort_values('revenue', ascending=False)

    # Рассчитываем долю выручки
    total = df['revenue'].sum()
    df['share'] = df['revenue'] / total

    # Группируем регионы ниже порога
    others = df[df['share'] < threshold]
    main = df[df['share'] >= threshold]

    if len(others) > 0:
        others_sum = others['revenue'].sum()
        others_share = others_sum / total
        main = pd.concat([
            main,
            pd.DataFrame([{'region': 'Другие', 'revenue': others_sum, 'share': others_share}])
        ])

    # Строим диаграмму
    fig = px.pie(main, names='region', values='revenue',
                 title='Распределение выручки по регионам',
                 hover_data=['share'])

    # Форматируем подписи
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
    fig = px.bar(df.head(top), x='name', y='average_price', title='Средняя цена по товарам')
    fig.update_layout(xaxis_title='Товар', yaxis_title='Средняя цена')
    return pio.to_html(fig, full_html=False)


def is_enough_data(df, date_col='ym'):
    return df[date_col].nunique() > 1



