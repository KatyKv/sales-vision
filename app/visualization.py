import plotly.express as px
import plotly.io as pio

def plot_sales_trend(df):
    """График выручки по месяцам"""
    fig = px.line(df, x='ym', y='revenue', markers=True,
                  title='Динамика выручки по месяцам')
    fig.update_layout(xaxis_title='Дата', yaxis_title='Выручка')
    return pio.to_html(fig, full_html=False)

def plot_top_products(df, by='revenue'):
    """Горизонтальная гистограмма ТОП-10 товаров."""
    # Сортируем данные и выбираем топ-10
    df = df.sort_values(by, ascending=False).head(10)
    # Создаем горизонтальную гистограмму
    fig = px.bar(df, y=df.index, x=by, orientation='h',
                  title=f'ТОП товаров по {"выручке" if by == "revenue" else "продажам"}',
                  labels={by: 'Значение', 'index': 'Товар'},
                  color=df.index, # добавляем цвет для различения товаров
                  color_discrete_sequence=px.colors.sequential.Viridis)
    # Обновляем макет для добавления сетки по оси Y
    fig.update_layout(yaxis_title='Товар', xaxis_title='Значение', yaxis=dict(categoryorder='total ascending'))
    return pio.to_html(fig, full_html=False)

def plot_sales_by_region(df):
    """Круговая диаграмма продаж по регионам."""
    fig = px.pie(df, values='revenue', names='region',
                  title='Доля выручки по регионам',
                  color_discrete_sequence=px.colors.sequential.tempo)
    # Обновляем макет, чтобы изменить угол поворота
    fig.update_traces(textinfo='percent+label', hole=0)
    fig.update_layout(showlegend=True) # Показываем легенду
    fig.update_traces(rotation=140) # Устанавливаем начальный угол
    return pio.to_html(fig, full_html=False)
