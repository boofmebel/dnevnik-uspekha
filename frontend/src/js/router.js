/**
 * Клиентский роутер для SPA
 * Обрабатывает маршруты: /admin, /parent, /child, /
 * 
 * ⚠️ ОГРАНИЧЕНИЕ: Роутер плоский, вложенные маршруты не поддерживаются
 * Например: /admin/users/123 - не поддерживается
 * Используйте query параметры: /admin?user=123
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

    // Обработка начального маршрута
    this.handleRoute();
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
        this.navigate('/');
      }
    } else {
      // Маршрут не найден - редирект на главную
      console.warn('Маршрут не найден:', fullPath);
      this.navigate('/');
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



