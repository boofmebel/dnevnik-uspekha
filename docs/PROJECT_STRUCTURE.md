# 📁 Структура проекта - Дневник успеха

Полная структура проекта согласно `rules.md`.

## 🏗️ Общая структура

```
/
├── backend/              # Backend на FastAPI
├── frontend/             # Frontend (Vanilla JS, в будущем Angular)
├── nginx.conf            # Конфигурация Nginx
├── health.html           # Health-check endpoint
├── rules.md              # Правила разработки (Cursor Rules)
├── SECURITY.md           # Документация по безопасности
├── ARCHITECTURE.md       # Документация по архитектуре
└── PROJECT_STRUCTURE.md  # Этот файл
```

## 🔧 Backend структура

```
backend/
├── main.py                    # Главный файл FastAPI приложения
├── requirements.txt           # Python зависимости
├── alembic.ini                # Конфигурация Alembic
├── .env.example               # Пример переменных окружения
│
├── routers/                   # Thin controllers (только вызовы сервисов)
│   ├── __init__.py
│   ├── auth.py               # Аутентификация
│   ├── users.py              # Пользователи
│   ├── children.py           # Дети
│   ├── tasks.py              # Задачи
│   ├── stars.py              # Звёзды
│   └── piggy.py              # Копилка
│
├── services/                  # Бизнес-логика
│   ├── __init__.py
│   └── auth_service.py       # Сервис аутентификации
│
├── repositories/              # Доступ к базе данных
│   ├── __init__.py
│   └── user_repository.py     # Репозиторий пользователей
│
├── schemas/                   # Pydantic модели (request/response)
│   ├── __init__.py
│   └── auth.py               # Схемы аутентификации
│
├── models/                    # SQLAlchemy модели
│   ├── __init__.py
│   └── user.py               # Модель пользователя
│
├── core/                      # Конфиги, utils, exceptions, security
│   ├── __init__.py
│   ├── config.py             # Конфигурация приложения
│   ├── exceptions.py         # Кастомные исключения
│   ├── utils/                # Утилиты
│   └── security/             # JWT, пароли, CSRF
│       ├── __init__.py
│       └── jwt.py            # JWT токены
│
└── migrations/                # Alembic миграции
    ├── env.py
    └── script.py.mako
```

### Принципы backend (согласно rules.md):

- ✅ **Async-first**: AsyncEngine + async_session
- ✅ **JWT Security**: Access token 5-15 минут, Refresh token в HttpOnly cookie
- ✅ **Слоистая архитектура**: routers → services → repositories
- ✅ **Миграции**: Все изменения БД только через Alembic
- ✅ **Валидация**: Pydantic схемы для всех request/response

## 🎨 Frontend структура

```
frontend/
├── index.html                 # Главный HTML файл
├── manifest.json              # PWA манифест
├── README.md                  # Документация frontend
│
├── src/                       # Исходный код
│   ├── js/                    # JavaScript модули
│   │   ├── error-handler.js  # Глобальная обработка ошибок
│   │   ├── utils.js          # Утилиты (валидация, безопасность)
│   │   ├── data.js           # Работа с данными (localStorage/API)
│   │   ├── ui.js             # UI логика (рендеринг, модальные окна)
│   │   ├── app.js            # Инициализация приложения
│   │   └── api.js            # API клиент для backend
│   ├── css/                   # CSS файлы (если будут дополнительные)
│   └── components/            # Компоненты (для будущего Angular)
│
├── static/                    # Статические файлы
│   ├── css/
│   │   └── styles.css        # Основные стили
│   ├── js/                   # Скомпилированные JS (для продакшена)
│   └── images/               # Изображения
│
└── config/                    # Конфигурационные файлы
```

### Принципы frontend (согласно rules.md):

- ✅ **Безопасность**: Защита от XSS (нет innerHTML для пользовательских данных)
- ✅ **Валидация**: Все входные данные валидируются
- ✅ **Обработка ошибок**: Глобальная обработка ошибок
- ✅ **API клиент**: Готов к интеграции с backend

## 📝 Важные файлы

### Backend:
- `backend/main.py` - точка входа FastAPI приложения
- `backend/core/config.py` - конфигурация (переменные окружения)
- `backend/core/security/jwt.py` - JWT токены
- `backend/routers/auth.py` - аутентификация

### Frontend:
- `frontend/index.html` - главный HTML
- `frontend/src/js/app.js` - инициализация
- `frontend/src/js/api.js` - API клиент
- `frontend/static/css/styles.css` - стили

## 🚀 Запуск

### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend:
Открыть `frontend/index.html` в браузере или настроить Nginx для статических файлов.

## 📚 Документация

- `rules.md` - правила разработки
- `SECURITY.md` - меры безопасности
- `ARCHITECTURE.md` - архитектура приложения
- `backend/README.md` - документация backend
- `frontend/README.md` - документация frontend

