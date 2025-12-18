/**
 * Админ-панель
 * Согласно rules.md: production-ready, безопасность, обработка ошибок
 */

// Состояние админки
let adminState = {
  currentUser: null,
  currentPage: 'dashboard',
  usersPage: 0,
  childrenPage: 0,
  subscriptionsPage: 0,
  notificationsPage: 0,
  pageSize: 50
};

// Debounce для поиска
function debounceSearch(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// Инициализация админки
document.addEventListener('DOMContentLoaded', async () => {
  // Проверяем авторизацию
  const token = apiClient.getAccessToken();
  if (!token) {
    // Пробуем получить токен из localStorage (временное решение для админа)
    // В production должно быть через отдельную страницу входа
    const savedToken = localStorage.getItem('admin_token');
    if (savedToken) {
      apiClient.setAccessToken(savedToken);
    } else {
      window.location.href = '/';
      return;
    }
  }

  try {
    // Проверяем права администратора
    await checkAdminAccess();
    // Загружаем данные
    await loadAdminStats();
    // Показываем email пользователя
    showAdminUserInfo();
  } catch (error) {
    showAdminError('Ошибка доступа: ' + error.message);
    setTimeout(() => {
      window.location.href = '/';
    }, 2000);
  }
});

// Проверка прав администратора
async function checkAdminAccess() {
  try {
    // Получаем статистику - если успешно, значит есть права админа
    const stats = await apiClient.get('/admin/stats');
    return true;
  } catch (error) {
    if (error.message.includes('403') || error.message.includes('администратора')) {
      throw new Error('Требуются права администратора');
    }
    throw error;
  }
}

// Показать информацию о пользователе
async function showAdminUserInfo() {
  try {
    // Получаем текущего пользователя через /api/users/me
    const user = await apiClient.get('/users/me');
    document.getElementById('admin-user-email').textContent = user.email || 'Администратор';
  } catch (error) {
    console.error('Ошибка получения информации о пользователе:', error);
  }
}

// Переключение страниц
function showAdminPage(page) {
  // Скрываем все страницы
  document.querySelectorAll('.admin-page').forEach(p => p.classList.remove('active'));
  // Показываем выбранную
  document.getElementById(`admin-page-${page}`).classList.add('active');
  
  // Обновляем навигацию
  document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelector(`[data-page="${page}"]`).classList.add('active');
  
  adminState.currentPage = page;
  
  // Загружаем данные для страницы
  switch(page) {
    case 'dashboard':
      loadAdminStats();
      break;
    case 'users':
      loadUsers();
      break;
    case 'children':
      loadChildren();
      break;
    case 'subscriptions':
      loadSubscriptions();
      break;
    case 'notifications':
      loadNotifications();
      break;
  }
}

// Загрузка статистики
async function loadAdminStats() {
  try {
    showLoading('recent-users-tbody');
    showLoading('recent-subscriptions-tbody');
    
    const stats = await apiClient.get('/admin/stats');
    
    // Обновляем карточки статистики
    document.getElementById('stat-total-users').textContent = stats.total_users || 0;
    document.getElementById('stat-total-parents').textContent = stats.total_parents || 0;
    document.getElementById('stat-total-children').textContent = stats.total_children || 0;
    document.getElementById('stat-active-subscriptions').textContent = stats.active_subscriptions || 0;
    document.getElementById('stat-total-subscriptions').textContent = stats.total_subscriptions || 0;
    document.getElementById('stat-refund-requests').textContent = stats.refund_requests || 0;
    
    // Обновляем таблицы
    renderRecentUsers(stats.recent_users || []);
    renderRecentSubscriptions(stats.recent_subscriptions || []);
  } catch (error) {
    showAdminError('Ошибка загрузки статистики: ' + error.message);
    console.error('Ошибка загрузки статистики:', error);
  }
}

// Рендеринг последних пользователей
function renderRecentUsers(users) {
  const tbody = document.getElementById('recent-users-tbody');
  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = users.map(user => `
    <tr>
      <td>${escapeHtml(user.email)}</td>
      <td><span class="badge badge-${user.role}">${getRoleLabel(user.role)}</span></td>
      <td>${user.children_count || 0}</td>
      <td>${user.subscriptions_count || 0}</td>
      <td>${formatDate(user.created_at)}</td>
      <td>
        <button class="admin-action-btn" onclick="editUser(${user.id}, '${escapeHtml(user.email)}', '${user.role}')">✏️</button>
        <button class="admin-action-btn danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.email)}')">🗑️</button>
      </td>
    </tr>
  `).join('');
}

// Рендеринг последних подписок
function renderRecentSubscriptions(subscriptions) {
  const tbody = document.getElementById('recent-subscriptions-tbody');
  if (!subscriptions || subscriptions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = subscriptions.map(sub => `
    <tr>
      <td>${escapeHtml(sub.user_email)}</td>
      <td>${formatDate(sub.start_date)}</td>
      <td>${formatDate(sub.end_date)}</td>
      <td><span class="badge badge-${sub.is_active ? 'active' : 'inactive'}">${sub.is_active ? 'Активна' : 'Неактивна'}</span></td>
      <td>${sub.refund_requested ? '⚠️ Да' : 'Нет'}</td>
      <td>-</td>
    </tr>
  `).join('');
}

// Загрузка пользователей
async function loadUsers() {
  try {
    showLoading('users-tbody');
    
    const role = document.getElementById('users-role-filter').value;
    const search = document.getElementById('users-search').value;
    const skip = adminState.usersPage * adminState.pageSize;
    
    let url = `/admin/users?skip=${skip}&limit=${adminState.pageSize}`;
    if (role) url += `&role=${role}`;
    
    const users = await apiClient.get(url);
    
    // Фильтруем по поиску на клиенте (можно перенести на сервер)
    let filteredUsers = users;
    if (search) {
      filteredUsers = users.filter(u => u.email.toLowerCase().includes(search.toLowerCase()));
    }
    
    renderUsers(filteredUsers);
    updatePagination('users', users.length);
  } catch (error) {
    showAdminError('Ошибка загрузки пользователей: ' + error.message);
    console.error('Ошибка загрузки пользователей:', error);
  }
}

// Рендеринг пользователей
function renderUsers(users) {
  const tbody = document.getElementById('users-tbody');
  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = users.map(user => `
    <tr>
      <td>${user.id}</td>
      <td>${escapeHtml(user.email)}</td>
      <td><span class="badge badge-${user.role}">${getRoleLabel(user.role)}</span></td>
      <td>${user.children_count || 0}</td>
      <td>${user.subscriptions_count || 0}</td>
      <td>${formatDate(user.created_at)}</td>
      <td>
        <button class="admin-action-btn" onclick="editUser(${user.id}, '${escapeHtml(user.email)}', '${user.role}')">✏️</button>
        <button class="admin-action-btn danger" onclick="deleteUser(${user.id}, '${escapeHtml(user.email)}')">🗑️</button>
      </td>
    </tr>
  `).join('');
}

// Загрузка детей
async function loadChildren() {
  try {
    showLoading('children-tbody');
    
    const skip = adminState.childrenPage * adminState.pageSize;
    const children = await apiClient.get(`/admin/children?skip=${skip}&limit=${adminState.pageSize}`);
    
    renderChildren(children);
    updatePagination('children', children.length);
  } catch (error) {
    showAdminError('Ошибка загрузки детей: ' + error.message);
    console.error('Ошибка загрузки детей:', error);
  }
}

// Рендеринг детей
function renderChildren(children) {
  const tbody = document.getElementById('children-tbody');
  if (!children || children.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = children.map(child => `
    <tr>
      <td>${child.id}</td>
      <td>${escapeHtml(child.name)}</td>
      <td>${escapeHtml(child.parent_email)}</td>
      <td>${getGenderLabel(child.gender)}</td>
      <td>${child.tasks_count || 0}</td>
      <td>${child.stars_total || 0}</td>
      <td>${formatDate(child.created_at)}</td>
    </tr>
  `).join('');
}

// Загрузка подписок
async function loadSubscriptions() {
  try {
    showLoading('subscriptions-tbody');
    
    const activeOnly = document.getElementById('subscriptions-active-only').checked;
    const skip = adminState.subscriptionsPage * adminState.pageSize;
    
    let url = `/admin/subscriptions?skip=${skip}&limit=${adminState.pageSize}`;
    if (activeOnly) url += '&active_only=true';
    
    const subscriptions = await apiClient.get(url);
    
    renderSubscriptions(subscriptions);
    updatePagination('subscriptions', subscriptions.length);
  } catch (error) {
    showAdminError('Ошибка загрузки подписок: ' + error.message);
    console.error('Ошибка загрузки подписок:', error);
  }
}

// Рендеринг подписок
function renderSubscriptions(subscriptions) {
  const tbody = document.getElementById('subscriptions-tbody');
  if (!subscriptions || subscriptions.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = subscriptions.map(sub => `
    <tr>
      <td>${sub.id}</td>
      <td>${escapeHtml(sub.user_email)}</td>
      <td>${formatDate(sub.start_date)}</td>
      <td>${formatDate(sub.end_date)}</td>
      <td><span class="badge badge-${sub.is_active ? 'active' : 'inactive'}">${sub.is_active ? 'Активна' : 'Неактивна'}</span></td>
      <td>${sub.refund_requested ? '⚠️ Да' : 'Нет'}</td>
      <td>${formatDate(sub.created_at)}</td>
    </tr>
  `).join('');
}

// Загрузка уведомлений
async function loadNotifications() {
  try {
    showLoading('notifications-tbody');
    
    const type = document.getElementById('notifications-type-filter').value;
    const skip = adminState.notificationsPage * adminState.pageSize;
    
    let url = `/admin/notifications?skip=${skip}&limit=${adminState.pageSize}`;
    if (type) url += `&type=${type}`;
    
    const notifications = await apiClient.get(url);
    
    renderNotifications(notifications);
    updatePagination('notifications', notifications.length);
  } catch (error) {
    showAdminError('Ошибка загрузки уведомлений: ' + error.message);
    console.error('Ошибка загрузки уведомлений:', error);
  }
}

// Рендеринг уведомлений
function renderNotifications(notifications) {
  const tbody = document.getElementById('notifications-tbody');
  if (!notifications || notifications.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = notifications.map(notif => `
    <tr>
      <td>${notif.id}</td>
      <td>${escapeHtml(notif.user_email)}</td>
      <td><span class="badge badge-${notif.type}">${getNotificationTypeLabel(notif.type)}</span></td>
      <td class="notification-message">${escapeHtml(notif.message)}</td>
      <td><span class="badge badge-${notif.status}">${getNotificationStatusLabel(notif.status)}</span></td>
      <td>${formatDate(notif.created_at)}</td>
    </tr>
  `).join('');
}

// Редактирование пользователя
function editUser(id, email, role) {
  document.getElementById('edit-user-id').value = id;
  document.getElementById('edit-user-email').value = email;
  document.getElementById('edit-user-role').value = role;
  document.getElementById('edit-user-modal').style.display = 'flex';
}

// Закрытие модального окна
function closeEditUserModal() {
  document.getElementById('edit-user-modal').style.display = 'none';
}

// Сохранение пользователя
async function saveUser(event) {
  event.preventDefault();
  
  const id = document.getElementById('edit-user-id').value;
  const email = document.getElementById('edit-user-email').value;
  const role = document.getElementById('edit-user-role').value;
  
  try {
    await apiClient.put(`/admin/users/${id}`, { email, role });
    showAdminSuccess('Пользователь обновлён');
    closeEditUserModal();
    loadUsers();
    if (adminState.currentPage === 'dashboard') {
      loadAdminStats();
    }
  } catch (error) {
    showAdminError('Ошибка обновления пользователя: ' + error.message);
  }
}

// Удаление пользователя
async function deleteUser(id, email) {
  if (!confirm(`Вы уверены, что хотите удалить пользователя ${email}? Это действие нельзя отменить.`)) {
    return;
  }
  
  try {
    await apiClient.delete(`/admin/users/${id}`);
    showAdminSuccess('Пользователь удалён');
    loadUsers();
    if (adminState.currentPage === 'dashboard') {
      loadAdminStats();
    }
  } catch (error) {
    showAdminError('Ошибка удаления пользователя: ' + error.message);
  }
}

// Пагинация
function changeUsersPage(delta) {
  adminState.usersPage = Math.max(0, adminState.usersPage + delta);
  loadUsers();
}

function changeChildrenPage(delta) {
  adminState.childrenPage = Math.max(0, adminState.childrenPage + delta);
  loadChildren();
}

function changeSubscriptionsPage(delta) {
  adminState.subscriptionsPage = Math.max(0, adminState.subscriptionsPage + delta);
  loadSubscriptions();
}

function changeNotificationsPage(delta) {
  adminState.notificationsPage = Math.max(0, adminState.notificationsPage + delta);
  loadNotifications();
}

function updatePagination(type, itemsCount) {
  const hasMore = itemsCount === adminState.pageSize;
  const pageInfo = document.getElementById(`${type}-page-info`);
  if (pageInfo) {
    pageInfo.textContent = `Страница ${adminState[`${type}Page`] + 1}${hasMore ? ' (есть ещё)' : ''}`;
  }
}

// Выход
async function adminLogout() {
  try {
    await apiClient.post('/auth/logout', {});
  } catch (error) {
    console.error('Ошибка выхода:', error);
  }
  localStorage.removeItem('admin_token');
  apiClient.setAccessToken(null);
  window.location.href = '/';
}

// Утилиты
function showLoading(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (tbody) {
    tbody.innerHTML = '<tr><td colspan="10" class="loading">Загрузка...</td></tr>';
  }
}

function showAdminError(message) {
  const el = document.getElementById('admin-error-message');
  el.textContent = message;
  el.style.display = 'block';
  setTimeout(() => {
    el.style.display = 'none';
  }, 5000);
}

function showAdminSuccess(message) {
  const el = document.getElementById('admin-success-message');
  el.textContent = message;
  el.style.display = 'block';
  setTimeout(() => {
    el.style.display = 'none';
  }, 3000);
}

function formatDate(dateString) {
  if (!dateString) return '-';
  const date = new Date(dateString);
  return date.toLocaleDateString('ru-RU') + ' ' + date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

function getRoleLabel(role) {
  const labels = {
    'parent': 'Родитель',
    'child': 'Ребёнок',
    'admin': 'Администратор'
  };
  return labels[role] || role;
}

function getGenderLabel(gender) {
  const labels = {
    'girl': '👧 Девочка',
    'boy': '👦 Мальчик',
    'none': 'Не указан'
  };
  return labels[gender] || gender;
}

function getNotificationTypeLabel(type) {
  const labels = {
    'subscription': 'Подписка',
    'refund': 'Возврат',
    'complaint': 'Жалоба',
    'consent': 'Согласие',
    'system': 'Система'
  };
  return labels[type] || type;
}

function getNotificationStatusLabel(status) {
  const labels = {
    'pending': 'Ожидает',
    'sent': 'Отправлено',
    'read': 'Прочитано',
    'failed': 'Ошибка'
  };
  return labels[status] || status;
}

