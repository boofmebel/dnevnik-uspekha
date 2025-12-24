/**
 * Клиентский роутер для SPA
 * Обрабатывает маршруты: /parent, /child, /
 * 
 * ⚠️ ОГРАНИЧЕНИЕ: Роутер плоский, вложенные маршруты не поддерживаются
 * Например: /parent/children/123 - не поддерживается
 * Используйте query параметры: /parent?child=123
 * 
 * ⚠️ /admin больше не поддерживается в product SPA
 * Админы должны использовать /staff/login
 */
class Router {
  constructor() {
    this.routes = {};
    this.currentRoute = null;
    this.currentParams = {};
    this.init();
  }

  init() {
    // Обработка изменения URL
    window.addEventListener('popstate', () => {
      this.handleRoute();
    });

    // Обработка кликов по ссылкам
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[data-route]');
      if (link) {
        e.preventDefault();
        const route = link.getAttribute('data-route');
        this.navigate(route);
      }
    });

    // НЕ обрабатываем начальный маршрут здесь - это будет сделано
    // после регистрации всех маршрутов в index.html
    // this.handleRoute();
  }

  /**
   * Регистрация маршрута
   */
  route(path, handler) {
    this.routes[path] = handler;
  }

  /**
   * Навигация по маршруту
   */
  navigate(path, replace = false) {
    if (replace) {
      window.history.replaceState({}, '', path);
    } else {
      window.history.pushState({}, '', path);
    }
    this.handleRoute();
  }

  /**
   * Обработка текущего маршрута
   */
  async handleRoute() {
    const path = window.location.pathname;
    const [route, ...params] = path.split('/').filter(Boolean);
    
    // Определяем полный путь
    const fullPath = '/' + (route || '');
    const normalizedPath = route || 'root';

    console.log('📍 Текущий маршрут:', fullPath, 'params:', params);

    // Ищем обработчик маршрута
    let handler = this.routes[fullPath] || this.routes[normalizedPath];

    if (handler) {
      try {
        // Вызываем обработчик
        await handler(params);
        this.currentRoute = fullPath;
        this.currentParams = params;
      } catch (error) {
        console.error('Ошибка обработки маршрута:', error);
        // НЕ редиректим на / если это /admin - показываем ошибку
        if (fullPath === '/admin') {
          console.error('Ошибка загрузки админки, но остаёмся на /admin');
        } else {
          this.navigate('/');
        }
      }
    } else {
      // Маршрут не найден
      if (fullPath === '/admin') {
        // /admin больше не поддерживается в product SPA
        console.warn('⚠️ /admin больше не поддерживается. Используйте /staff/login для staff пользователей.');
        alert('Админ-панель перемещена. Пожалуйста, используйте /staff/login для входа в staff панель.');
        this.navigate('/');
      } else if (fullPath.startsWith('/staff')) {
        // Staff маршруты обрабатываются отдельно
        console.warn('⚠️ Staff маршруты должны обрабатываться через staff.html или отдельный SPA');
        // Редирект на staff.html для /staff/login
        if (fullPath === '/staff/login') {
          window.location.href = '/staff.html';
        } else {
          this.navigate('/staff/login');
        }
      } else {
        console.warn('Маршрут не найден:', fullPath);
        this.navigate('/');
      }
    }
  }

  /**
   * Получить текущий маршрут
   */
  getCurrentRoute() {
    return this.currentRoute || window.location.pathname;
  }

  /**
   * Получить параметры маршрута
   */
  getParams() {
    return this.currentParams;
  }
}

// Создаём глобальный экземпляр роутера
const router = new Router();

// Экспорт
window.router = router;



