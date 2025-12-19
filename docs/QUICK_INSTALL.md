# 🚀 Быстрая установка токена

## ✅ Токен готов!

## 📋 Простая инструкция (3 шага):

### 1. Откройте админку
```
http://89.104.74.123:3000/admin.html
```

### 2. Откройте консоль браузера
Нажмите **F12** → вкладка **Console**

### 3. Выполните этот код:

```javascript
localStorage.setItem('admin_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2MTM3NTI4LCJ0eXBlIjoiYWNjZXNzIn0.hD3XHJQ-a2MjIA-LLzk6s4KzgSC4Fdo9JUybWwkwRnM');
location.reload();
```

**Готово!** Страница обновится и токен будет установлен.

---

## 🔍 Проверка

После установки проверьте в консоли:
```javascript
console.log('Токен:', localStorage.getItem('admin_token'));
```

Должен показать токен.

---

## 📝 Альтернативный способ

Если не работает, попробуйте открыть консоль и выполнить по частям:

1. Установка токена:
```javascript
localStorage.setItem('admin_token', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIiwiZXhwIjoxNzY2MTM3NTI4LCJ0eXBlIjoiYWNjZXNzIn0.hD3XHJQ-a2MjIA-LLzk6s4KzgSC4Fdo9JUybWwkwRnM');
```

2. Проверка:
```javascript
console.log(localStorage.getItem('admin_token'));
```

3. Обновление страницы:
```javascript
location.reload();
```

