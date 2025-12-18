# Как добавить workflow через GitHub UI

GitHub требует специальные права для создания workflow файлов через API. 
Workflow файл временно удален, но сохранен в `deploy.yml.backup`.

## Способ 1: Через веб-интерфейс GitHub (рекомендуется)

1. Перейдите на GitHub: https://github.com/boofmebel/dnevnik-uspekha
2. Нажмите "Add file" → "Create new file"
3. Введите путь: `.github/workflows/deploy.yml`
4. Скопируйте содержимое из файла `deploy.yml.backup` в редактор
5. Нажмите "Commit new file"

## Способ 2: Настроить Personal Access Token с правами workflow

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Выберите scope: `workflow`
4. Скопируйте токен
5. Используйте токен вместо пароля при push:
   ```bash
   git remote set-url origin https://YOUR_TOKEN@github.com/boofmebel/dnevnik-uspekha.git
   git push -u origin main
   ```

## Способ 3: Использовать SSH

```bash
git remote set-url origin git@github.com:boofmebel/dnevnik-uspekha.git
git push -u origin main
```

После этого workflow файл можно вернуть обратно.

