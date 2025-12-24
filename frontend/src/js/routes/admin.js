/**
 * Маршрут /admin
 * Админ-панель
 * 
 * Защита: проверяет роль через /api/auth/me перед показом UI
 */
async function handleAdminRoute() {
  console.log('🔐 Загрузка админ-панели...');
  
  // СНАЧАЛА ПРИНУДИТЕЛЬНО СКРЫВАЕМ АДМИНКУ - показываем только после авторизации!
  const adminHeader = document.querySelector('.admin-header');
  const adminNav = document.querySelector('.admin-nav');
  const adminMain = document.querySelector('.admin-main');
  if (adminHeader) adminHeader.style.display = 'none';
  if (adminNav) adminNav.style.display = 'none';
  if (adminMain) adminMain.style.display = 'none';
  
  // Показываем контейнер admin-content (но админка внутри будет скрыта до авторизации)
  const adminContent = document.getElementById('admin-content');
  const mainContent = document.getElementById('app-content');
  const parentContent = document.getElementById('parent-content');
  const childContent = document.getElementById('child-content');
  
  // Скрываем другие контейнеры
  if (mainContent) {
    mainContent.style.display = 'none';
  }
  if (parentContent) {
    parentContent.style.display = 'none';
  }
  if (childContent) {
    childContent.style.display = 'none';
  }
  
  // Показываем admin-content (внутри него initAdminPanel решит, что показывать)
  if (adminContent) {
    adminContent.style.display = 'block';
  }
  
  // ЗАЩИТА МАРШРУТА: проверяем роль через /api/auth/me
  const token = apiClient.getAccessToken();
  if (!token) {
    // Нет токена - показываем форму входа
    if (typeof showAdminLogin === 'function') {
      showAdminLogin();
    }
    return;
  }
  
  try {
    const me = await apiClient.get('/auth/me');
    
    // Проверка роли
    if (me.role !== 'admin') {
      console.warn('⚠️ Доступ запрещён: роль не admin, редирект на /');
      router.navigate('/', true);
      return;
    }
    
    // Роль admin подтверждена - инициализируем админку
    if (typeof initAdminPanel === 'function') {
      await initAdminPanel();
    } else {
      console.error('❌ Функция initAdminPanel не найдена. Убедитесь, что admin.js загружен.');
      const loadingEl = document.getElementById('admin-loading');
      if (loadingEl) {
        loadingEl.style.display = 'none';
      }
      if (typeof showAdminLogin === 'function') {
        showAdminLogin();
      } else {
        console.error('❌ Функция showAdminLogin также не найдена');
      }
    }
  } catch (e) {
    // 401 или другая ошибка - пробуем обновить токен
    const refreshed = await apiClient.refreshToken();
    if (refreshed) {
      apiClient.setAccessToken(refreshed);
      // Повторяем проверку
      return handleAdminRoute();
    }
    // Если не удалось обновить - показываем форму входа
    console.error('❌ Ошибка проверки авторизации:', e);
    if (typeof showAdminLogin === 'function') {
      showAdminLogin();
    }
  }
}

window.handleAdminRoute = handleAdminRoute;

