# Инструкция по деплою

## Подключение к GitHub

1. Создайте новый репозиторий на GitHub (например, `dnevnik-uspekha`)

2. Подключите локальный репозиторий к GitHub:
```bash
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
```

3. Отправьте обе ветки на GitHub:
```bash
# Отправляем main
git push -u origin main

# Отправляем dev
git checkout dev
git push -u origin dev

# Возвращаемся на main
git checkout main
```

## Рабочий процесс

### Разработка (ветка dev)
```bash
git checkout dev
# Делаете изменения
git add .
git commit -m "Описание изменений"
git push origin dev
```

### Релиз (ветка main)
```bash
# Переключаемся на main
git checkout main

# Мержим изменения из dev
git merge dev

# Отправляем на GitHub
git push origin main

# После push на main автоматически запустится деплой на сервер
```

## Настройка деплоя на сервер

### Вариант 1: GitHub Actions (рекомендуется)

Создайте файл `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Server

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        uses: appleboy/ssh-action@master
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SERVER_SSH_KEY }}
          script: |
            cd /path/to/your/project
            git pull origin main
            # Дополнительные команды если нужно (npm install, build и т.д.)
```

**Настройка секретов в GitHub:**
1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте:
   - `SERVER_HOST` - IP или домен вашего сервера
   - `SERVER_USER` - пользователь для SSH
   - `SERVER_SSH_KEY` - приватный SSH ключ

### Вариант 2: Webhook на сервере

1. Создайте скрипт на сервере `/path/to/deploy.sh`:
```bash
#!/bin/bash
cd /path/to/your/project
git pull origin main
# Дополнительные команды если нужно
```

2. Настройте GitHub Webhook:
   - Settings → Webhooks → Add webhook
   - Payload URL: `https://your-server.com/webhook/deploy`
   - Content type: `application/json`
   - Events: только `push` на ветку `main`

3. На сервере создайте endpoint для webhook (через nginx, apache или node.js)

### Вариант 3: Ручной деплой через SSH

Используйте скрипт `deploy.sh` (создан ниже) для ручного деплоя.

