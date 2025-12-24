/**
 * Маршрут /staff/login и /staff/dashboard
 * Staff панель для операторов, поддержки и администраторов
 */

/**
 * Маршрут /staff/login
 * Страница входа для staff пользователей
 */
async function handleStaffLoginRoute() {
  console.log('🔐 Загрузка страницы входа staff...');
  
  // Редирект на staff.html
  window.location.href = '/staff.html';
}

/**
 * Маршрут /staff/dashboard
 * Dashboard для staff пользователей
 */
async function handleStaffDashboardRoute() {
  console.log('📊 Загрузка staff dashboard...');
  
  // ЗАЩИТА МАРШРУТА: проверяем роль через /api/staff/me
  const token = apiClient.getAccessToken();
  if (!token) {
    // Нет токена - редирект на login
    router.navigate('/staff/login', true);
    return;
  }
  
  try {
    const me = await apiClient.get('/staff/me');
    
    // Проверка, что это staff пользователь
    if (!me.is_staff) {
      console.warn('⚠️ Доступ запрещён: не staff пользователь, редирект на /');
      router.navigate('/', true);
      return;
    }
    
    // Показываем staff dashboard
    const staffContent = document.getElementById('staff-content');
    const mainContent = document.getElementById('app-content');
    const adminContent = document.getElementById('admin-content');
    const parentContent = document.getElementById('parent-content');
    const childContent = document.getElementById('child-content');
    
    // Скрываем другие контейнеры
    if (mainContent) mainContent.style.display = 'none';
    if (adminContent) adminContent.style.display = 'none';
    if (parentContent) parentContent.style.display = 'none';
    if (childContent) childContent.style.display = 'none';
    
    // Показываем staff контент
    if (staffContent) {
      staffContent.style.display = 'block';
    } else {
      // Если контейнера нет, создаём базовый
      createStaffDashboard(me);
    }
    
    // Инициализируем staff dashboard
    if (typeof initStaffDashboard === 'function') {
      await initStaffDashboard(me);
    }
    
  } catch (e) {
    // 401 или другая ошибка - пробуем обновить токен
    const refreshed = await apiClient.refreshToken();
    if (refreshed) {
      apiClient.setAccessToken(refreshed);
      // Повторяем проверку
      return handleStaffDashboardRoute();
    }
    // Если не удалось обновить - редирект на login
    console.error('❌ Ошибка проверки авторизации:', e);
    router.navigate('/staff/login', true);
  }
}

function createStaffDashboard(staffUser) {
  const body = document.body;
  
  // Создаём контейнер для staff dashboard
  const staffContent = document.createElement('div');
  staffContent.id = 'staff-content';
  staffContent.innerHTML = `
    <div class="staff-dashboard">
      <header class="staff-header">
        <h1>Staff Dashboard</h1>
        <div class="staff-user-info">
          <span>${staffUser.email}</span>
          <span class="staff-role">${staffUser.role}</span>
          <button onclick="handleStaffLogout()">Выход</button>
        </div>
      </header>
      <nav class="staff-nav">
        <button onclick="showStaffPage('stats')">Статистика</button>
        <button onclick="showStaffPage('users')">Пользователи</button>
        <button onclick="showStaffPage('children')">Дети</button>
        ${staffUser.role === 'admin' || staffUser.role === 'support' ? '<button onclick="showStaffPage(\'subscriptions\')">Подписки</button>' : ''}
        <button onclick="showStaffPage('notifications')">Уведомления</button>
      </nav>
      <main class="staff-main">
        <div id="staff-loading">Загрузка...</div>
        <div id="staff-stats-page" class="staff-page" style="display: none;"></div>
        <div id="staff-users-page" class="staff-page" style="display: none;"></div>
        <div id="staff-children-page" class="staff-page" style="display: none;"></div>
        <div id="staff-subscriptions-page" class="staff-page" style="display: none;"></div>
        <div id="staff-notifications-page" class="staff-page" style="display: none;"></div>
      </main>
    </div>
  `;
  
  body.appendChild(staffContent);
}

async function handleStaffLogout() {
  try {
    await apiClient.logout();
    apiClient.setAccessToken(null);
    router.navigate('/staff/login', true);
  } catch (e) {
    console.error('Ошибка выхода:', e);
    apiClient.setAccessToken(null);
    router.navigate('/staff/login', true);
  }
}

function showStaffPage(page) {
  document.querySelectorAll('.staff-page').forEach(p => p.style.display = 'none');
  const pageEl = document.getElementById(`staff-${page}-page`);
  if (pageEl) {
    pageEl.style.display = 'block';
    loadStaffPageData(page);
  }
}

async function loadStaffPageData(page) {
  const loadingEl = document.getElementById('staff-loading');
  if (loadingEl) loadingEl.style.display = 'block';
  
  try {
    switch (page) {
      case 'stats':
        await loadStaffStats();
        break;
      case 'users':
        await loadStaffUsers();
        break;
      case 'children':
        await loadStaffChildren();
        break;
      case 'subscriptions':
        await loadStaffSubscriptions();
        break;
      case 'notifications':
        await loadStaffNotifications();
        break;
    }
  } catch (e) {
    console.error(`Ошибка загрузки ${page}:`, e);
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

async function loadStaffStats() {
  const stats = await apiClient.get('/staff/stats');
  const pageEl = document.getElementById('staff-stats-page');
  if (pageEl) {
    pageEl.innerHTML = `
      <h2>Статистика</h2>
      <div class="stats-grid">
        <div class="stat-card">
          <h3>Пользователи</h3>
          <p>${stats.total_users}</p>
        </div>
        <div class="stat-card">
          <h3>Родители</h3>
          <p>${stats.total_parents}</p>
        </div>
        <div class="stat-card">
          <h3>Дети</h3>
          <p>${stats.total_children}</p>
        </div>
        <div class="stat-card">
          <h3>Активные подписки</h3>
          <p>${stats.active_subscriptions}</p>
        </div>
        <div class="stat-card">
          <h3>Задачи</h3>
          <p>${stats.total_tasks}</p>
        </div>
        <div class="stat-card">
          <h3>Звёзды</h3>
          <p>${stats.total_stars}</p>
        </div>
      </div>
    `;
  }
}

async function loadStaffUsers() {
  const users = await apiClient.get('/staff/users');
  const pageEl = document.getElementById('staff-users-page');
  if (pageEl) {
    pageEl.innerHTML = `
      <h2>Пользователи</h2>
      <table class="staff-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Email</th>
            <th>Телефон</th>
            <th>Роль</th>
          </tr>
        </thead>
        <tbody>
          ${users.map(u => `
            <tr>
              <td>${u.id}</td>
              <td>${u.name || '-'}</td>
              <td>${u.email || '-'}</td>
              <td>${u.phone || '-'}</td>
              <td>${u.role}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }
}

async function loadStaffChildren() {
  const children = await apiClient.get('/staff/children');
  const pageEl = document.getElementById('staff-children-page');
  if (pageEl) {
    pageEl.innerHTML = `
      <h2>Дети</h2>
      <table class="staff-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Имя</th>
            <th>Родитель ID</th>
          </tr>
        </thead>
        <tbody>
          ${children.map(c => `
            <tr>
              <td>${c.id}</td>
              <td>${c.name}</td>
              <td>${c.user_id}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }
}

async function loadStaffSubscriptions() {
  const subscriptions = await apiClient.get('/staff/subscriptions');
  const pageEl = document.getElementById('staff-subscriptions-page');
  if (pageEl) {
    pageEl.innerHTML = `
      <h2>Подписки</h2>
      <table class="staff-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пользователь ID</th>
            <th>Активна</th>
          </tr>
        </thead>
        <tbody>
          ${subscriptions.map(s => `
            <tr>
              <td>${s.id}</td>
              <td>${s.user_id}</td>
              <td>${s.is_active ? 'Да' : 'Нет'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }
}

async function loadStaffNotifications() {
  const notifications = await apiClient.get('/staff/notifications');
  const pageEl = document.getElementById('staff-notifications-page');
  if (pageEl) {
    pageEl.innerHTML = `
      <h2>Уведомления</h2>
      <table class="staff-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Пользователь ID</th>
            <th>Тип</th>
            <th>Сообщение</th>
          </tr>
        </thead>
        <tbody>
          ${notifications.map(n => `
            <tr>
              <td>${n.id}</td>
              <td>${n.user_id}</td>
              <td>${n.type}</td>
              <td>${n.message}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
    `;
  }
}

window.handleStaffLoginRoute = handleStaffLoginRoute;
window.handleStaffDashboardRoute = handleStaffDashboardRoute;
window.handleStaffLogout = handleStaffLogout;
window.showStaffPage = showStaffPage;


