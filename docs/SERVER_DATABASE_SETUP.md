# 🐘 НАСТРОЙКА POSTGRESQL НА СЕРВЕРЕ

## Вариант 1: PostgreSQL уже установлен на сервере

### Шаг 1: Получите данные подключения
Нужны следующие данные:
- **Host**: IP сервера или localhost (если на том же сервере)
- **Port**: обычно 5432
- **Database**: dnevnik_uspekha
- **User**: обычно postgres
- **Password**: пароль пользователя БД

### Шаг 2: Обновите DATABASE_URL в .env
```env
DATABASE_URL=postgresql+asyncpg://user:password@89.104.74.123:5432/dnevnik_uspekha
```

### Шаг 3: Выполните миграцию на сервере
```bash
# На сервере
cd /path/to/project/backend
source venv/bin/activate
alembic upgrade head
```

---

## Вариант 2: Установка PostgreSQL на сервере (Linux)

### Шаг 1: Подключитесь к серверу
```bash
ssh user@89.104.74.123
```

### Шаг 2: Установите PostgreSQL
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y postgresql postgresql-contrib

# CentOS/RHEL
sudo yum install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
```

### Шаг 3: Запустите PostgreSQL
```bash
# Ubuntu/Debian
sudo systemctl start postgresql
sudo systemctl enable postgresql

# CentOS/RHEL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

### Шаг 4: Создайте базу данных
```bash
sudo -u postgres psql
CREATE DATABASE dnevnik_uspekha;
CREATE USER your_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE dnevnik_uspekha TO your_user;
\q
```

### Шаг 5: Настройте доступ (если нужно удаленное подключение)
Отредактируйте `/etc/postgresql/14/main/postgresql.conf`:
```
listen_addresses = '*'
```

Отредактируйте `/etc/postgresql/14/main/pg_hba.conf`:
```
host    all             all             0.0.0.0/0               md5
```

Перезапустите PostgreSQL:
```bash
sudo systemctl restart postgresql
```

---

## Вариант 3: Использовать Docker на сервере

### Шаг 1: Установите Docker (если нет)
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Шаг 2: Запустите PostgreSQL через Docker
```bash
docker run --name dnevnik-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=dnevnik_uspekha \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:14
```

---

## После установки на сервере

### 1. Обновите DATABASE_URL в .env
```env
# Если БД на том же сервере, где backend
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/dnevnik_uspekha

# Если БД на другом сервере
DATABASE_URL=postgresql+asyncpg://postgres:password@89.104.74.123:5432/dnevnik_uspekha
```

### 2. Выполните миграцию
```bash
cd backend
source venv/bin/activate
alembic upgrade head
```

### 3. Проверьте подключение
```bash
python scripts/check_setup.py
```

