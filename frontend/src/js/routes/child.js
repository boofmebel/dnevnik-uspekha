/**
 * Маршрут /child
 * Интерфейс ребенка
 */
async function handleChildRoute() {
  console.log('👧 Загрузка интерфейса ребенка...');
  
  // Показываем контент ребенка
  const childContent = document.getElementById('child-content');
  const mainContent = document.getElementById('app-content');
  const parentContent = document.getElementById('parent-content');
  const adminContent = document.getElementById('admin-content');
  
  if (childContent) {
    childContent.style.display = 'block';
  }
  if (mainContent) {
    mainContent.style.display = 'none';
  }
  if (parentContent) {
    parentContent.style.display = 'none';
  }
  if (adminContent) {
    adminContent.style.display = 'none';
  }
  
  // Загружаем скрипт ребенка если еще не загружен
  if (typeof initChildApp === 'undefined') {
    const script = document.createElement('script');
    script.src = '/src/js/child.js';
    document.body.appendChild(script);
    // Ждем загрузки скрипта
    await new Promise((resolve) => {
      script.onload = resolve;
    });
  }
  
  // Инициализируем приложение ребенка
  if (typeof initChildApp === 'function') {
    await initChildApp();
  }
}

window.handleChildRoute = handleChildRoute;



