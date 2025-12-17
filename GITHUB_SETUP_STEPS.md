# Шаги для завершения настройки

## ✅ Уже выполнено автоматически:
- ✅ Git user.name и user.email настроены
- ✅ SSH ключ подготовлен
- ✅ Workflow файл создан

## 📋 Что нужно сделать вручную:

### 1. Создайте репозиторий на GitHub
1. Перейдите на https://github.com/new
2. Название: `dnevnik-uspekha` (или другое)
3. Выберите: **Private** или **Public**
4. **НЕ** добавляйте README, .gitignore или license (они уже есть)
5. Нажмите "Create repository"

### 2. Подключите локальный репозиторий
```bash
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
git push -u origin main
git checkout dev
git push -u origin dev
git checkout main
```

### 3. Настройте Secrets в GitHub
1. Перейдите: Settings → Secrets and variables → Actions
2. Добавьте секреты:

**SERVER_HOST:**
```
ваш-сервер.com
или
192.168.1.100
```

**SERVER_USER:**
```
root
или
deploy
```

**SERVER_SSH_KEY:**
```
[скопируйте приватный ключ из вывода скрипта выше]
```

**SERVER_PATH:**
```
/var/www/dnevnik-uspekha
```

### 4. Подготовьте сервер
```bash
# Подключитесь к серверу
ssh user@your-server.com

# Создайте директорию
sudo mkdir -p /var/www/dnevnik-uspekha
sudo chown -R $USER:$USER /var/www/dnevnik-uspekha

# Клонируйте репозиторий
cd /var/www/dnevnik-uspekha
git clone https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git .

# Или если репозиторий уже есть:
git init
git remote add origin https://github.com/ВАШ_USERNAME/dnevnik-uspekha.git
```

### 5. Добавьте SSH ключ на сервер
```bash
# Скопируйте публичный ключ на сервер
ssh-copy-id -i ~/.ssh/id_rsa_github_actions.pub user@your-server.com

# Или вручную добавьте в ~/.ssh/authorized_keys на сервере
```

### 6. Проверьте деплой
```bash
# Сделайте небольшое изменение
echo "# Test" >> README.md
git add .
git commit -m "Test deployment"
git push origin main
```

Затем проверьте: GitHub → Actions → должен быть успешный деплой ✅

