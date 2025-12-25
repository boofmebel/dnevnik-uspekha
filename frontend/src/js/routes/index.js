/**
 * Bootstrap авторизации
 * Единая точка входа для проверки авторизации и роутинга по ролям
 * 
 * Безопасность: используем /api/auth/me вместо декодирования JWT на клиенте
 */
async function bootstrapAuth() {
  let token = apiClient.getAccessToken();
  console.log('🔍 bootstrapAuth: токен есть?', !!token);

  // Если токена нет в памяти, пробуем восстановить из refresh token
  if (!token) {
    console.log('⚠️ bootstrapAuth: токен отсутствует в памяти, пробую восстановить из refresh token...');
    try {
      const refreshed = await apiClient.refreshToken();
      if (refreshed) {
        console.log('✅ bootstrapAuth: токен восстановлен из refresh token');
        token = refreshed;
        apiClient.setAccessToken(refreshed);
      } else {
        console.log('⚠️ bootstrapAuth: не удалось восстановить токен, показываю форму входа');
        if (typeof showAuthModal === 'function') {
          showAuthModal();
        } else {
          // Fallback: показываем форму входа напрямую
          const authModal = document.getElementById('auth-modal');
          if (authModal) {
            authModal.style.display = 'flex';
          }
        }
        return;
      }
    } catch (error) {
      console.error('❌ bootstrapAuth: ошибка при восстановлении токена:', error);
      // Если не удалось восстановить - показываем форму входа
      if (typeof showAuthModal === 'function') {
        showAuthModal();
      } else {
        const authModal = document.getElementById('auth-modal');
        if (authModal) {
          authModal.style.display = 'flex';
        }
      }
      return;
    }
  }

  try {
    console.log('📤 bootstrapAuth: запрашиваю /api/auth/me...');
    const me = await apiClient.get('/auth/me');
    console.log('✅ bootstrapAuth: /api/auth/me вернул:', me);

    // Не делаем редирект, если мы уже на правильной странице после входа по QR-коду
    const currentPath = window.location.pathname;
    if (currentPath === '/child' && me.role === 'child') {
      console.log('✅ bootstrapAuth: уже на странице ребенка, редирект не нужен');
      return; // Не делаем редирект, продолжаем загрузку страницы
    }

    // Редирект по роли из backend
    if (me.role === 'parent') {
      console.log('🔄 bootstrapAuth: редирект на /parent');
      router.navigate('/parent', true);
    } else if (me.role === 'child') {
      console.log('🔄 bootstrapAuth: редирект на /child');
      router.navigate('/child', true);
    } else if (me.role === 'admin' || me.role === 'support' || me.role === 'moderator') {
      // Staff роли - редирект на staff панель
      console.log('🔄 bootstrapAuth: редирект на /staff/dashboard');
      window.location.href = '/staff/dashboard';
      return;
    } else {
      // Неизвестная роль - выход
      console.warn('⚠️ bootstrapAuth: неизвестная роль:', me.role);
      await apiClient.logout();
      if (typeof showAuthModal === 'function') {
        showAuthModal();
      }
    }
  } catch (e) {
    console.error('❌ bootstrapAuth: ошибка при проверке /api/auth/me:', e);
    // Пробуем обновить токен
    console.log('🔄 bootstrapAuth: пробую обновить токен...');
    const refreshed = await apiClient.refreshToken();
    if (refreshed) {
      console.log('✅ bootstrapAuth: токен обновлён, повторяю проверку');
      apiClient.setAccessToken(refreshed);
      return bootstrapAuth();
    }
    // Если не удалось обновить - выход
    console.error('❌ bootstrapAuth: не удалось обновить токен, показываю форму входа');
    await apiClient.logout();
    if (typeof showAuthModal === 'function') {
      showAuthModal();
    }
  }
}

/**
 * Маршрут / (главная)
 * Использует bootstrapAuth() для определения роли и редиректа
 */
async function handleRootRoute() {
  console.log('🏠 Обработка главного маршрута...');
  await bootstrapAuth();
}

window.handleRootRoute = handleRootRoute;
window.bootstrapAuth = bootstrapAuth;



