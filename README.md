# Sales Vision

## 📌 Описание проекта

**Sales Vision** — это веб-приложения для автоматизированного анализа данных по продажам. Оно разработано в рамках учебной командной работы по теме "Аналитика данных" ( ТЗ №4).

Приложение позволяет загружать CSV-файлы с продажами и без технических навыков получать наглядную аналитику: ключевые метрики, графики, динамику и таблицы. Всё происходит быстро, визуально и просто — без Excel, SQL или кода.

### 🌟 Целевая аудитория

- Предприниматели и маркетологи
- Начинающие аналитики
- Руководители, которым нужен быстрый отчёт "на лету"

---

## 💡 Ключевые возможности

- Загрузка и обработка CSV-файлов
- Очистка и нормализация "грязных" данных
- Расчёт метрик: выручка, объем продаж, средняя цена
- Графики (Plotly): линейные, столбчатые, круговые
- Визуальный прогресс-бар (через SSE)
- Фильтры и выбор типа графика
- Скачивание итогового отчёта

---

## 🧠 Архитектура проекта

**MVC (Model-View-Controller):**

- **Model**
  - `data_loader.py` — обработка и очистка CSV
  - `analytics.py` — расчёт метрик
  - `visualization.py` — графики
  - `models.py` — задел под БД
- **View**
  - `templates/` и `static/`
- **Controller**
  - `routes.py`, `forms.py`, SSE, jQuery

---

## 📊 Структура проекта

```
sales-vision/
├── app/
│   ├── static/
│   │   ├── css/               # Стили
│   │   └── img/               # Демо-изображения
│   ├── templates/             # HTML-шаблоны
│   ├── analytics.py           # Метрики, обработка датафрейма
│   ├── data_loader.py         # Обработка CSV
│   ├── forms.py               # Flask-формы
│   ├── models.py              # Модель (БД)
│   ├── routes.py              # Маршруты
│   └── visualization.py       # Графики
├── config.py                  # Настройки
├── create_db.py               # Скрипт СБ
├── data/datasets_for_test/    # Тестовые CSV
├── instance/users.db          # SQLite-база
├── legacy/                    # Устаревшие файлы
├── tests/                     # Тесты (в разработке)
├── uploads/                   # Обработанные CSV
├── app.log                    # Лог-файл
├── LICENSE
├── main.py                    # Точка запуска
├── README.md
└── requirements.txt
```

---

## ⚙️ Технологии

- **Backend**: Flask, Pandas
- **Frontend**: HTML, CSS (Bootstrap), Jinja2, JS (jQuery)
- **Графики**: Plotly
- **Для прогресса**: SSE (Server-Sent Events)

---

## 🚀 Запуск проекта

```bash
pip install -r requirements.txt
python main.py
```

Перейдите в браузере:
```
http://127.0.0.1:5000
```

