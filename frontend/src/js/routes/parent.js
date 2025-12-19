/**
 * Маршрут /parent
 * Панель родителя
 */
async function handleParentRoute() {
  console.log('👨‍👩‍👧 Загрузка панели родителя...');
  
  // Показываем контент родителя
  const parentContent = document.getElementById('parent-content');
  const mainContent = document.getElementById('app-content');
  const adminContent = document.getElementById('admin-content');
  
  if (parentContent) {
    parentContent.style.display = 'block';
  }
  if (mainContent) {
    mainContent.style.display = 'none';
  }
  if (adminContent) {
    adminContent.style.display = 'none';
  }
  
  // Загружаем скрипт родителя если еще не загружен
  if (typeof initParentDashboard === 'undefined') {
    const script = document.createElement('script');
    script.src = '/src/js/parent.js';
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
}

window.handleParentRoute = handleParentRoute;



