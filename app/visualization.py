import matplotlib.pyplot as plt
import seaborn as sns


def plot_sales_trend(df):
    """График динамики продаж."""
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=df, x='ym', y='revenue', marker='o')
    plt.title('Динамика выручки по месяцам')
    plt.xlabel('Дата')
    plt.ylabel('Выручка')
    plt.xticks(rotation=45)
    plt.grid()
    plt.show()


def plot_top_products(df, by='revenue'):
    """Горизонтальная гистограмма ТОП-10 товаров."""
    df = df.sort_values(by, ascending=True)
    plt.figure(figsize=(10, 6))
    sns.barplot(y=df.index, x=df[by], palette='viridis', hue=df.index)
    plt.title(f'ТОП товаров по {"выручке" if by == "revenue" else "продажам"}')
    plt.xlabel('Значение')
    plt.ylabel('Товар')
    plt.grid(axis='x')
    plt.show()


def plot_sales_by_region(df):
    """Круговая диаграмма продаж по регионам."""
    plt.figure(figsize=(8, 8))
    plt.pie(df['revenue'], labels=df['region'], autopct='%1.1f%%',
            startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Доля выручки по регионам')
    plt.show()


def plot_all_together(df, df_top, df_by_region):
    """Все 4 графика на одной фигуре."""
    fig, axes = plt.subplots(2, 2, figsize=(13, 8))

    # График 1: Динамика выручки по месяцам
    sns.lineplot(data=df, x='ym', y='revenue', marker='o', ax=axes[0, 0])
    axes[0, 0].set_title('Динамика выручки по месяцам')
    axes[0, 0].set_xlabel('Дата')
    axes[0, 0].set_ylabel('Выручка')
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid()

    # График 2: ТОП товаров по выручке
    df_sorted_revenue = df_top.sort_values('revenue', ascending=True)
    sns.barplot(y=df_sorted_revenue.index, x=df_sorted_revenue['revenue'],
                palette='viridis', hue=df_sorted_revenue.index, ax=axes[0, 1])
    axes[0, 1].set_title('ТОП товаров по выручке')
    axes[0, 1].set_xlabel('Выручка')
    axes[0, 1].set_ylabel('Товар')
    axes[0, 1].grid(axis='x')

    # График 3: ТОП товаров по количеству
    df_sorted_quantity = df_top.sort_values('quantity', ascending=True)
    sns.barplot(y=df_sorted_quantity.index, x=df_sorted_quantity['quantity'],
                palette='viridis', hue=df_sorted_quantity.index, ax=axes[1, 0])
    axes[1, 0].set_title('ТОП товаров по количеству')
    axes[1, 0].set_xlabel('Количество')
    axes[1, 0].set_ylabel('Товар')
    axes[1, 0].grid(axis='x')

    # График 4: Доля выручки по регионам
    axes[1, 1].pie(df_by_region['revenue'], labels=df_by_region['region'],
                   autopct='%1.1f%%', startangle=140,
                   colors=sns.color_palette('pastel'))
    axes[1, 1].set_title('Доля выручки по регионам')

    plt.tight_layout()
    plt.show()
