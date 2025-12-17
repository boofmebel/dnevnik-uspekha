# Настройка Secrets в GitHub

## Шаги:

1. Перейдите: https://github.com/boofmebel/dnevnik-uspekha/settings/secrets/actions

2. Нажмите "New repository secret" и добавьте:

### SERVER_HOST
```
ваш-ip-адрес-сервера
```
**ВАЖНО:** Не используйте реальный IP в документации! Храните только в Secrets.

### SERVER_USER
```
root
```
(или другой пользователь, если используете не root)

### SERVER_SSH_KEY
Скопируйте ВСЁ содержимое файла `SSH_PRIVATE_KEY.txt` (включая BEGIN и END строки)

### SERVER_PATH
```
/var/www/dnevnik-uspekha
```

### SERVER_PORT (опционально)
```
22
```
(можно не добавлять, по умолчанию 22)

## После настройки:

Workflow будет автоматически запускаться при каждом `git push origin main`

