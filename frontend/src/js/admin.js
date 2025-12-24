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

// Функции для входа
function showAdminLogin() {
  console.log('🔐 Показываем окно входа...');
  
  // ВАЖНО: Показываем контейнер admin-content, чтобы форма входа была видна
  const adminContent = document.getElementById('admin-content');
  if (adminContent) {
    adminContent.style.display = 'block';
    console.log('✅ Контейнер admin-content показан');
  }
  
  // Скрываем админку (header, nav, main)
  const adminHeader = document.querySelector('.admin-header');
  const adminNav = document.querySelector('.admin-nav');
  const adminMain = document.querySelector('.admin-main');
  if (adminHeader) adminHeader.style.display = 'none';
  if (adminNav) adminNav.style.display = 'none';
  if (adminMain) adminMain.style.display = 'none';
  
  // Показываем матричный фон
  const matrixBg = document.getElementById('matrix-background');
  if (matrixBg) {
    matrixBg.style.display = 'block';
    matrixBg.style.visibility = 'visible';
    console.log('✅ Матричный фон показан');
    // Запускаем матричный эффект
    startMatrixEffect();
  } else {
    console.error('❌ Элемент matrix-background не найден!');
  }
  
  // Показываем модальное окно
  const modal = document.getElementById('admin-login-modal');
  if (modal) {
    modal.style.display = 'flex';
    modal.style.visibility = 'visible';
    modal.style.zIndex = '10000'; // Убеждаемся, что модалка поверх всего
    console.log('✅ Модальное окно показано');
  } else {
    console.error('❌ Элемент admin-login-modal не найден!');
  }
  
  // Скрываем индикатор загрузки
  const loadingEl = document.getElementById('admin-loading');
  if (loadingEl) {
    loadingEl.style.display = 'none';
  }
}

// Матричный эффект
function startMatrixEffect() {
  const matrixBg = document.getElementById('matrix-background');
  if (!matrixBg) {
    console.error('❌ Элемент matrix-background не найден для матричного эффекта');
    return;
  }
  
  console.log('🎬 Запуск матричного эффекта...');
  
  // Очищаем предыдущие колонки
  matrixBg.innerHTML = '';
  
  const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
  const columns = Math.floor(window.innerWidth / 20);
  
  console.log(`📊 Создаем ${columns} колонок для матричного эффекта`);
  
  for (let i = 0; i < columns; i++) {
    const column = document.createElement('div');
    column.className = 'matrix-column';
    column.style.left = (i * 20) + 'px';
    column.style.animationDuration = (Math.random() * 3 + 2) + 's';
    column.style.animationDelay = Math.random() * 2 + 's';
    
    // Генерируем случайные символы
    let text = '';
    for (let j = 0; j < 50; j++) {
      text += chars[Math.floor(Math.random() * chars.length)] + '<br>';
    }
    column.innerHTML = text;
    
    matrixBg.appendChild(column);
  }
  
  console.log('✅ Матричный эффект запущен');
}

function closeAdminLogin() {
  const modal = document.getElementById('admin-login-modal');
  if (modal) {
    modal.style.display = 'none';
  }
}

async function handleAdminLogin(event) {
  event.preventDefault();
  const phone = document.getElementById('admin-login-phone').value;
  const password = document.getElementById('admin-login-password').value;
  const errorEl = document.getElementById('admin-login-error');
  
  if (errorEl) {
    errorEl.style.display = 'none';
    errorEl.textContent = '';
  }
  
  try {
    const response = await fetch('/api/auth/admin-login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ phone, password }),
    });
    
    if (!response.ok) {
      const data = await response.json().catch(() => ({ detail: 'Ошибка входа' }));
      throw new Error(data.detail || 'Неверный телефон или пароль');
    }
    
    const data = await response.json();
    
    // Сохраняем токен
    console.log('📥 Ответ от сервера:', { 
      has_token: !!data.access_token, 
      token_preview: data.access_token ? data.access_token.substring(0, 30) + '...' : 'нет',
      user: data.user 
    });
    
    if (data.access_token && data.access_token.trim()) {
      const token = data.access_token.trim();
      // Согласно rules.md: access token хранится только в памяти
      apiClient.setAccessToken(token);
      // localStorage.setItem('admin_token', token); // Удалено: токены не хранятся в localStorage
      console.log('✅ Токен сохранен в apiClient (память)');
    } else {
      console.error('❌ Токен не получен в ответе:', data);
      throw new Error('Токен не получен от сервера');
    }
    
    // Сохраняем информацию о пользователе
    adminState.currentUser = data.user;
    
    // Закрываем модальное окно
    closeAdminLogin();
    
    // Скрываем матричный фон
    const matrixBg = document.getElementById('matrix-background');
    if (matrixBg) {
      matrixBg.style.display = 'none';
    }
    
    // Показываем основной контент админки
    const adminHeader = document.querySelector('.admin-header');
    const adminNav = document.querySelector('.admin-nav');
    const adminMain = document.querySelector('.admin-main');
    if (adminHeader) adminHeader.style.display = 'block';
    if (adminNav) adminNav.style.display = 'block';
    if (adminMain) adminMain.style.display = 'block';
    
    // Обновляем информацию о пользователе в шапке
    const userPhoneEl = document.getElementById('admin-user-phone');
    if (userPhoneEl && data.user) {
      userPhoneEl.textContent = data.user.phone || data.user.email || 'Администратор';
    }
    
    // Загружаем данные
    await loadAdminStats();
    
  } catch (error) {
    if (errorEl) {
      errorEl.textContent = error.message || 'Ошибка входа. Проверьте телефон и пароль.';
      errorEl.style.display = 'block';
    }
    console.error('Ошибка входа:', error);
  }
}

// Функция инициализации админки (для использования в роутере)
async function initAdminPanel() {
  console.log('🔐 Инициализация админ-панели...');
  
  // СНАЧАЛА СКРЫВАЕМ АДМИНКУ - показываем только после успешной авторизации
  const adminHeader = document.querySelector('.admin-header');
  const adminNav = document.querySelector('.admin-nav');
  const adminMain = document.querySelector('.admin-main');
  if (adminHeader) adminHeader.style.display = 'none';
  if (adminNav) adminNav.style.display = 'none';
  if (adminMain) adminMain.style.display = 'none';
  
  // Показываем индикатор загрузки
  const loadingEl = document.getElementById('admin-loading');
  if (loadingEl) {
    loadingEl.style.display = 'flex';
  }
  
  // Проверяем токен
  let token = apiClient.getAccessToken();
  if (!token || !token.trim()) {
    console.log('❌ Токен отсутствует, пробуем обновить через refresh');
    // Пробуем обновить через refresh token
    const retryToken = await apiClient.refreshToken();
    if (retryToken && retryToken.trim()) {
      apiClient.setAccessToken(retryToken);
      token = retryToken;
      console.log('✅ Токен восстановлен через refresh');
    } else {
      // Нет токена - показываем форму входа и скрываем админку
      if (loadingEl) loadingEl.style.display = 'none';
      showAdminLogin();
      return;
    }
  }
  
  if (token && token.trim()) {
    console.log('✅ Токен найден:', token.substring(0, 30) + '...');
    // Проверяем права администратора
    try {
      await checkAdminAccess();
      console.log('✅ Права администратора подтверждены');
      
      // Загружаем данные
      await loadAdminStats();
      
      // ТОЛЬКО ПОСЛЕ УСПЕШНОЙ ПРОВЕРКИ показываем админку
      if (adminHeader) adminHeader.style.display = 'block';
      if (adminNav) adminNav.style.display = 'block';
      if (adminMain) adminMain.style.display = 'block';
      if (loadingEl) loadingEl.style.display = 'none';
      
      // Скрываем матричный фон и форму входа
      const matrixBg = document.getElementById('matrix-background');
      if (matrixBg) {
        matrixBg.style.display = 'none';
      }
      const loginModal = document.getElementById('admin-login-modal');
      if (loginModal) {
        loginModal.style.display = 'none';
      }
    } catch (error) {
      console.error('❌ Ошибка проверки прав или загрузки данных:', error);
      // При ошибке скрываем админку и показываем форму входа
      if (adminHeader) adminHeader.style.display = 'none';
      if (adminNav) adminNav.style.display = 'none';
      if (adminMain) adminMain.style.display = 'none';
      if (loadingEl) loadingEl.style.display = 'none';
      showAdminLogin();
    }
  } else {
    // Нет токена - скрываем админку и показываем форму входа
    if (adminHeader) adminHeader.style.display = 'none';
    if (adminNav) adminNav.style.display = 'none';
    if (adminMain) adminMain.style.display = 'none';
    if (loadingEl) loadingEl.style.display = 'none';
    showAdminLogin();
  }
}

// Экспортируем функцию для использования в роутере
window.initAdminPanel = initAdminPanel;

// Инициализация админки при загрузке страницы (для прямого доступа к admin.html)
document.addEventListener('DOMContentLoaded', async () => {
  // Проверяем, что мы на странице админки (только через класс body)
  const isAdminPage = document.body.classList.contains('admin-body');
  
  if (!isAdminPage) {
    // Это не админ-страница, не инициализируем админку
    return;
  }
  
  // Если это админ-страница и есть контейнер admin-content, используем функцию инициализации
  if (adminContent) {
    await initAdminPanel();
    return;
  }

  // Показываем инструкцию если нет токена
  const loadingEl = document.getElementById('admin-loading');
  
  // ВАЖНО: Восстанавливаем токен из localStorage ПЕРЕД проверкой
  // Пробуем получить токен из localStorage (временное решение для админа)
  console.log('🔍 Проверка localStorage...');
  // Согласно rules.md: токены не хранятся в localStorage
  // Проверяем только токен в памяти
  const savedToken = apiClient.getAccessToken();
  console.log('📦 Токен в памяти:', savedToken ? savedToken.substring(0, 30) + '...' : 'null');
  
  if (savedToken && savedToken.trim()) {
    console.log('✅ Токен найден в памяти');
  } else {
    console.log('❌ Токен не найден в localStorage или пустой');
    // Проверяем все ключи в localStorage
    console.log('📋 Все ключи в localStorage:', Object.keys(localStorage));
  }
  
  // Проверяем авторизацию
  let token = apiClient.getAccessToken();
  if (!token || !token.trim()) {
    console.log('❌ Токен отсутствует, показываем форму входа');
    // Пробуем обновить через refresh token
    const retryToken = await apiClient.refreshToken();
    if (retryToken && retryToken.trim()) {
      apiClient.setAccessToken(retryToken);
      token = retryToken;
      console.log('✅ Токен восстановлен через refresh');
    } else {
      // Нет токена - показываем форму входа
      showAdminLogin();
      return;
    }
  }
  
  if (token && token.trim()) {
    console.log('✅ Токен найден:', token.substring(0, 30) + '...');
    // Проверяем, что токен валиден, пытаясь загрузить данные
    try {
      await loadAdminStats();
      // Если успешно - показываем админку
      const adminHeader = document.querySelector('.admin-header');
      const adminNav = document.querySelector('.admin-nav');
      const adminMain = document.querySelector('.admin-main');
      if (adminHeader) adminHeader.style.display = 'block';
      if (adminNav) adminNav.style.display = 'block';
      if (adminMain) adminMain.style.display = 'block';
      if (loadingEl) loadingEl.style.display = 'none';
    } catch (error) {
      console.error('❌ Ошибка загрузки данных, показываем форму входа:', error);
      showAdminLogin();
    }
  } else {
    showAdminLogin();
  }
  
  if (!token || !token.trim()) {
    // Если нет токена, показываем окно входа
    console.log('🚪 Нет токена, показываем окно входа');
    
    // Скрываем индикатор загрузки
    if (loadingEl) {
      loadingEl.style.display = 'none';
    }
    
    // Скрываем основной контент админки
    const adminHeader = document.querySelector('.admin-header');
    const adminNav = document.querySelector('.admin-nav');
    const adminMain = document.querySelector('.admin-main');
    if (adminHeader) adminHeader.style.display = 'none';
    if (adminNav) adminNav.style.display = 'none';
    if (adminMain) adminMain.style.display = 'none';
    
    // Показываем окно входа (внутри функции уже показывается матричный фон)
    showAdminLogin();
    return;
  }
  
  console.log('🔐 Токен найден, проверяем права доступа...');
  
  // ВАЖНО: Сначала проверяем права администратора, ПОТОМ показываем админку
  try {
    // Проверяем права администратора ПЕРЕД показом админки
    await checkAdminAccess();
    console.log('✅ Права администратора подтверждены');
    
    // Только после успешной проверки показываем админку
    const matrixBg = document.getElementById('matrix-background');
    if (matrixBg) {
      matrixBg.style.display = 'none';
    }
    
    // Показываем основной контент админки
    const adminHeader = document.querySelector('.admin-header');
    const adminNav = document.querySelector('.admin-nav');
    const adminMain = document.querySelector('.admin-main');
    if (adminHeader) adminHeader.style.display = 'block';
    if (adminNav) adminNav.style.display = 'block';
    if (adminMain) adminMain.style.display = 'block';
    
    // Скрываем индикатор загрузки
    const loadingEl = document.getElementById('admin-loading');
    if (loadingEl) {
      loadingEl.style.display = 'none';
    }
    
    // Загружаем данные
    await loadAdminStats();
    // Показываем email пользователя
    showAdminUserInfo();
  } catch (error) {
    console.error('❌ Ошибка доступа к админке:', error);
    const loadingEl = document.getElementById('admin-loading');
    if (loadingEl) {
      loadingEl.style.display = 'none';
    }
    
    // ВАЖНО: При ЛЮБОЙ ошибке checkAdminAccess скрываем админку и показываем окно входа
    // Это ошибка авторизации/доступа, поэтому всегда показываем окно входа
    console.log('🚪 Ошибка доступа, скрываем админку и показываем окно входа');
    
    // Скрываем весь контент админки
    const adminHeader = document.querySelector('.admin-header');
    const adminNav = document.querySelector('.admin-nav');
    const adminMain = document.querySelector('.admin-main');
    if (adminHeader) adminHeader.style.display = 'none';
    if (adminNav) adminNav.style.display = 'none';
    if (adminMain) adminMain.style.display = 'none';
    
    // Очищаем токен
    apiClient.setAccessToken(null);
    
    // Показываем окно входа
    showAdminLogin();
    return;
  }
});

// Проверка прав администратора
async function checkAdminAccess() {
  try {
    // Получаем статистику - если успешно, значит есть права админа
    const stats = await apiClient.get('/admin/stats');
    return true;
  } catch (error) {
    console.error('❌ Ошибка проверки прав администратора:', error);
    
    // Если токен не предоставлен или истек - показываем окно входа
    if (error.message.includes('401') || 
        error.message.includes('Токен не предоставлен') || 
        error.message.includes('Недействительный') ||
        error.message.includes('истекший токен')) {
      // Скрываем админку и показываем окно входа
      const adminHeader = document.querySelector('.admin-header');
      const adminNav = document.querySelector('.admin-nav');
      const adminMain = document.querySelector('.admin-main');
      if (adminHeader) adminHeader.style.display = 'none';
      if (adminNav) adminNav.style.display = 'none';
      if (adminMain) adminMain.style.display = 'none';
      
      showAdminLogin();
      throw new Error('Требуется авторизация. Пожалуйста, войдите в систему.');
    }
    
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
    const identifier = user.name || user.phone || user.email || 'Администратор';
    document.getElementById('admin-user-phone').textContent = identifier;
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
    
    const stats = await apiClient.getAdminStats();
    
    console.log('📊 Статистика загружена:', stats);
    console.log('👥 Последние пользователи:', stats.recent_users);
    
    // Обновляем карточки статистики
    document.getElementById('stat-total-users').textContent = stats.total_users || 0;
    document.getElementById('stat-total-parents').textContent = stats.total_parents || 0;
    document.getElementById('stat-total-children').textContent = stats.total_children || 0;
    document.getElementById('stat-active-subscriptions').textContent = stats.active_subscriptions || 0;
    document.getElementById('stat-total-subscriptions').textContent = stats.total_subscriptions || 0;
    document.getElementById('stat-refund-requests').textContent = stats.refund_requests || 0;
    
    // Обновляем таблицы
    const recentUsers = stats.recent_users || [];
    console.log(`✅ Отображаем ${recentUsers.length} пользователей в таблице`);
    renderRecentUsers(recentUsers);
    renderRecentSubscriptions(stats.recent_subscriptions || []);
  } catch (error) {
    const errorMessage = error.message || 'Неизвестная ошибка';
    
    // ВАЖНО: Если ошибка авторизации - скрываем админку и показываем окно входа
    if (errorMessage.includes('401') || 
        errorMessage.includes('403') || 
        errorMessage.includes('Требуется авторизация') ||
        errorMessage.includes('Токен не предоставлен') ||
        errorMessage.includes('Недействительный') ||
        errorMessage.includes('истекший токен')) {
      console.log('🚪 Ошибка авторизации при загрузке статистики, показываем окно входа');
      // Скрываем админку
      const adminHeader = document.querySelector('.admin-header');
      const adminNav = document.querySelector('.admin-nav');
      const adminMain = document.querySelector('.admin-main');
      if (adminHeader) adminHeader.style.display = 'none';
      if (adminNav) adminNav.style.display = 'none';
      if (adminMain) adminMain.style.display = 'none';
      // Очищаем токен
      apiClient.setAccessToken(null);
      // Показываем окно входа
      showAdminLogin();
      return;
    }
    
    // Для ошибок БД просто показываем нули
    if (errorMessage.includes('500') || errorMessage.includes('503') || errorMessage.includes('недоступн')) {
      console.warn('⚠️ База данных недоступна. Показываем нулевую статистику.');
      // Показываем нулевую статистику
      document.getElementById('total-users').textContent = '0';
      document.getElementById('total-parents').textContent = '0';
      document.getElementById('total-children').textContent = '0';
      document.getElementById('active-subscriptions').textContent = '0';
      document.getElementById('total-subscriptions').textContent = '0';
      document.getElementById('refund-requests').textContent = '0';
      renderRecentUsers([]);
      renderRecentSubscriptions([]);
      return;
    }
    
    showAdminError('Ошибка загрузки статистики: ' + errorMessage);
    console.error('Ошибка загрузки статистики:', error);
  }
}

// Рендеринг последних пользователей
function renderRecentUsers(users) {
  const tbody = document.getElementById('recent-users-tbody');
  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = users.map(user => {
    const name = user.name ? escapeHtml(user.name) : '-';
    const phone = user.phone ? escapeHtml(user.phone) : '-';
    const parentId = user.parent_id ? user.parent_id : '-';
    const updatedAt = user.updated_at ? formatDate(user.updated_at) : '-';
    return `
    <tr>
      <td><strong>${user.id}</strong></td>
      <td><strong>${name}</strong></td>
      <td>${phone}</td>
      <td><span class="badge badge-${user.role}">${getRoleLabel(user.role)}</span></td>
      <td>${parentId}</td>
      <td>${user.children_count || 0}</td>
      <td>${user.subscriptions_count || 0}</td>
      <td>${formatDate(user.created_at)}</td>
      <td>${updatedAt}</td>
      <td>
        <button class="admin-action-btn" onclick="editUser(${user.id}, ${JSON.stringify(user.name || '')}, ${JSON.stringify(user.phone || '')}, ${JSON.stringify(user.role)}, ${user.parent_id || 'null'})">✏️</button>
        <button class="admin-action-btn danger" onclick="deleteUser(${user.id}, ${JSON.stringify(user.name || user.phone || 'пользователь')})">🗑️</button>
      </td>
    </tr>
    `;
  }).join('');
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
    
    const users = await apiClient.getAdminUsers(skip, adminState.pageSize, role);
    
    // Фильтруем по поиску на клиенте (можно перенести на сервер)
    let filteredUsers = users;
    if (search) {
      filteredUsers = users.filter(u => {
    const nameMatch = u.name && u.name.toLowerCase().includes(search.toLowerCase());
    const phoneMatch = u.phone && u.phone.toLowerCase().includes(search.toLowerCase());
    return nameMatch || phoneMatch;
      });
    }
    
    renderUsers(filteredUsers);
    updatePagination('users', users.length);
  } catch (error) {
    const errorMessage = error.message || 'Неизвестная ошибка';
    
    // Если ошибка авторизации, пробуем восстановить токен
    if (errorMessage.includes('авторизац') || errorMessage.includes('401') || errorMessage.includes('Требуется')) {
      // Согласно rules.md: токены не хранятся в localStorage
      const savedToken = apiClient.getAccessToken();
      if (savedToken && savedToken.trim()) {
        console.log('🔄 Токен восстановлен, повторяем запрос...');
        // Повторяем запрос
        setTimeout(() => loadUsers(), 500);
        return;
      } else {
        showAdminError('Требуется авторизация. Пожалуйста, войдите заново.');
        showAdminLogin();
        return;
      }
    }
    
    // Для ошибок БД просто показываем пустую таблицу
    if (errorMessage.includes('500') || errorMessage.includes('503') || errorMessage.includes('недоступн')) {
      console.warn('⚠️ База данных недоступна. Показываем пустую таблицу.');
      renderUsers([]);
      return;
    }
    
    // Для других ошибок показываем сообщение
    showAdminError('Ошибка загрузки пользователей: ' + errorMessage);
    console.error('Ошибка загрузки пользователей:', error);
  }
}

// Рендеринг пользователей
function renderUsers(users) {
  const tbody = document.getElementById('users-tbody');
  if (!users || users.length === 0) {
    tbody.innerHTML = '<tr><td colspan="10" class="empty">Нет данных</td></tr>';
    return;
  }
  
  tbody.innerHTML = users.map(user => {
    const phone = user.phone ? escapeHtml(user.phone) : '-';
    const email = user.email ? escapeHtml(user.email) : '-';
    const parentId = user.parent_id ? user.parent_id : '-';
    const updatedAt = user.updated_at ? formatDate(user.updated_at) : '-';
    return `
    <tr>
      <td><strong>${user.id}</strong></td>
      <td><strong>${phone}</strong></td>
      <td>${email}</td>
      <td><span class="badge badge-${user.role}">${getRoleLabel(user.role)}</span></td>
      <td>${parentId}</td>
      <td>${user.children_count || 0}</td>
      <td>${user.subscriptions_count || 0}</td>
      <td>${formatDate(user.created_at)}</td>
      <td>${updatedAt}</td>
      <td>
        <button class="admin-action-btn" onclick="editUser(${user.id}, ${JSON.stringify(user.phone || '')}, ${JSON.stringify(user.email || '')}, ${JSON.stringify(user.role)}, ${user.parent_id || 'null'})">✏️</button>
        <button class="admin-action-btn danger" onclick="deleteUser(${user.id}, ${JSON.stringify(user.phone || user.email || 'пользователь')})">🗑️</button>
      </td>
    </tr>
    `;
  }).join('');
}

// Загрузка детей
async function loadChildren() {
  try {
    showLoading('children-tbody');
    
    const skip = adminState.childrenPage * adminState.pageSize;
    const children = await apiClient.getAdminChildren(skip, adminState.pageSize);
    
    renderChildren(children);
    updatePagination('children', children.length);
  } catch (error) {
    const errorMessage = error.message || 'Неизвестная ошибка';
    
    // Для ошибок БД просто показываем пустую таблицу
    if (errorMessage.includes('500') || errorMessage.includes('503') || errorMessage.includes('недоступн')) {
      console.warn('⚠️ База данных недоступна. Показываем пустую таблицу.');
      renderChildren([]);
      return;
    }
    
    showAdminError('Ошибка загрузки детей: ' + errorMessage);
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
    
    const subscriptions = await apiClient.getAdminSubscriptions(skip, adminState.pageSize, activeOnly);
    
    renderSubscriptions(subscriptions);
    updatePagination('subscriptions', subscriptions.length);
  } catch (error) {
    const errorMessage = error.message || 'Неизвестная ошибка';
    
    // Для ошибок БД просто показываем пустую таблицу
    if (errorMessage.includes('500') || errorMessage.includes('503') || errorMessage.includes('недоступн')) {
      console.warn('⚠️ База данных недоступна. Показываем пустую таблицу.');
      renderSubscriptions([]);
      return;
    }
    
    showAdminError('Ошибка загрузки подписок: ' + errorMessage);
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
    
    const notifications = await apiClient.getAdminNotifications(skip, adminState.pageSize, type);
    
    renderNotifications(notifications);
    updatePagination('notifications', notifications.length);
  } catch (error) {
    const errorMessage = error.message || 'Неизвестная ошибка';
    
    // Для ошибок БД просто показываем пустую таблицу
    if (errorMessage.includes('500') || errorMessage.includes('503') || errorMessage.includes('недоступн')) {
      console.warn('⚠️ База данных недоступна. Показываем пустую таблицу.');
      renderNotifications([]);
      return;
    }
    
    showAdminError('Ошибка загрузки уведомлений: ' + errorMessage);
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
function editUser(id, name, phone, role, parentId) {
  document.getElementById('edit-user-id').value = id;
  document.getElementById('edit-user-name').value = name || '';
  document.getElementById('edit-user-phone').value = phone || '';
  document.getElementById('edit-user-role').value = role;
  const parentIdInput = document.getElementById('edit-user-parent-id');
  if (parentIdInput) {
    parentIdInput.value = parentId && parentId !== 'null' ? parentId : '';
  }
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
  const name = document.getElementById('edit-user-name').value.trim();
  const phone = document.getElementById('edit-user-phone').value.trim();
  const role = document.getElementById('edit-user-role').value;
  const parentIdInput = document.getElementById('edit-user-parent-id');
  const parentIdValue = parentIdInput ? parentIdInput.value.trim() : '';
  const parentId = parentIdValue ? parseInt(parentIdValue) : null;
  
  const updateData = { role };
  if (name) updateData.name = name;
  else updateData.name = null;
  
  if (phone) updateData.phone = phone;
  else updateData.phone = null;
  
  if (parentId !== null) {
    updateData.parent_id = parentId;
  } else if (role === 'parent') {
    // Убираем parent_id для родителей
    updateData.parent_id = null;
  }
  
  try {
    await apiClient.updateAdminUser(id, updateData);
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
    await apiClient.deleteAdminUser(id);
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
      // Согласно rules.md: токены не хранятся в localStorage
      apiClient.setAccessToken(null);
  adminState.currentUser = null;
  
  // Скрываем админку
  const adminHeader = document.querySelector('.admin-header');
  const adminNav = document.querySelector('.admin-nav');
  const adminMain = document.querySelector('.admin-main');
  if (adminHeader) adminHeader.style.display = 'none';
  if (adminNav) adminNav.style.display = 'none';
  if (adminMain) adminMain.style.display = 'none';
  
  // Редиректим на главную или показываем форму входа
  if (window.router) {
    window.router.navigate('/');
  } else {
    showAdminLogin();
  }
}

// Утилиты
function showLoading(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (tbody) {
    // Определяем количество колонок в зависимости от таблицы
    let colspan = 10; // По умолчанию для users и recent-users
    if (tbodyId.includes('subscriptions')) {
      colspan = 6; // Для subscriptions
    } else if (tbodyId.includes('children')) {
      colspan = 7; // Для children
    } else if (tbodyId.includes('notifications')) {
      colspan = 6; // Для notifications
    }
    tbody.innerHTML = `<tr><td colspan="${colspan}" class="loading">Загрузка...</td></tr>`;
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

