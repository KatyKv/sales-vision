# Временный файл для тестирования работы анализа и отображения
# графиков matplotlib. Пока не реализована web-версия

from analytics import (
    load_data, calculate_metrics, sales_by_date,
    sales_by_month, top_products, sales_by_region
)
from visualization import (
    plot_sales_trend, plot_top_products, plot_sales_by_region,
    plot_all_together
)

df = load_data('../data/for_analysis.csv')
metrics = calculate_metrics(df)
for key, value in metrics.items():
    print(f'{key}: {value:.2f}')

df_by_date = sales_by_date(df)
print(df_by_date)

df_by_month = sales_by_month(df)
print(df_by_month)

df_by_region = sales_by_region(df)
print(df_by_region)

df_top = top_products(df)
print(df_top)

df.info()

print('Количество наименований продукции:', len(df['product_name'].unique()))

one_by_one = input('\nВывести графики по очереди? Введите "Y"/"y" или "Д"/"д". '
                   'Иначе все на одном. ').lower()
if one_by_one in ['y', 'д', 'у']:
    plot_sales_trend(df)
    plot_top_products(df_top)
    plot_top_products(df_top, 'quantity')
    plot_sales_by_region(df_by_region)
else:
    plot_all_together(df, df_top, df_by_region)

print('FIN')