/**
 * Маршрут /parent
 * Панель родителя
 * 
 * Защита: проверяет роль через /api/auth/me перед показом UI
 */
async function handleParentRoute() {
  console.log('👨‍👩‍👧 Загрузка панели родителя...');
  
  // ЗАЩИТА МАРШРУТА: проверяем роль через /api/auth/me
  const token = apiClient.getAccessToken();
  if (!token) {
    // Нет токена - редирект на главную
    router.navigate('/', true);
    return;
  }
  
  try {
    const me = await apiClient.get('/auth/me');
    
    // Проверка роли
    if (me.role !== 'parent') {
      console.warn('⚠️ Доступ запрещён: роль не parent, редирект на /');
      router.navigate('/', true);
      return;
    }
    
    // Роль parent подтверждена - показываем контент родителя
    const parentContent = document.getElementById('parent-content');
    const mainContent = document.getElementById('app-content');
    const adminContent = document.getElementById('admin-content');
    const authModal = document.getElementById('auth-modal');
    
    // Скрываем форму входа и другие контенты
    if (authModal) {
      authModal.style.display = 'none';
      console.log('✅ handleParentRoute: форма входа скрыта');
    }
    // Показываем app-content для родителя (там находится весь контент)
    if (mainContent) {
      mainContent.style.display = 'block';
      console.log('✅ handleParentRoute: контент родителя показан');
    }
    if (parentContent) {
      parentContent.style.display = 'none';
    }
    if (adminContent) {
      adminContent.style.display = 'none';
    }
    
    // Загружаем скрипты родителя если еще не загружены
    if (typeof initParentDashboard === 'undefined') {
      const script = document.createElement('script');
      script.src = '/src/js/parent.js';
      document.body.appendChild(script);
      // Ждем загрузки скрипта
      await new Promise((resolve) => {
        script.onload = resolve;
      });
    }
    
    // Загружаем скрипт модального окна управления детьми
    // Проверяем, не загружен ли уже скрипт
    if (typeof initChildrenModal === 'undefined' && !document.querySelector('script[src*="children-modal.js"]')) {
      const script = document.createElement('script');
      script.src = '/src/js/children-modal.js?v=' + Date.now();
      document.body.appendChild(script);
      // Ждем загрузки скрипта
      await new Promise((resolve) => {
        script.onload = resolve;
      });
    }
    
    // Инициализируем панель родителя
    if (typeof initParentDashboard === 'function') {
      await initParentDashboard();
    }
    
    // Инициализируем модальное окно управления детьми
    if (typeof initChildrenModal === 'function') {
      await initChildrenModal();
    }
    
    // Проверяем, есть ли дети. Если нет - показываем форму создания
    try {
      const children = await apiClient.getChildren();
      if (children.length === 0) {
        console.log('👶 Детей нет, показываем форму создания первого ребенка');
        // Показываем модальное окно добавления ребенка
        if (typeof openAddChildModal === 'function') {
          setTimeout(() => openAddChildModal(), 500);
        }
      } else {
        // Если есть дети, выбираем первого по умолчанию
        if (typeof window.switchToChild === 'function') {
          await window.switchToChild(children[0].id);
        }
      }
    } catch (error) {
      console.error('❌ Ошибка проверки детей:', error);
    }
  } catch (e) {
    // 401 или другая ошибка - пробуем обновить токен
    const refreshed = await apiClient.refreshToken();
    if (refreshed) {
      apiClient.setAccessToken(refreshed);
      // Повторяем проверку
      return handleParentRoute();
    }
    // Если не удалось обновить - редирект на главную
    console.error('❌ Ошибка проверки авторизации:', e);
    router.navigate('/', true);
  }
}

window.handleParentRoute = handleParentRoute;



