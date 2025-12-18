# 🛠️ Руководство по реализации монетизации

## 📋 Быстрый старт

### Вариант 1: Node.js/Express (рекомендуется)
- ✅ Проще для фронтенда (один язык)
- ✅ Быстрая разработка
- ✅ Много готовых решений

### Вариант 2: Python/FastAPI
- ✅ Мощный и быстрый
- ✅ Отличная документация
- ✅ Хорошо для аналитики

---

## 🏗️ СТРУКТУРА ПРОЕКТА

```
dnevnik-uspekha/
├── frontend/              # React или чистый JS
│   ├── public/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   ├── Login.jsx
│   │   │   ├── ParentDashboard.jsx
│   │   │   ├── ChildApp.jsx      # Текущее приложение
│   │   │   └── AdminPanel.jsx
│   │   ├── components/
│   │   ├── services/
│   │   │   └── api.js            # API клиент
│   │   └── utils/
│   └── package.json
│
├── backend/              # Node.js/Express
│   ├── src/
│   │   ├── models/       # Модели БД
│   │   ├── routes/      # API маршруты
│   │   ├── middleware/  # Auth, roles
│   │   ├── services/    # Бизнес-логика
│   │   └── config/      # Конфигурация
│   ├── migrations/      # Миграции БД
│   └── package.json
│
├── database/
│   └── schema.sql       # Схема БД
│
└── docs/
    └── API.md           # Документация API
```

---

## 🔐 АУТЕНТИФИКАЦИЯ (Пример кода)

### Backend (Node.js/Express):

```javascript
// backend/src/middleware/auth.js
const jwt = require('jsonwebtoken');

const authMiddleware = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  
  if (!token) {
    return res.status(401).json({ error: 'Токен не предоставлен' });
  }
  
  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Недействительный токен' });
  }
};

const roleMiddleware = (...allowedRoles) => {
  return (req, res, next) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Доступ запрещен' });
    }
    next();
  };
};

module.exports = { authMiddleware, roleMiddleware };
```

### Frontend (API клиент):

```javascript
// frontend/src/services/api.js
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:3000/api';

class ApiClient {
  constructor() {
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_URL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);
    
    if (response.status === 401) {
      // Токен истек
      localStorage.removeItem('token');
      window.location.href = '/login';
      return;
    }

    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || 'Ошибка запроса');
    }

    return data;
  }

  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    if (data.token) {
      this.token = data.token;
      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify(data.user));
    }
    
    return data;
  }

  async getChildren() {
    return this.request('/parent/children');
  }

  async createChild(childData) {
    return this.request('/parent/child', {
      method: 'POST',
      body: JSON.stringify(childData),
    });
  }

  // ... другие методы
}

export default new ApiClient();
```

---

## 📊 API ENDPOINTS

### Аутентификация:
```javascript
POST   /api/auth/register    - Регистрация родителя
POST   /api/auth/login       - Вход
POST   /api/auth/refresh     - Обновление токена
POST   /api/auth/logout      - Выход
```

### Родитель:
```javascript
GET    /api/parent/profile           - Профиль родителя
GET    /api/parent/children          - Список детей
POST   /api/parent/child              - Создать профиль ребенка
PUT    /api/parent/child/:id          - Обновить профиль
DELETE /api/parent/child/:id          - Удалить профиль

GET    /api/parent/child/:id/tasks   - Задачи ребенка
POST   /api/parent/child/:id/tasks   - Создать задачу
PUT    /api/parent/tasks/:id          - Обновить задачу
DELETE /api/parent/tasks/:id          - Удалить задачу

GET    /api/parent/child/:id/rules   - Правила
POST   /api/parent/child/:id/rules   - Создать правило

PUT    /api/parent/child/:id/settings - Настройки курса

GET    /api/parent/child/:id/stats   - Статистика
GET    /api/parent/child/:id/history - История операций

GET    /api/parent/subscription       - Подписка
POST   /api/parent/payment            - Создать платеж
```

### Ребенок:
```javascript
GET    /api/child/profile             - Профиль
POST   /api/child/tasks/:id/complete  - Выполнить задачу
GET    /api/child/stars               - Звезды
POST   /api/child/stars/convert       - Конвертация
GET    /api/child/piggy               - Копилка
POST   /api/child/diary               - Запись в дневник
GET    /api/child/wishlist            - Вишлист
```

### Администратор:
```javascript
GET    /api/admin/users               - Все пользователи
GET    /api/admin/stats               - Общая статистика
GET    /api/admin/subscriptions       - Все подписки
PUT    /api/admin/user/:id/role       - Изменить роль
DELETE /api/admin/user/:id            - Удалить пользователя
GET    /api/admin/analytics           - Аналитика
```

---

## 💳 ИНТЕГРАЦИЯ ПЛАТЕЖЕЙ (YooKassa)

### Backend:

```javascript
// backend/src/routes/payment.js
const express = require('express');
const router = express.Router();
const yookassa = require('yookassa');

const yooKassa = yookassa({
  shopId: process.env.YOOKASSA_SHOP_ID,
  secretKey: process.env.YOOKASSA_SECRET_KEY,
});

router.post('/create', authMiddleware, async (req, res) => {
  const { plan, amount } = req.body;
  const userId = req.user.id;

  const payment = await yooKassa.createPayment({
    amount: {
      value: amount.toFixed(2),
      currency: 'RUB',
    },
    confirmation: {
      type: 'redirect',
      return_url: `${process.env.FRONTEND_URL}/payment/success`,
    },
    description: `Подписка ${plan}`,
    metadata: {
      userId,
      plan,
    },
  });

  // Сохранить payment_id в БД
  await db.payments.create({
    userId,
    paymentId: payment.id,
    amount,
    plan,
    status: 'pending',
  });

  res.json({ paymentUrl: payment.confirmation.confirmation_url });
});

// Webhook от YooKassa
router.post('/webhook', async (req, res) => {
  const { event, object } = req.body;

  if (event === 'payment.succeeded') {
    const payment = await db.payments.findOne({
      where: { paymentId: object.id },
    });

    if (payment) {
      // Обновить подписку
      await db.subscriptions.update(
        {
          plan: payment.plan,
          status: 'active',
          startedAt: new Date(),
          expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000), // 30 дней
        },
        { where: { userId: payment.userId } }
      );

      await db.payments.update(
        { status: 'succeeded' },
        { where: { id: payment.id } }
      );
    }
  }

  res.status(200).send('OK');
});
```

---

## 🎨 АДАПТАЦИЯ ТЕКУЩЕГО UI

### 1. Страница входа/регистрации:

```html
<!-- frontend/src/pages/Login.jsx -->
<div class="login-page">
  <div class="login-card">
    <h1>Дневник успеха</h1>
    <form onSubmit={handleLogin}>
      <input type="email" placeholder="Email" />
      <input type="password" placeholder="Пароль" />
      <button type="submit">Войти</button>
    </form>
    <a href="/register">Регистрация</a>
  </div>
</div>
```

### 2. Панель родителя:

```html
<!-- frontend/src/pages/ParentDashboard.jsx -->
<div class="parent-dashboard">
  <header>
    <h1>Панель родителя</h1>
    <button onclick="logout()">Выход</button>
  </header>

  <div class="children-list">
    <h2>Мои дети</h2>
    {children.map(child => (
      <div class="child-card">
        <h3>{child.name}</h3>
        <button onclick={`openChildSettings(${child.id})`}>
          Настройки
        </button>
        <button onclick={`viewChildStats(${child.id})`}>
          Статистика
        </button>
      </div>
    ))}
    <button onclick="createChild()">+ Добавить ребенка</button>
  </div>

  <div class="subscription-section">
    <h2>Подписка</h2>
    <p>Текущий план: {subscription.plan}</p>
    <button onclick="upgradeSubscription()">
      Обновить подписку
    </button>
  </div>
</div>
```

### 3. Приложение ребенка (текущий UI):

```javascript
// frontend/src/pages/ChildApp.jsx
// Это ваш текущий index.html, но с API вместо localStorage

useEffect(() => {
  // Загрузка данных с сервера
  loadChildData();
}, []);

async function loadChildData() {
  try {
    const data = await api.getChildProfile();
    // Заполнить appData из ответа API
    setAppData(data);
  } catch (error) {
    console.error('Ошибка загрузки:', error);
  }
}

async function completeTask(taskId) {
  try {
    await api.completeTask(taskId);
    // Обновить UI
    loadChildData();
  } catch (error) {
    console.error('Ошибка:', error);
  }
}
```

---

## 🗄️ МИГРАЦИЯ ДАННЫХ

### Скрипт для переноса из localStorage в БД:

```javascript
// backend/src/scripts/migrate-localStorage.js
// Родитель загружает JSON из localStorage
// И отправляет на сервер

router.post('/migrate', authMiddleware, async (req, res) => {
  const { childId, localStorageData } = req.body;
  
  // Преобразовать данные из формата localStorage в формат БД
  const tasks = localStorageData.checklist.map(task => ({
    childId,
    text: task.text,
    stars: task.stars,
    completed: task.completed,
    date: new Date(),
  }));

  const stars = localStorageData.stars.history.map(star => ({
    childId,
    amount: star.amount,
    source: star.source,
    date: new Date(star.date),
  }));

  // Сохранить в БД
  await db.tasks.bulkCreate(tasks);
  await db.stars.bulkCreate(stars);
  // ... остальные данные

  res.json({ success: true });
});
```

---

## 🚀 ПОШАГОВЫЙ ПЛАН

### Неделя 1: Backend основа
- [ ] Настроить Node.js/Express проект
- [ ] Подключить PostgreSQL
- [ ] Создать модели (User, Child, Task, Star, etc.)
- [ ] Реализовать JWT аутентификацию
- [ ] Создать базовые API endpoints

### Неделя 2: Frontend основа
- [ ] Создать страницы входа/регистрации
- [ ] Интегрировать API клиент
- [ ] Создать панель родителя
- [ ] Адаптировать текущее приложение под API

### Неделя 3: Функционал
- [ ] Реализовать все CRUD операции
- [ ] Добавить проверку подписки
- [ ] Реализовать статистику
- [ ] Тестирование

### Неделя 4: Платежи
- [ ] Интегрировать YooKassa
- [ ] Создать страницу подписки
- [ ] Реализовать webhook
- [ ] Тестирование платежей

### Неделя 5: Админ-панель
- [ ] Создать админ-панель
- [ ] Реализовать аналитику
- [ ] Управление пользователями
- [ ] Дашборд с метриками

### Неделя 6: Полировка
- [ ] Исправление багов
- [ ] Оптимизация
- [ ] Документация
- [ ] Подготовка к запуску

---

## 📝 ЧЕКЛИСТ ПЕРЕХОДА

### Подготовка:
- [ ] Выбрать стек (Node.js или Python)
- [ ] Настроить базу данных
- [ ] Создать репозиторий для backend
- [ ] Настроить CI/CD

### Разработка:
- [ ] Реализовать аутентификацию
- [ ] Мигрировать функционал на API
- [ ] Создать интерфейсы для всех ролей
- [ ] Интегрировать платежи

### Тестирование:
- [ ] Протестировать все сценарии
- [ ] Проверить безопасность
- [ ] Нагрузочное тестирование
- [ ] Тестирование платежей

### Запуск:
- [ ] Деплой backend
- [ ] Деплой frontend
- [ ] Настройка домена
- [ ] SSL сертификат
- [ ] Мониторинг

---

## 💡 РЕКОМЕНДАЦИИ

1. **Начните с MVP:**
   - Только родитель и ребенок
   - Базовая подписка
   - Минимум функций

2. **Используйте готовые решения:**
   - Auth0 для аутентификации (опционально)
   - Stripe/YooKassa для платежей
   - Vercel для фронтенда
   - Railway для бэкенда

3. **Безопасность:**
   - HTTPS обязательно
   - Валидация всех данных
   - Rate limiting
   - Защита от SQL injection

4. **Масштабирование:**
   - Кеширование (Redis)
   - CDN для статики
   - Балансировка нагрузки
   - Мониторинг (Sentry, LogRocket)

---

Готов помочь с реализацией любого этапа! 🚀

