# 🖥️ Настройка веб-сервера

## Быстрая настройка Nginx

### 1. Установите Nginx (если не установлен)
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install nginx

# CentOS/RHEL
sudo yum install nginx
```

### 2. Скопируйте конфигурацию
```bash
# На сервере
sudo cp /var/www/dnevnik-uspekha/nginx.conf /etc/nginx/sites-available/dnevnik-uspekha
sudo ln -s /etc/nginx/sites-available/dnevnik-uspekha /etc/nginx/sites-enabled/
```

### 3. Проверьте конфигурацию и перезапустите
```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4. Откройте в браузере
```
http://89.104.74.123
```

## Альтернатива: Python HTTP сервер (для тестирования)

```bash
cd /var/www/dnevnik-uspekha
python3 -m http.server 8000
```

Затем откройте: `http://89.104.74.123:8000`

## Настройка SSL (HTTPS) - опционально

### Используя Let's Encrypt (бесплатно):
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d ваш-домен.com
```

После настройки SSL ссылка будет: `https://ваш-домен.com`

## 🔗 Итоговая ссылка:

**Без домена:**
- HTTP: `http://89.104.74.123`

**С доменом и SSL:**
- HTTPS: `https://ваш-домен.com`

