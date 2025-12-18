# 🔗 Ссылки на окружения

## 🌐 Продакшн (main ветка)

**Ссылка:** http://89.104.74.123

**Ветка:** `main`

**Автоматический деплой:** При каждом `git push origin main`

**Директория на сервере:** `/var/www/dnevnik-uspekha`

---

## 🧪 Тестовая версия (dev ветка)

**Ссылка:** http://89.104.74.123:8080

**Ветка:** `dev`

**Автоматический деплой:** При каждом `git push origin dev`

**Директория на сервере:** `/var/www/dnevnik-uspekha-test`

---

## 🚀 Быстрая настройка

### Автоматическая настройка (рекомендуется):
```bash
./setup_nginx.sh root@89.104.74.123
```

### Ручная настройка:

1. **На сервере:**
```bash
ssh root@89.104.74.123

# Установите nginx
sudo apt-get update && sudo apt-get install -y nginx

# Создайте директории
sudo mkdir -p /var/www/dnevnik-uspekha
sudo mkdir -p /var/www/dnevnik-uspekha-test
sudo chown -R $USER:$USER /var/www/dnevnik-uspekha*
```

2. **Клонируйте репозитории:**
```bash
# Продакшн
cd /var/www/dnevnik-uspekha
git clone https://github.com/boofmebel/dnevnik-uspekha.git .
git checkout main

# Тест
cd /var/www/dnevnik-uspekha-test
git clone https://github.com/boofmebel/dnevnik-uspekha.git .
git checkout dev
```

3. **Настройте nginx:**
```bash
# Скопируйте конфигурацию
sudo cp /var/www/dnevnik-uspekha/nginx.conf /etc/nginx/sites-available/dnevnik-uspekha
sudo ln -s /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-enabled/

# Проверьте и перезапустите
sudo nginx -t
sudo systemctl reload nginx
```

---

## 📋 Рабочий процесс

### Разработка:
```bash
git checkout dev
# Делаете изменения
git add .
git commit -m "Новая функция"
git push origin dev
# Автоматически деплоится на http://89.104.74.123/test
```

### Релиз в продакшн:
```bash
git checkout main
git merge dev
git push origin main
# Автоматически деплоится на http://89.104.74.123
```

---

## ✅ Проверка

После настройки проверьте:
- ✅ Продакшн: http://89.104.74.123
- ✅ Тест: http://89.104.74.123/test

Оба сайта должны работать независимо друг от друга.

