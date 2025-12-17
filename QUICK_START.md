# 🚀 Быстрый старт - что уже сделано

## ✅ Автоматически выполнено:

1. ✅ **Git настроен** (user.name и user.email)
2. ✅ **SSH ключ подготовлен** (`id_rsa_github_actions`)
3. ✅ **Workflow файл создан** (`.github/workflows/deploy.yml`)
4. ✅ **Ветки созданы** (main и dev)
5. ✅ **Все файлы закоммичены**

## 📋 Что осталось сделать (5 минут):

### 1. Создайте репозиторий на GitHub
- Перейдите: https://github.com/new
- Название: `dnevnik-uspekha` (или другое)
- **НЕ** добавляйте README, .gitignore (они уже есть)
- Нажмите "Create repository"

### 2. Подключите репозиторий
```bash
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
git push -u origin main
git checkout dev
git push -u origin dev
git checkout main
```

### 3. Настройте Secrets в GitHub
1. GitHub → Settings → Secrets and variables → Actions
2. Добавьте 4 секрета:

| Name | Value |
|------|-------|
| `SERVER_HOST` | IP или домен вашего сервера |
| `SERVER_USER` | Пользователь SSH (например: `root`) |
| `SERVER_SSH_KEY` | Содержимое файла `SSH_PRIVATE_KEY.txt` |
| `SERVER_PATH` | Путь на сервере (например: `/var/www/dnevnik-uspekha`) |

### 4. Подготовьте сервер
```bash
# На сервере
mkdir -p /var/www/dnevnik-uspekha
cd /var/www/dnevnik-uspekha
git clone https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git .

# Добавьте публичный ключ на сервер
# Скопируйте содержимое SSH_PUBLIC_KEY.txt в ~/.ssh/authorized_keys
```

### 5. Проверьте деплой
```bash
echo "# Test" >> README.md
git add .
git commit -m "Test deployment"
git push origin main
```

Проверьте: GitHub → Actions → должен быть успешный деплой ✅

---

## 📁 Полезные файлы:

- `SSH_PRIVATE_KEY.txt` - приватный ключ для GitHub Secrets
- `SSH_PUBLIC_KEY.txt` - публичный ключ для сервера
- `GITHUB_SETUP_STEPS.md` - подробная инструкция
- `SETUP_GITHUB_ACTIONS.md` - детальная настройка

