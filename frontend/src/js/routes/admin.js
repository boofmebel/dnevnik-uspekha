/**
 * Маршрут /admin
 * Админ-панель
 */
async function handleAdminRoute() {
  console.log('🔐 Загрузка админ-панели...');
  
  // Показываем админку
  const adminContent = document.getElementById('admin-content');
  const mainContent = document.getElementById('app-content');
  const parentContent = document.getElementById('parent-content');
  const childContent = document.getElementById('child-content');
  
  if (adminContent) {
    adminContent.style.display = 'block';
  }
  if (mainContent) {
    mainContent.style.display = 'none';
  }
  if (parentContent) {
    parentContent.style.display = 'none';
  }
  if (childContent) {
    childContent.style.display = 'none';
  }
  
  // Инициализируем админку (admin.js должен быть уже загружен в index.html)
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
}

window.handleAdminRoute = handleAdminRoute;

