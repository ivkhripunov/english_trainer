# 🇬🇧 English Trainer

Веб-приложение для изучения английской лексики с карточками и квизами.
Написано на Python/Django в рамках учебного проекта.

## Возможности

- **Словарь** — добавляй, редактируй и удаляй слова (CRUD)
- **Квиз** — проверяй знания в двух направлениях: EN→RU и RU→EN
- **Статистика** — отслеживай точность по каждому слову
- **Поиск и сортировка** — удобная навигация по словарю
- **Валидация** — все формы защищены от некорректного ввода

## Технологии

- Python 3.10+
- Django 4.2
- Bootstrap 5.3
- SQLite (встроенная БД)

## Установка и запуск

```bash
# 1. Клонировать репозиторий
git clone https://github.com/<your-username>/english-trainer.git
cd english-trainer

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Применить миграции
python manage.py migrate

# 5. Загрузить тестовые данные (опционально)
python manage.py loaddata fixtures/initial_words.json

# 6. Запустить сервер
python manage.py runserver
```

Открыть в браузере: http://127.0.0.1:8000/

## Проверка качества кода

```bash
pylint trainer/ english_trainer/
```

## Структура проекта

```
english_trainer/
├── english_trainer/     # Настройки проекта
├── trainer/             # Основное приложение
│   ├── templates/       # HTML-шаблоны
│   ├── models.py        # Модель Word
│   ├── views.py         # Логика страниц и квиза
│   ├── forms.py         # Формы с валидацией
│   └── urls.py          # URL-маршруты
├── fixtures/            # Начальные данные
├── requirements.txt
└── manage.py
```

## Автор

Учебный проект по курсу "Разработка Web-приложения на Django".
