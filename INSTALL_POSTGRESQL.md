# 🐘 УСТАНОВКА POSTGRESQL

## Вариант 1: Docker (РЕКОМЕНДУЕТСЯ - самый простой)

### Шаг 1: Установите Docker Desktop
- macOS: https://www.docker.com/products/docker-desktop
- Скачайте и установите Docker Desktop

### Шаг 2: Запустите PostgreSQL
```bash
# Из корневой директории проекта
./backend/scripts/start_postgres.sh

# Или вручную:
docker-compose up -d postgres
```

### Шаг 3: Проверьте статус
```bash
docker ps | grep postgres
```

---

## Вариант 2: Homebrew (macOS)

### Шаг 1: Установите Homebrew (если нет)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Шаг 2: Установите PostgreSQL
```bash
brew install postgresql@14
```

### Шаг 3: Запустите PostgreSQL
```bash
brew services start postgresql@14
```

### Шаг 4: Создайте базу данных
```bash
createdb dnevnik_uspekha
```

---

## Вариант 3: Официальный установщик (macOS)

### Шаг 1: Скачайте установщик
- Перейдите на: https://www.postgresql.org/download/macosx/
- Скачайте установщик для вашей версии macOS

### Шаг 2: Установите PostgreSQL
- Запустите установщик
- Следуйте инструкциям
- Запомните пароль для пользователя postgres

### Шаг 3: Создайте базу данных
```bash
# Добавьте PostgreSQL в PATH (если нужно)
export PATH="/Library/PostgreSQL/14/bin:$PATH"

# Создайте БД
createdb -U postgres dnevnik_uspekha
```

---

## Вариант 4: Использовать удаленную БД

Если у вас есть доступ к удаленному PostgreSQL серверу:

1. Обновите `DATABASE_URL` в `backend/.env`:
```env
DATABASE_URL=postgresql+asyncpg://user:password@remote-host:5432/dnevnik_uspekha
```

2. Проверьте подключение:
```bash
cd backend
source venv/bin/activate
python scripts/check_setup.py
```

---

## После установки PostgreSQL

### 1. Проверьте подключение
```bash
cd backend
source venv/bin/activate
python scripts/check_setup.py
```

### 2. Выполните миграцию
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 3. Проверьте готовность
```bash
curl http://localhost:8000/ready
```

---

## Troubleshooting

### PostgreSQL не запускается
- Проверьте логи: `docker logs dnevnik-postgres` (для Docker)
- Проверьте порт 5432: `lsof -i :5432`
- Убедитесь, что пароль в `.env` совпадает с паролем в PostgreSQL

### Ошибка подключения
- Проверьте, что PostgreSQL запущен
- Проверьте `DATABASE_URL` в `.env`
- Проверьте права доступа пользователя postgres

### Порт 5432 занят
- Остановите другой экземпляр PostgreSQL
- Или измените порт в `docker-compose.yml` и `.env`

