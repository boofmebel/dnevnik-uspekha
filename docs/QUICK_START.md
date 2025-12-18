# ⚡ Быстрый старт

## 🎯 За 5 минут

### 1. GitHub Secrets (2 минуты)
```
Settings → Secrets and variables → Actions → New repository secret

Добавьте:
✅ SERVER_HOST = 89.104.74.123
✅ SERVER_USER = root
✅ SERVER_SSH_KEY = (ваш приватный SSH ключ)
✅ SERVER_PATH = /var/www/dnevnik-uspekha
```

### 2. Сервер (2 минуты)
```bash
ssh root@89.104.74.123

# Автоматическая настройка:
cd /path/to/project
./setup_nginx.sh root@89.104.74.123

# ИЛИ вручную:
sudo apt-get install -y nginx git
sudo mkdir -p /var/www/dnevnik-uspekha /var/www/dnevnik-uspekha-test
cd /var/www/dnevnik-uspekha && git clone https://github.com/boofmebel/dnevnik-uspekha.git . && git checkout main
cd /var/www/dnevnik-uspekha-test && git clone https://github.com/boofmebel/dnevnik-uspekha.git . && git checkout dev
sudo cp /var/www/dnevnik-uspekha/nginx.conf /etc/nginx/sites-available/dnevnik-uspekha
sudo ln -sf /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### 3. Проверка (1 минута)
```
✅ http://89.104.74.123 (продакшн)
✅ http://89.104.74.123:8080 (тест)
```

---

## 📋 Подробная инструкция
См. **SETUP_CHECKLIST.md** для детального чек-листа

---

## 🔗 Ссылки
- **Продакшн:** http://89.104.74.123
- **Тест:** http://89.104.74.123:8080
- **GitHub Actions:** https://github.com/boofmebel/dnevnik-uspekha/actions
